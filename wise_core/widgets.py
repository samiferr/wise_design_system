"""
Form widgets for the components whose markup Django has to render.

Everything here is a plain `django.forms` widget emitting the component classes
from tokens.css, so a ModelForm gets the styled control for free and
`wise_core/components/_form_fields.html` keeps rendering the label, help text
and errorlist around it exactly as it does for a stock widget.

The richer, JS-backed widgets live in their own apps instead:
`wise_autocomplete` (AutocompleteInputWidget, AutoSuggestInputWidget) and
`wise_richtext` (RichTextInputWidget).
"""
import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class SwitchInput(forms.CheckboxInput):
    """A checkbox rendered as a switch. Posts and validates like a checkbox."""

    def __init__(self, attrs=None, check_test=None):
        super().__init__({'class': 'switch', **(attrs or {})}, check_test)


class ColorInput(forms.TextInput):
    """`<input type="color">` - the browser supplies the picker itself."""

    input_type = 'color'
    template_name = 'django/forms/widgets/text.html'

    def __init__(self, attrs=None):
        super().__init__({'class': 'color-input', **(attrs or {})})


class ComboboxInput(forms.TextInput):
    """
    A free-text input with a native `<datalist>` of suggestions: the user can
    pick a known value or type a new one.

    This is the no-JS, no-endpoint end of the spectrum. When the option list is
    too big to inline, or you need to search server-side as the user types,
    reach for `wise_autocomplete.AutocompleteInputWidget` instead.
    """

    template_name = 'wise_core/widgets/combobox.html'

    def __init__(self, choices=(), attrs=None):
        self.choices = list(choices)
        super().__init__({'class': 'input', 'list': None, **(attrs or {})})

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        list_id = f'{context["widget"]["attrs"].get("id", "id_" + name)}_list'
        context['widget']['attrs']['list'] = list_id
        context['widget']['list_id'] = list_id
        context['widget']['datalist'] = self.choices
        return context


class RatingInput(forms.RadioSelect):
    """
    A star rating built from real radio inputs - the stars are `<label>`s, so
    clicking one checks its radio and the value posts like any other choice
    field. Keyboard navigation comes free with the radio group.
    """

    template_name = 'wise_core/widgets/rating.html'

    def __init__(self, attrs=None, choices=(), stars=5):
        self.stars = stars
        super().__init__(attrs, choices or [(i, str(i)) for i in range(1, stars + 1)])


class OTPInput(forms.MultiWidget):
    """
    One single-character box per digit of a one-time code.

    Rendering N boxes is the easy half; the useful half is that `OTPField`
    below recombines them into one string before validation, so the rest of
    the form (and your view) sees a normal `"123456"` value.
    """

    template_name = 'wise_core/widgets/otp.html'

    def __init__(self, length=6, attrs=None):
        self.length = length
        widgets = [
            forms.TextInput(attrs={
                'class': 'otp-input',
                'maxlength': '1',
                'inputmode': 'numeric',
                'pattern': '[0-9]*',
                # Only the first box advertises one-time-code, otherwise
                # browsers offer to autofill the whole code into every box.
                'autocomplete': 'one-time-code' if i == 0 else 'off',
                'aria-label': _('Digit %(n)d') % {'n': i + 1},
                **(attrs or {}),
            })
            for i in range(length)
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        """Split an existing `"123456"` back out across the boxes."""
        if not value:
            return [None] * self.length
        digits = list(str(value))[:self.length]
        return digits + [None] * (self.length - len(digits))


class OTPField(forms.MultiValueField):
    """
    The field half of `OTPInput`: joins the per-digit boxes into one string and
    validates it as a whole.

    `require_all_fields=False` so a partially-filled code produces one "enter
    all N digits" error rather than one error per empty box.
    """

    def __init__(self, length=6, **kwargs):
        self.length = length
        fields = [
            forms.CharField(max_length=1, required=False)
            for _i in range(length)
        ]
        kwargs.setdefault('widget', OTPInput(length=length))
        kwargs.setdefault('require_all_fields', False)
        super().__init__(fields, **kwargs)

    def compress(self, data_list):
        if not data_list:
            return ''
        code = ''.join((d or '').strip() for d in data_list)
        if not code:
            return ''
        if len(code) != self.length or not re.fullmatch(r'\d+', code):
            raise ValidationError(
                _('Enter all %(n)d digits of the code.'),
                code='incomplete',
                params={'n': self.length},
            )
        return code
