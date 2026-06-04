from django.test import TestCase
from events.models.category import Category
from events.serializers.category_serializer import CategorySerializer

class CategorySerializerTestCase(TestCase):
    def test_category_serializer_returns_expected_fields(self):
        category = Category.objects.create(name="Education")
        serializer = CategorySerializer(instance=category)
        expected_fields = {'id', 'name', 'events'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)
        self.assertEqual(serializer.data['name'], "Education")
        self.assertEqual(serializer.data['events'], [])