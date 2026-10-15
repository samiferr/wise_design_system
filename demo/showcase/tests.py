from unittest import mock

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models.deletion import ProtectedError
from django.template import Context, Engine
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from wise_core.mixins import ProtectedDeleteMixin
from wise_core.steps import wizard_steps
from wise_core.templatetags.wise_actions import build_actions
from wise_core.templatetags.wise_tags import field_rows

from .models import Category, Product

User = get_user_model()


def make_user(username, *codenames, superuser=False):
    if superuser:
        return User.objects.create_superuser(username, f'{username}@example.com', 'pw')
    user = User.objects.create_user(username, password='pw')
    for codename in codenames:
        user.user_permissions.add(Permission.objects.get(codename=codename))
    return user


class DemoData:
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Stationery', color='#336699')
        cls.product = Product.objects.create(name='Ballpoint pen', category=cls.category)


class BuildActionsTests(DemoData, TestCase):
    def labels(self, user, **kwargs):
        return [action['label'] for action in build_actions(user, self.product, **kwargs)]

    def test_edit_and_delete_follow_the_model_permissions(self):
        self.assertEqual(self.labels(make_user('a', superuser=True)), ['Edit', 'Delete'])
        self.assertEqual(self.labels(make_user('b', 'change_product')), ['Edit'])
        self.assertEqual(self.labels(make_user('c', 'delete_product')), ['Delete'])
        self.assertEqual(self.labels(make_user('d')), [])

    def test_order_is_actions_edit_more_delete(self):
        user = make_user('a', superuser=True)
        labels = self.labels(user, actions=[{'label': 'Approve', 'url': '/a/'}],
                             more_actions=[{'label': 'Print', 'url': '/p/'}])
        self.assertEqual(labels, ['Approve', 'Edit', 'Print', 'Delete'])

    def test_an_action_with_its_own_permission_is_hidden_without_it(self):
        extra = [{'label': 'Approve', 'url': '/a/', 'permission': 'showcase.approve_product'}]
        self.assertNotIn('Approve', self.labels(make_user('a', 'change_product'), actions=extra))

    def test_explicit_urls_and_switches(self):
        user = make_user('a', superuser=True)
        built = build_actions(user, self.product, edit_url='/e/', delete_url='/d/')
        self.assertEqual([a['url'] for a in built], ['/e/', '/d/'])
        self.assertTrue(built[1]['danger'])
        self.assertEqual(self.labels(user, edit=False, delete=False), [])

    def test_defaults_are_filled_in(self):
        built = build_actions(make_user('a', superuser=True), self.product, actions=[{'label': 'X', 'url': '/x/'}])
        self.assertEqual((built[0]['icon'], built[0]['style']), ('arrow-right', 'secondary'))


class ActionPagesTests(DemoData, TestCase):
    def test_detail_panel_has_one_button_and_an_overflow_menu(self):
        self.client.force_login(make_user('a', superuser=True))
        html = self.client.get(self.product.get_absolute_url()).content.decode()
        self.assertIn('detail-panel-overflow', html)
        self.assertIn(reverse('product_delete_view', args=[self.product.pk]), html)

    def test_no_permission_means_no_empty_menu(self):
        self.client.force_login(make_user('a', 'view_product', 'view_category', 'view_productvariant',
                                          'view_productreview'))
        html = self.client.get(self.product.get_absolute_url()).content.decode()
        self.assertNotIn('detail-panel-overflow', html)

    def test_row_actions_render_in_the_table_view(self):
        self.client.force_login(make_user('a', superuser=True))
        html = self.client.get(reverse('product_list_view') + '?view=table').content.decode()
        self.assertIn('row-actions', html)


class FieldRowsTests(TestCase):
    class SampleForm(forms.Form):
        field_rows = (('dosage', 'unit'), ('gone', 'start'))
        name = forms.CharField()
        dosage = forms.CharField()
        notes = forms.CharField()
        unit = forms.CharField()
        start = forms.CharField()

    def test_groups_share_a_row_at_the_position_of_their_first_field(self):
        rows = field_rows(self.SampleForm())
        self.assertEqual([[f.name for f in row] for row in rows],
                         [['name'], ['dosage', 'unit'], ['notes'], ['start']])

    def test_a_form_without_groups_is_one_field_per_row(self):
        class Plain(forms.Form):
            a = forms.CharField()
            b = forms.CharField()
        self.assertEqual([len(row) for row in field_rows(Plain())], [1, 1])

    def test_form_media_is_rendered_once_by_the_include(self):
        class WithMedia(forms.Form):
            class Media:
                js = ('some/widget.js',)
            a = forms.CharField()
        html = Engine.get_default().from_string(
            "{% include 'wise_core/components/_form_fields.html' %}").render(Context({'form': WithMedia()}))
        self.assertEqual(html.count('some/widget.js'), 1)


class WizardStepsTests(TestCase):
    def test_states_follow_the_current_index(self):
        steps = wizard_steps(['A', 'B', 'C'], current=1, urls=['/a/', None, None])
        self.assertEqual([s['state'] for s in steps], ['done', 'current', 'upcoming'])
        self.assertEqual([s['number'] for s in steps], [1, 2, 3])
        self.assertEqual(steps[0]['url'], '/a/')

    def test_include_marks_the_current_step_and_links_a_finished_one(self):
        html = Engine.get_default().from_string("{% include 'wise_core/components/_steps.html' %}").render(
            Context({'steps': wizard_steps(['A', 'B', 'C'], current=1, urls=['/a/', None, None])}))
        self.assertEqual(html.count('aria-current="step"'), 1)
        self.assertIn('<a class="step-label" href="/a/">A</a>', html)


class ProtectedDeleteTests(DemoData, TestCase):
    def blocked(self):
        return ProtectedError('blocked', {self.product})

    def test_delete_page_lists_the_blockers_and_drops_the_button(self):
        self.client.force_login(make_user('a', superuser=True))
        with mock.patch('django.db.models.deletion.Collector.collect', side_effect=self.blocked()):
            html = self.client.get(reverse('category_delete_view', args=[self.category.pk])).content.decode()
        self.assertIn('data-role="delete-blockers"', html)
        self.assertIn('Ballpoint pen', html)
        self.assertNotIn('btn btn-danger', html)

    def test_a_deletable_record_shows_the_normal_confirmation(self):
        self.client.force_login(make_user('a', superuser=True))
        html = self.client.get(reverse('category_delete_view', args=[self.category.pk])).content.decode()
        self.assertNotIn('delete-blockers', html)
        self.assertIn('btn btn-danger', html)

    def test_a_post_the_database_refuses_shows_the_same_page(self):
        self.client.force_login(make_user('a', superuser=True))
        with mock.patch.object(Category, 'delete', side_effect=self.blocked()):
            response = self.client.post(reverse('category_delete_view', args=[self.category.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-role="delete-blockers"')
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())

    def test_blockers_are_named_only_for_a_visitor_who_may_view_them(self):
        request = RequestFactory().get('/')
        view = ProtectedDeleteMixin()
        view.request = request
        request.user = make_user('a')
        groups = view.describe_blockers([self.product])
        self.assertEqual((groups[0]['label'], groups[0]['count'], groups[0]['records']), ('Product', 1, []))
        request.user = make_user('b', 'view_product')
        self.assertEqual(view.describe_blockers([self.product])[0]['records'][0]['label'], 'Ballpoint pen')


class SearchTests(DemoData, TestCase):
    def setUp(self):
        self.client.force_login(make_user('a', superuser=True))
        self.url = reverse('product_list_view')

    def test_a_search_is_not_an_applied_filter(self):
        response = self.client.get(self.url, {'q': 'pen'})
        self.assertEqual(response.context['filter_kwargs_count'], 0)
        self.assertTrue(response.context['can_search'])
        self.assertTrue(response.context['search_active'])
        self.assertContains(response, self.product.name)

    def test_a_filter_still_counts(self):
        response = self.client.get(self.url, {'name': 'pen'})
        self.assertEqual(response.context['filter_kwargs_count'], 1)

    def test_an_empty_search_says_so_instead_of_inviting_a_first_record(self):
        response = self.client.get(self.url, {'q': 'zzzz'})
        self.assertContains(response, 'Nothing matches your search')
        self.assertContains(response, 'Clear search')
        self.assertNotContains(response, 'Create the first')

    def test_a_list_without_a_search_filter_has_no_search_bar(self):
        response = self.client.get(reverse('product_variant_list_view', args=[self.product.pk]))
        self.assertFalse(response.context['can_search'])
        self.assertNotContains(response, 'role="search"')


class NavTests(DemoData, TestCase):
    def setUp(self):
        self.client.force_login(make_user('a', superuser=True))

    def test_breadcrumbs_follow_the_page_when_enabled(self):
        html = self.client.get(self.product.get_absolute_url()).content.decode()
        self.assertIn('aria-label="Breadcrumb"', html)
        self.assertIn('aria-current="page">Ballpoint pen</span>', html)

    @override_settings(WISE_BREADCRUMBS=False)
    def test_breadcrumbs_are_off_by_default(self):
        html = self.client.get(self.product.get_absolute_url()).content.decode()
        self.assertNotIn('aria-label="Breadcrumb"', html)

    def test_the_sidebar_is_a_tree_with_the_current_section_open(self):
        html = self.client.get(self.product.get_absolute_url()).content.decode()
        self.assertIn('class="tree"', html)
        self.assertIn('class="tree-leaf selected"', html)


class PropertiesFieldTests(DemoData, TestCase):
    """wise_core.widgets.PropertiesField: a JSONField edited as key/value rows."""

    def make_form(self, data=None, initial=None, **field_kwargs):
        from wise_core.widgets import PropertiesField

        field_kwargs.setdefault('allow_extra', True)

        class SpecsForm(forms.Form):
            specs = PropertiesField(schema={
                'weight': forms.DecimalField(min_value=0, label='Weight (kg)'),
                'color': forms.ChoiceField(choices=[('red', 'Red'), ('blue', 'Blue')], required=False),
                'released': forms.DateField(required=False),
                'fragile': forms.BooleanField(required=False),  # unchecked is stored as False
                'category': forms.ModelChoiceField(Category.objects.all(), required=False),
            }, **field_kwargs)

        return SpecsForm(data=data, initial=initial)

    def post(self, **values):
        data = {'specs': ''}
        data.update({f'specs__{k}': v for k, v in values.items()})
        return data

    def test_each_schema_value_is_cleaned_by_its_own_field_into_json(self):
        form = self.make_form(self.post(s0='1.50', s1='blue', s2='2026-03-04', s3='on', s4=str(self.category.pk)))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['specs'], {
            'weight': '1.50', 'color': 'blue', 'released': '2026-03-04', 'fragile': True,
            'category': self.category.pk,
        })

    def test_schema_errors_are_prefixed_with_the_label_and_mark_only_that_row(self):
        form = self.make_form(self.post(s0='-1', s1='green'))
        self.assertFalse(form.is_valid())
        errors = form.errors['specs']
        self.assertIn('Weight (kg): Ensure this value is greater than or equal to 0.', errors)
        self.assertTrue(any(e.startswith('Color: Select a valid choice.') for e in errors))
        html = str(form['specs'])
        self.assertIn('id="id_specs__s0" aria-invalid="true"', html)
        self.assertNotIn('id="id_specs__s2" aria-invalid', html)

    def test_a_required_schema_key_must_be_filled(self):
        form = self.make_form(self.post(s0=''))
        self.assertFalse(form.is_valid())
        self.assertIn('Weight (kg): This field is required.', form.errors['specs'])

    def test_free_rows_keep_their_posted_order_and_skip_blank_ones(self):
        form = self.make_form(self.post(
            s0='2', x7__key='zeta', x7__value='last', x2__key='alpha', x2__value='first',
            x3__key='', x3__value='',
        ))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(list(form.cleaned_data['specs']), ['weight', 'fragile', 'alpha', 'zeta'])

    def test_free_values_are_typed_json_unless_they_are_plain_text(self):
        form = self.make_form(self.post(
            s0='2', x0__key='ports', x0__value='4', x1__key='hdmi', x1__value='true',
            x2__key='zip', x2__value='01234', x3__key='code', x3__value='"42"', x4__key='tags', x4__value='["a", "b"]',
            x5__key='nan', x5__value='NaN',
        ))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['specs'], {
            'weight': '2', 'fragile': False,
            'ports': 4, 'hdmi': True, 'zip': '01234', 'code': '42', 'tags': ['a', 'b'], 'nan': 'NaN',
        })

    def test_stored_values_round_trip_through_the_rendered_inputs(self):
        html = str(self.make_form(initial={'specs': {'weight': '2', 'code': '42', 'tags': ['a'], 'zip': '01234'}})['specs'])
        self.assertIn('value="&quot;42&quot;"', html)
        self.assertIn('value="[&quot;a&quot;]"', html)
        self.assertIn('value="01234"', html)

    def test_duplicate_and_missing_keys_are_rejected(self):
        form = self.make_form(self.post(
            s0='1', x0__key='color', x0__value='x', x1__key='a', x1__value='1',
            x2__key='a', x2__value='2', x3__key='', x3__value='orphan',
        ))
        self.assertFalse(form.is_valid())
        errors = form.errors['specs']
        self.assertIn('The key “color” is used more than once.', errors)
        self.assertIn('The key “a” is used more than once.', errors)
        self.assertIn('Enter a key for the value “orphan”.', errors)

    def test_extra_keys_need_allow_extra(self):
        form = self.make_form(self.post(s0='1', x0__key='rogue', x0__value='x'), allow_extra=False)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['specs'], {'weight': '1', 'fragile': False})
        self.assertNotIn('data-property-add', str(form['specs']))

    def test_max_extra_and_custom_key_and_value_fields(self):
        form = self.make_form(
            self.post(s0='1', x0__key='bad key', x0__value='3', x1__key='ok', x1__value='x', x2__key='more', x2__value='5'),
            key_field=forms.SlugField(), extra_field=forms.IntegerField(), max_extra=1,
        )
        self.assertFalse(form.is_valid())
        errors = form.errors['specs']
        self.assertTrue(any(e.startswith('bad key: Enter a valid “slug”') for e in errors))
        self.assertIn('ok: Enter a whole number.', errors)
        self.assertIn('Add at most 1 custom properties.', errors)

    def test_has_changed_compares_the_cleaned_dict(self):
        initial = {'specs': {'weight': '1.50', 'color': 'red', 'fragile': False}}
        self.assertFalse(self.make_form(self.post(s0='1.50', s1='red'), initial=initial).has_changed())
        self.assertTrue(self.make_form(self.post(s0='2', s1='red'), initial=initial).has_changed())

    def test_the_product_form_saves_specs_to_the_json_field(self):
        self.client.force_login(make_user('admin', superuser=True))
        url = reverse('product_update_view', args=[self.product.pk])
        response = self.client.get(url)
        self.assertContains(response, 'data-properties')
        response = self.client.post(url, {
            'name': self.product.name, 'category': self.category.pk, 'notes': '',
            'specs': '', 'specs__s0': '0.250', 'specs__s1': 'black', 'specs__s2': '2',
            'specs__x0__key': 'ink', 'specs__x0__value': 'blue',
        })
        self.assertEqual(response.status_code, 302, getattr(response, 'context', None) and response.context['form'].errors)
        self.product.refresh_from_db()
        self.assertEqual(self.product.specs, {'weight_kg': '0.250', 'color': 'black', 'warranty_years': 2, 'fragile': False, 'ink': 'blue'})

    def test_the_admin_edits_specs_with_the_same_field(self):
        self.client.force_login(make_user('admin', superuser=True))
        response = self.client.get(reverse('admin:showcase_product_change', args=[self.product.pk]))
        self.assertContains(response, 'name="specs__s0"')

    def test_docs_page_renders(self):
        response = self.client.get(reverse('docs_forms_properties_input'))
        self.assertContains(response, 'The key “color” is used more than once.')
