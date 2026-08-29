from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7, default='#16a34a',
        help_text='Swatch color shown in the datatable, as a hex code.',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail_view', args=[self.pk])


class Product(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    notes = models.TextField(
        blank=True,
        help_text='Rendered with the wise_richtext RichTextInputWidget (Quill).',
    )
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='0-5, rendered by the Rating component on the detail page.',
    )
    available_from = models.DateField(null=True, blank=True)
    datasheet = models.FileField(upload_to='datasheets/', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail_view', args=[self.pk])


class Department(models.Model):
    """
    A self-referencing hierarchy, purely so the Tree component page has real
    recursive data to render rather than a hand-written nest of <details>.

    Deliberately a plain adjacency list (a `parent` FK) rather than MPTT or a
    tree package: the Tree component only ever walks *down* from a root, which
    a prefetch handles fine, and this keeps the demo dependency-free.
    """
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='children',
    )
    icon = models.CharField(
        max_length=40, default='building-2',
        help_text='Lucide icon name rendered next to the node.',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
