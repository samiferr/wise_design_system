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
