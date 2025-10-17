import unittest
import json
import os
import sys

# Ajouter le répertoire parent au path pour pouvoir importer app.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class TestCreditScoringAPI(unittest.TestCase):
    """Tests unitaires pour l'API de scoring crédit"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.app = app.test_client()
        self.app.testing = True

    def test_health_endpoint(self):
        """Teste l'endpoint de santé de l'API"""
        response = self.app.get('/health')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'OK')
        self.assertIn('version', data)
        self.assertIn('model', data)

    def test_get_clients(self):
        """Teste la récupération de la liste des clients"""
        response = self.app.get('/clients')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'OK')
        self.assertIn('client_ids', data)
        self.assertIsInstance(data['client_ids'], list)
        self.assertGreater(len(data['client_ids']), 0)

    def test_client_prediction(self):
        """Teste la prédiction pour un client valide"""
        # D'abord récupérer un ID client valide
        response = self.app.get('/clients?limit=1')
        data = json.loads(response.get_data(as_text=True))
        client_id = data['client_ids'][0]
        
        # Maintenant tester la prédiction
        response = self.app.get(f'/predict/{client_id}')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'OK')
        self.assertIn('probability', data)
        self.assertIn('decision', data)
        self.assertIn(data['decision'], ['ACCEPTÉ', 'REFUSÉ'])

    def test_invalid_client_prediction(self):
        """Teste la prédiction pour un client invalide"""
        response = self.app.get('/predict/0')
        self.assertEqual(response.status_code, 400)
        
        response = self.app.get('/predict/999999999')  # ID supposé invalide
        self.assertEqual(response.status_code, 404)

    def test_client_details(self):
        """Teste la récupération des détails d'un client valide"""
        # D'abord récupérer un ID client valide
        response = self.app.get('/clients?limit=1')
        data = json.loads(response.get_data(as_text=True))
        client_id = data['client_ids'][0]
        
        # Maintenant tester la récupération des détails
        response = self.app.get(f'/client/{client_id}/details')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'OK')
        self.assertIn('personal_info', data)
        self.assertIn('credit_info', data)
        self.assertIn('credit_history', data)

    def test_shap_values(self):
        """Teste la récupération des valeurs SHAP pour un client valide"""
        # D'abord récupérer un ID client valide
        response = self.app.get('/clients?limit=1')
        data = json.loads(response.get_data(as_text=True))
        client_id = data['client_ids'][0]
        
        # Maintenant tester la récupération des valeurs SHAP
        response = self.app.get(f'/shap_values/{client_id}')
        
        # Si l'explainer est disponible, on devrait avoir un statut 200
        # Sinon, on devrait avoir un statut 503
        if response.status_code == 200:
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['status'], 'OK')
            self.assertIn('shap_values', data)
            self.assertIsInstance(data['shap_values'], dict)
        else:
            self.assertEqual(response.status_code, 503)

if __name__ == '__main__':
    unittest.main()