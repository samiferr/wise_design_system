from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand

from showcase.models import Category, Department, Product


class Command(BaseCommand):
    help = 'Creates a demo superuser and a handful of sample records for the showcase site.'

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={'is_staff': True, 'is_superuser': True, 'first_name': 'Demo', 'last_name': 'User'},
        )
        if created:
            user.set_password('wise-demo-2026')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created superuser "demo" / "wise-demo-2026".'))
        else:
            self.stdout.write('Superuser "demo" already exists.')

        categories = [
            ('Stationery', 'Pens, notebooks, and desk supplies.', '#16a34a'),
            ('Electronics', 'Cables, adapters, and small devices.', '#15803d'),
            ('Furniture', 'Desks, chairs, and shelving.', '#a97e2e'),
        ]
        made = {}
        for name, description, color in categories:
            category, _ = Category.objects.get_or_create(
                name=name, defaults={'description': description, 'color': color},
            )
            made[name] = category

        products = [
            ('Ballpoint pen (box of 12)', 'Stationery', '<p>Standard <strong>blue ink</strong>, medium tip.</p>', 4),
            ('USB-C hub', 'Electronics', '<p>4 ports, includes HDMI passthrough.</p>', 5),
            ('Standing desk', 'Furniture', '<p>Electric height adjustment, 120x60cm top.</p>', 3),
        ]
        for name, category_name, notes, rating in products:
            product, _ = Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': made[category_name], 'notes': notes,
                    'rating': rating, 'created_by': user,
                },
            )
            # Backfill rows created before `rating` existed - get_or_create's
            # defaults only apply on insert, so re-running the seed after a
            # migration would otherwise leave the new column empty.
            if product.rating is None:
                product.rating = rating
                product.save(update_fields=['rating'])

        # A real hierarchy for the Navigation -> Tree page to walk.
        tree = {
            'Operations': ['Logistics', 'Facilities'],
            'Engineering': ['Platform', 'Frontend', 'Data'],
            'Commercial': ['Sales', 'Support'],
        }
        icons = {'Operations': 'building-2', 'Engineering': 'zap', 'Commercial': 'users'}
        for root_name, children in tree.items():
            root, _ = Department.objects.get_or_create(
                name=root_name, parent=None, defaults={'icon': icons[root_name]},
            )
            for child_name in children:
                Department.objects.get_or_create(
                    name=child_name, parent=root, defaults={'icon': 'clipboard-list'},
                )

        self.stdout.write(self.style.SUCCESS('Demo data ready.'))
