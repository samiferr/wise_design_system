import decimal
import io

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from showcase.models import (
    Category,
    Department,
    Product,
    ProductImage,
    ProductReview,
    ProductVariant,
)


# Lumen palette steps (scripts/lumen-scales.json, light theme): a pale
# ground, a mid tone and a deep tone per hue, for the drawn product photos.
_PHOTO_TONES = {
    'blue': ('#f5f9ff', '#accffd', '#274dea'),       # blue-100 / 400 / 1000
    'gray': ('#f8f8f8', '#c6c6c6', '#505050'),       # gray-50 / 400 / 700
    'orange': ('#fff6e7', '#ffc15e', '#c24e00'),     # orange-100 / 400 / 900
}


def _draw_photo(hue, variant, size=800):
    """A flat placeholder "product shot" as PNG bytes: a ground and a shape per angle."""
    from PIL import Image, ImageDraw  # Pillow is a demo requirement (ImageField).

    ground, mid, deep = _PHOTO_TONES[hue]
    image = Image.new('RGB', (size, size), ground)
    draw = ImageDraw.Draw(image)
    unit = size // 8
    draw.ellipse((unit, 6 * unit + unit // 2, 7 * unit, 7 * unit + unit // 4), fill=mid)  # shadow
    if variant % 4 == 0:
        draw.rounded_rectangle((2 * unit, 2 * unit, 6 * unit, 6 * unit + unit // 2), radius=unit // 2, fill=deep)
    elif variant % 4 == 1:
        draw.rounded_rectangle((unit, 3 * unit, 7 * unit, 5 * unit), radius=unit, fill=deep)
        draw.ellipse((5 * unit, 3 * unit + unit // 2, 6 * unit, 4 * unit + unit // 2), fill=ground)
    elif variant % 4 == 2:
        draw.ellipse((2 * unit, 2 * unit, 6 * unit, 6 * unit), fill=deep)
        draw.ellipse((3 * unit, 3 * unit, 5 * unit, 5 * unit), fill=mid)
    else:
        draw.polygon([(4 * unit, unit + unit // 2), (7 * unit, 6 * unit + unit // 2), (unit, 6 * unit + unit // 2)], fill=deep)
    buffer = io.BytesIO()
    image.save(buffer, format='PNG', optimize=True)
    return buffer.getvalue()


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

        # A few photos per product for the image gallery on its Overview
        # tab. Drawn here rather than shipped as binaries; skipped for a
        # product that already has photos, so re-seeding never duplicates.
        photos = {
            'Ballpoint pen (box of 12)': ('blue', ['Front', 'Side', 'Tip', 'Box']),
            'USB-C hub': ('gray', ['Front', 'Ports', 'Cable', 'In use']),
            'Standing desk': ('orange', ['Front', 'Raised', 'Controls']),
        }
        for product_name, (hue, views) in photos.items():
            product = Product.objects.get(name=product_name)
            if product.images.exists():
                continue
            for position, view in enumerate(views):
                image = ProductImage(
                    product=product, position=position,
                    alt_text='{}, {}'.format(product_name, view.lower()),
                )
                image.image.save(
                    'product-{}-{}.png'.format(product.pk, position + 1),
                    ContentFile(_draw_photo(hue, position)),
                    save=False,
                )
                image.save()

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
