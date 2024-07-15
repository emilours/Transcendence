from django.test import TestCase
from .models import MyModel  # Assurez-vous que vous avez des modèles définis

class MyModelTestCase(TestCase):
    def setUp(self):
        # Prépare les données pour les tests
        MyModel.objects.create(name="test")

    def test_model_str(self):
        # Teste une méthode ou une propriété du modèle
        test_model = MyModel.objects.get(name="test")
        self.assertEqual(str(test_model), "test")
