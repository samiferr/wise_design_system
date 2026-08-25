from rest_framework import routers, viewsets

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Backs the `AutocompleteInputWidget` on ProductForm.category - see
    docs/autocomplete-widget.md's "Backend contract" for what each of the
    widget's three calls (list/search, detail, OPTIONS) expects here.
    """
    serializer_class = CategorySerializer

    def get_queryset(self):
        qs = Category.objects.all()
        q = self.request.query_params.get('q')
        if not q or q == 'all':
            return qs
        return qs.filter(name__icontains=q)


router = routers.SimpleRouter()
router.register('categories', CategoryViewSet, basename='category-api')
