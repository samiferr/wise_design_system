import decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand

from showcase.models import (
    Category,
    Department,
    Product,
    ProductReview,
    ProductVariant,
)


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

        # Two child models per product, so the Products pages have real
        # tabs to switch between - see showcase/views.PRODUCT_TABS.
        variants = {
            'Ballpoint pen (box of 12)': [
                ('Blue, medium tip', 'PEN-BLU-M', '4.90', 120),
                ('Black, fine tip', 'PEN-BLK-F', '4.90', 64),
            ],
            'USB-C hub': [
                ('4 ports', 'HUB-4P', '39.00', 18),
                ('7 ports + HDMI', 'HUB-7P-HDMI', '64.50', 6),
            ],
            'Standing desk': [
                ('120x60cm, oak', 'DSK-120-OAK', '410.00', 3),
                ('160x80cm, walnut', 'DSK-160-WAL', '520.00', 0),
            ],
        }
        for product_name, rows in variants.items():
            product = Product.objects.get(name=product_name)
            for label, sku, price, stock in rows:
                ProductVariant.objects.get_or_create(
                    sku=sku,
                    defaults={
                        'product': product, 'label': label,
                        'price': decimal.Decimal(price), 'stock': stock,
                    },
                )

        reviews = {
            'Ballpoint pen (box of 12)': [
                ('Nadia B.', 4, 'Writes smoothly, though the box arrived open.'),
                ('Tom R.', 5, 'Exactly what the office needed.'),
            ],
            'USB-C hub': [
                ('Priya S.', 5, 'Runs two monitors without dropping frames.'),
                ('Alex M.', 3, 'Gets warm under load.'),
            ],
            'Standing desk': [
                ('Jo K.', 4, 'Solid at full height. Assembly took two people.'),
            ],
        }
        for product_name, rows in reviews.items():
            product = Product.objects.get(name=product_name)
            for author, rating, comment in rows:
                ProductReview.objects.get_or_create(
                    product=product, author=author,
                    defaults={'rating': rating, 'comment': comment},
                )

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
