"""
A key/value editor for a model's `JSONField`: `PropertiesField` + `PropertiesWidget`.

The field holds a *schema*: a dict mapping each known key to an ordinary
`django.forms` field (`DecimalField`, `DateField`, `ChoiceField`, ...). Each of
those fields renders its own widget on its own row and cleans its own value,
so a property validates exactly like a top-level form field would - same
widgets, same error messages, same `min_value`/`max_length`/`validators`.
Free-form rows (keys the schema doesn't name) are opt-in with
`allow_extra=True`; their keys are cleaned by `key_field` and their values by
`extra_field`, both ordinary form fields too.

`cleaned_data[name]` is a plain dict of JSON-native values, ready for a
`models.JSONField`. See docs/properties-widget.md.
"""
import copy
import json
import re

from django import forms
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms.utils import pretty_name
from django.utils.translation import gettext_lazy as _

PREFIX_PLACEHOLDER = '__prefix__'


class PropertyRow:
    """One row of the editor, as both the field and the widget see it."""

    __slots__ = ('key', 'value', 'index', 'fixed')

    def __init__(self, key, value, index, fixed):
        self.key = key          # the key (raw text for a free row)
        self.value = value      # the raw posted value, or the stored JSON value
        self.index = index      # schema position for a fixed row, posted index for a free one
        self.fixed = fixed      # True for a schema row, False for a free-form row

    @property
    def row_id(self):
        return f's{self.index}' if self.fixed else f'x{self.index}'

    def __repr__(self):
        return f'PropertyRow({self.key!r}, {self.value!r}, {self.row_id})'


class JSONValueField(forms.CharField):
    """
    The default value field for free-form rows: text that reads as JSON other
    than a bare string is stored as that JSON (`42`, `1.5`, `true`, `null`,
    `[1, 2]`, `{"a": 1}`); anything else is stored as the text itself
    (`FR`, `01234`, `hello world`). Quote a value to force a string (`"42"`).

    It round-trips: a stored string that would otherwise read back as a number
    or a boolean is shown quoted, and a stored list or object is shown as JSON,
    so saving a record without touching a row never changes its type.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('required', False)
        super().__init__(**kwargs)

    def to_python(self, value):
        if value is not None and not isinstance(value, str):
            return value  # already JSON data (a stored value, not posted text)
        text = super().to_python(value)
        if text in self.empty_values:
            return self.empty_value
        try:
            return json.loads(text, parse_constant=_reject_constant)
        except ValueError:
            return text

    def bound_data(self, data, initial):
        if self.disabled:
            return initial
        return self.to_python(data)

    def prepare_value(self, value):
        if isinstance(value, str):
            try:
                json.loads(value, parse_constant=_reject_constant)
            except ValueError:
                return value
            return json.dumps(value)
        if value is None:
            return 'null'
        return json.dumps(value, cls=DjangoJSONEncoder)


class PropertiesWidget(forms.Widget):
    """
    Renders a `PropertiesField` as a Property | Value table in a table card,
    one row per property.

    Schema rows show the key as a label and the value as the schema field's own
    widget. Free-form rows (`allow_extra=True`) show a key input, a value input
    (the `extra_field`'s widget) and a remove button; "Add property", in the
    card footer, clones a blank one from a `<template>`. Everything posts as
    ordinary form inputs:

        <name>                  presence marker (always posted, empty)
        <name>__s<i>            value of the i-th schema key
        <name>__x<n>__key       key of free row n
        <name>__x<n>__value     value of free row n

    The field sets `schema`, `allow_extra`, `extra_field`, `key_field` and
    `max_extra` on its widget, the same way `ChoiceField` hands its choices to
    a `Select`, so you rarely build one of these yourself.
    """

    template_name = 'wise_core/widgets/properties.html'
    add_label = _('Add property')
    empty_label = _('No properties yet.')
    key_header = _('Property')
    value_header = _('Value')
    key_placeholder = _('Key')
    value_placeholder = _('Value')

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.schema = {}
        self.allow_extra = False
        self.extra_field = JSONValueField()
        self.key_field = forms.CharField(max_length=100)
        self.max_extra = None
        # Filled in by PropertiesField.clean() on a bound form, so the rows
        # that failed can be marked invalid when the form re-renders.
        self.row_errors = {}

    def __deepcopy__(self, memo):
        obj = super().__deepcopy__(memo)
        obj.row_errors = {}
        return obj

    # ── Reading the POST ──────────────────────────────────────────────────

    def value_from_datadict(self, data, files, name):
        rows = []
        for i, (key, field) in enumerate(self.schema.items()):
            raw = field.widget.value_from_datadict(data, files, f'{name}__s{i}')
            rows.append(PropertyRow(key, raw, i, fixed=True))
        if self.allow_extra:
            pattern = re.compile(rf'^{re.escape(name)}__x(\d+)__key$')
            indexes = sorted({int(m.group(1)) for k in data if (m := pattern.match(k))})
            for n in indexes:
                key = data.get(f'{name}__x{n}__key', '')
                raw = self.extra_field.widget.value_from_datadict(data, files, f'{name}__x{n}__value')
                rows.append(PropertyRow(key, raw, n, fixed=False))
        return rows

    def value_omitted_from_data(self, data, files, name):
        # The hidden marker input is always rendered, so its absence means the
        # widget wasn't on the page at all (e.g. a partial update form).
        return name not in data

    def id_for_label(self, id_):
        if id_ and self.schema:
            return f'{id_}__s0'
        return id_

    # ── Rendering ─────────────────────────────────────────────────────────

    def to_rows(self, value):
        """Normalize whatever the form hands the widget into a list of rows."""
        if isinstance(value, list) and all(isinstance(r, PropertyRow) for r in value):
            return value, True
        data = _load_json_dict(value)
        rows = [PropertyRow(key, data.get(key), i, fixed=True) for i, key in enumerate(self.schema)]
        if self.allow_extra:
            extra = [key for key in data if key not in self.schema]
            rows += [PropertyRow(key, data[key], n, fixed=False) for n, key in enumerate(extra)]
        return rows, False

    def format_value(self, value):
        return value

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        widget = context['widget']
        attrs = widget['attrs']
        base_id = attrs.get('id') or f'id_{name}'
        disabled = bool(attrs.get('disabled'))
        rows, bound = self.to_rows(value)
        rendered = []
        next_index = 0
        for row in rows:
            if row.fixed:
                rendered.append(self._render_fixed(name, base_id, row, bound, disabled))
            else:
                rendered.append(self._render_extra(name, base_id, row, bound, disabled))
                next_index = max(next_index, row.index + 1)
        template_row = None
        if self.allow_extra and not disabled:
            blank = PropertyRow('', '', PREFIX_PLACEHOLDER, fixed=False)
            template_row = self._render_extra(name, base_id, blank, False, False)
        widget.update({
            'base_id': base_id,
            'rows': rendered,
            'template_row': template_row,
            'allow_extra': self.allow_extra,
            'disabled': disabled,
            'next_index': next_index,
            'max_extra': self.max_extra,
            'extra_count': sum(1 for r in rows if not r.fixed),
            'has_actions': self.allow_extra and not disabled,
            'add_label': self.add_label,
            'empty_label': self.empty_label,
            'key_header': self.key_header,
            'value_header': self.value_header,
        })
        # The container is a <div>: the per-row inputs carry their own names,
        # so the outer `required`/`maxlength`/... attrs have nowhere to go.
        widget['attrs'] = {k: v for k, v in attrs.items() if k in ('id', 'class')}
        return context

    def _sub_attrs(self, sub_id, invalid, disabled, extra=None):
        attrs = {'id': sub_id, **(extra or {})}
        if invalid:
            attrs['aria-invalid'] = 'true'
        if disabled:
            attrs['disabled'] = True
        return attrs

    def _render_fixed(self, name, base_id, row, bound, disabled):
        field = self.schema[row.key]
        sub_name, sub_id = f'{name}__s{row.index}', f'{base_id}__s{row.index}'
        value = field.bound_data(row.value, None) if bound else row.value
        value = field.prepare_value(value)
        errors = self.row_errors.get(row.row_id, {})
        attrs = self._sub_attrs(sub_id, errors.get('value'), disabled or field.disabled)
        if field.required and field.widget.use_required_attribute(value) and not disabled:
            attrs['required'] = True
        return {
            'fixed': True,
            'key': row.key,
            'label': field.label if field.label is not None else pretty_name(str(row.key)),
            'required': field.required,
            'help_text': field.help_text,
            'value_id': sub_id,
            'value_html': field.widget.render(sub_name, value, attrs),
            'is_checkbox': getattr(field.widget, 'input_type', None) == 'checkbox',
            'invalid': bool(errors),
        }

    def _render_extra(self, name, base_id, row, bound, disabled):
        prefix = f'x{row.index}'
        key_name, key_id = f'{name}__{prefix}__key', f'{base_id}__{prefix}__key'
        value_name, value_id = f'{name}__{prefix}__value', f'{base_id}__{prefix}__value'
        errors = self.row_errors.get(row.row_id, {})
        if bound:
            value = self.extra_field.bound_data(row.value, None)
        elif isinstance(row.value, (dict, list)) and not isinstance(self.extra_field, (forms.JSONField, JSONValueField)):
            # A nested value under a free key shown in a plain text input:
            # show it as JSON rather than Python's repr.
            value = json.dumps(row.value, cls=DjangoJSONEncoder)
        else:
            value = row.value
        value = self.extra_field.prepare_value(value)
        key_attrs = self._sub_attrs(key_id, errors.get('key'), disabled, {
            'class': 'input property-key-input',
            'placeholder': self.key_placeholder,
            'aria-label': self.key_placeholder,
            'autocomplete': 'off',
            'data-property-key': '',
        })
        value_attrs = self._sub_attrs(value_id, errors.get('value'), disabled, {
            'placeholder': self.value_placeholder,
            'aria-label': self.value_placeholder,
        })
        return {
            'fixed': False,
            'key': row.key,
            'key_html': self.key_field.widget.render(key_name, self.key_field.prepare_value(row.key), key_attrs),
            'value_id': value_id,
            'value_html': self.extra_field.widget.render(value_name, value, value_attrs),
            'is_checkbox': getattr(self.extra_field.widget, 'input_type', None) == 'checkbox',
            'invalid': bool(errors),
        }


class PropertiesField(forms.Field):
    """
    A form field for a `models.JSONField` holding a flat `{key: value}` object.

        specs = PropertiesField(
            schema={
                'weight': forms.DecimalField(min_value=0, label='Weight (kg)'),
                'color': forms.ChoiceField(choices=COLORS),
                'released': forms.DateField(required=False),
            },
            allow_extra=True,
        )

    schema       {key: forms.Field}. Each key gets a row rendered by that
                 field's widget and validated by that field's clean().
    allow_extra  Allow keys outside the schema (add/remove rows). With False,
                 stored keys the schema doesn't name are dropped on save.
    extra_field  Cleans free-form values (default `JSONValueField()`: JSON
                 literals are typed, other text is a string; pass
                 `forms.CharField(required=False)` to store strings only).
    key_field    Cleans free-form keys (default `CharField(max_length=100)`;
                 `forms.SlugField()` keeps them identifier-like).
    max_extra    Cap on the number of free-form rows.
    drop_empty   Omit a key whose cleaned value is empty ('' / None / [] / {})
                 instead of storing it (default True).
    encoder      JSON encoder for the cleaned values (default
                 `DjangoJSONEncoder`: dates and times become ISO strings,
                 Decimal and UUID become strings).
    """

    widget = PropertiesWidget
    default_error_messages = {
        'required': _('Add at least one property.'),
        'invalid_json': _('Enter a valid JSON object.'),
        'missing_key': _('Enter a key for the value “%(value)s”.'),
        'duplicate_key': _('The key “%(key)s” is used more than once.'),
        'too_many': _('Add at most %(max)d custom properties.'),
        'property': '%(label)s: %(message)s',
    }

    def __init__(self, *, schema=None, allow_extra=False, extra_field=None, key_field=None,
                 max_extra=None, drop_empty=True, encoder=None, **kwargs):
        self.schema = dict(schema or {})
        for key, field in self.schema.items():
            if not isinstance(field, forms.Field):
                raise ImproperlyConfigured(f'PropertiesField schema[{key!r}] must be a django.forms.Field instance.')
            if isinstance(field, forms.FileField):
                raise ImproperlyConfigured(f'PropertiesField schema[{key!r}]: a file cannot be stored in a JSONField.')
        self.allow_extra = allow_extra
        self.extra_field = extra_field or JSONValueField()
        self.key_field = key_field or forms.CharField(max_length=100)
        self.max_extra = max_extra
        self.drop_empty = drop_empty
        self.encoder = encoder or DjangoJSONEncoder
        kwargs.setdefault('required', False)
        super().__init__(**kwargs)
        self._configure_widget()

    def _configure_widget(self):
        self.widget.schema = self.schema
        self.widget.allow_extra = self.allow_extra
        self.widget.extra_field = self.extra_field
        self.widget.key_field = self.key_field
        self.widget.max_extra = self.max_extra

    def __deepcopy__(self, memo):
        result = super().__deepcopy__(memo)
        result.schema = copy.deepcopy(self.schema, memo)
        result.extra_field = copy.deepcopy(self.extra_field, memo)
        result.key_field = copy.deepcopy(self.key_field, memo)
        result._configure_widget()
        return result

    # ── Value plumbing ────────────────────────────────────────────────────

    def prepare_value(self, value):
        return value

    def bound_data(self, data, initial):
        if self.disabled:
            return initial
        return data

    def to_python(self, value):
        """Turn the widget's rows (or a stored dict / JSON string) into rows."""
        if isinstance(value, list) and all(isinstance(r, PropertyRow) for r in value):
            return value
        try:
            data = _load_json_dict(value, strict=True)
        except ValueError:
            raise ValidationError(self.error_messages['invalid_json'], code='invalid_json')
        return self.widget.to_rows(data)[0]

    def clean(self, value):
        cleaned, errors, row_errors = self._clean_rows(self.to_python(value))
        self.widget.row_errors = row_errors
        if errors:
            raise ValidationError(errors)
        self.validate(cleaned)
        self.run_validators(cleaned)
        return cleaned

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'], code='required')

    def has_changed(self, initial, data):
        if self.disabled:
            return False
        try:
            cleaned, errors, _row_errors = self._clean_rows(self.to_python(data))
            initial = _load_json_dict(initial, strict=True)
        except (ValidationError, ValueError):
            return True
        if errors:
            return True
        dump = lambda v: json.dumps(v, sort_keys=True, cls=self.encoder)  # noqa: E731
        return dump(cleaned) != dump(initial)

    # ── Validation ────────────────────────────────────────────────────────

    def _clean_rows(self, rows):
        """
        Clean every row with its own form field. Returns (dict, errors,
        row_errors): `errors` is a list of ValidationErrors with the property's
        label prefixed, `row_errors` maps a row id to {'key': bool, 'value':
        bool} for the widget.
        """
        result, errors, row_errors = {}, [], {}
        seen = set()
        extra_count = 0

        def fail(row, label, error, part):
            row_errors.setdefault(row.row_id, {})[part] = True
            for message in _messages(error):
                errors.append(ValidationError(
                    self.error_messages['property'], code='property',
                    params={'label': label, 'message': message},
                ))

        for row in rows:
            if row.fixed:
                field = self.schema[row.key]
                label = field.label if field.label is not None else pretty_name(str(row.key))
                try:
                    value = field.clean(row.value)
                except ValidationError as error:
                    fail(row, label, error, 'value')
                    continue
                key = row.key
            else:
                raw_key = row.key.strip() if isinstance(row.key, str) else row.key
                if raw_key in (None, '') and row.value in self.extra_field.empty_values:
                    continue  # a blank row nobody filled in
                extra_count += 1
                if raw_key in (None, ''):
                    row_errors.setdefault(row.row_id, {})['key'] = True
                    errors.append(ValidationError(
                        self.error_messages['missing_key'], code='missing_key',
                        params={'value': str(row.value)[:40]},
                    ))
                    continue
                try:
                    key = self.key_field.clean(raw_key)
                except ValidationError as error:
                    fail(row, raw_key, error, 'key')
                    continue
                if key in self.schema or key in seen:
                    row_errors.setdefault(row.row_id, {})['key'] = True
                    errors.append(ValidationError(
                        self.error_messages['duplicate_key'], code='duplicate_key', params={'key': key},
                    ))
                    continue
                try:
                    value = self.extra_field.clean(row.value)
                except ValidationError as error:
                    fail(row, key, error, 'value')
                    continue
            seen.add(key)
            if self.drop_empty and value in forms.Field.empty_values:
                continue
            result[key] = self._to_json(value)

        if self.max_extra is not None and extra_count > self.max_extra:
            errors.append(ValidationError(
                self.error_messages['too_many'], code='too_many', params={'max': self.max_extra},
            ))
        return result, errors, row_errors

    def _to_json(self, value):
        """A cleaned value as JSON-native data: a model becomes its pk, a
        queryset a list of pks, and the encoder handles dates/Decimals/UUIDs."""
        if isinstance(value, models.Model):
            value = value.pk
        elif isinstance(value, models.QuerySet):
            value = list(value.values_list('pk', flat=True))
        return json.loads(json.dumps(value, cls=self.encoder))


def _load_json_dict(value, strict=False):
    """A stored value (dict, JSON string, None) as a dict."""
    if value in (None, ''):
        return {}
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            if strict:
                raise ValueError('invalid JSON')
            return {}
    if not isinstance(value, dict):
        if strict:
            raise ValueError('not a JSON object')
        return {}
    return value


def _reject_constant(name):
    """`NaN` / `Infinity` parse in Python's json but aren't valid JSON: keep them as text."""
    raise ValueError(name)


def _messages(error):
    """Every message of a ValidationError, already formatted with its params."""
    return list(error.messages) if hasattr(error, 'messages') else [str(error)]
