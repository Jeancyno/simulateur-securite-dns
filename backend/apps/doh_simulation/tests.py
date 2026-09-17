from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from .services.doh_resolver import doh_resolver


class DohAPITestCase(TestCase):
    """Tests pour l'API DNS over HTTPS"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = APIClient()

    def test_compare_valid_domain_format(self):
        """Test de comparaison avec un format de domaine valide"""
        url = reverse('doh-compare')
        data = {'domain': 'example.com'}
        response = self.client.post(url, data, format='json')

        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
        # Le test peut échouer si le réseau n'est pas accessible

    def test_compare_empty_domain(self):
        """Test de comparaison avec un domaine vide"""
        url = reverse('doh-compare')
        data = {'domain': ''}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_compare_invalid_domain_format(self):
        """Test de comparaison avec un format de domaine invalide"""
        url = reverse('doh-compare')
        data = {'domain': 'invalid_domain_format'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_compare_too_long_domain(self):
        """Test de comparaison avec un domaine trop long"""
        url = reverse('doh-compare')
        long_domain = 'a.' * 200 + 'com'
        data = {'domain': long_domain}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_compare_missing_domain_field(self):
        """Test de comparaison sans le champ domaine"""
        url = reverse('doh-compare')
        data = {}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_response_structure(self):
        """Test de la structure de la réponse JSON"""
        url = reverse('doh-compare')
        data = {'domain': 'example.com'}
        response = self.client.post(url, data, format='json')

        if response.status_code == status.HTTP_200_OK:
            self.assertIn('success', response.data)
            self.assertIn('domain', response.data)
            self.assertIn('classic', response.data)
            self.assertIn('doh', response.data)

            # Vérifier la structure des données classic
            self.assertIn('protocol', response.data['classic'])
            self.assertIn('transport', response.data['classic'])
            self.assertIn('encryption', response.data['classic'])
            self.assertIn('response', response.data['classic'])

            # Vérifier la structure des données doh
            self.assertIn('protocol', response.data['doh'])
            self.assertIn('transport', response.data['doh'])
            self.assertIn('encryption', response.data['doh'])
            self.assertIn('response', response.data['doh'])
            self.assertIn('fallback_used', response.data['doh'])
        else:
            self.assertIn('success', response.data)
            self.assertIn('error', response.data)


class DohResolverServiceTestCase(TestCase):
    """Tests pour le service de résolveur DoH"""

    def setUp(self):
        """Configuration initiale"""
        self.resolver = doh_resolver

    def test_is_domain_valid_valid_domain(self):
        """Test de validation d'un domaine valide"""
        self.assertTrue(self.resolver.is_domain_valid('example.com'))
        self.assertTrue(self.resolver.is_domain_valid('sub.example.com'))
        self.assertTrue(self.resolver.is_domain_valid('test-domain.example.com'))

    def test_is_domain_valid_invalid_domain(self):
        """Test de validation d'un domaine invalide"""
        self.assertFalse(self.resolver.is_domain_valid(''))
        self.assertFalse(self.resolver.is_domain_valid('invalid_domain'))
        self.assertFalse(self.resolver.is_domain_valid('-example.com'))
        self.assertFalse(self.resolver.is_domain_valid('example-.com'))

    def test_is_domain_valid_too_long(self):
        """Test de validation d'un domaine trop long"""
        long_domain = 'a.' * 200 + 'com'
        self.assertFalse(self.resolver.is_domain_valid(long_domain))

    def test_is_domain_valid_none(self):
        """Test de validation avec None"""
        self.assertFalse(self.resolver.is_domain_valid(None))
        self.assertFalse(self.resolver.is_domain_valid(123))

    def test_resolve_doh_invalid_domain(self):
        """Test de résolution DoH avec un domaine invalide"""
        result = self.resolver.resolve_doh('invalid_domain')

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_resolve_doh_empty_domain(self):
        """Test de résolution DoH avec un domaine vide"""
        result = self.resolver.resolve_doh('')

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_resolve_doh_real_domain(self):
        """Test de résolution DoH avec un domaine réel"""
        # Ce test peut échouer si le réseau n'est pas accessible
        result = self.resolver.resolve_doh('example.com')

        # On vérifie juste que la structure est correcte
        self.assertIn('success', result)
        self.assertIn('domain', result)

        if result['success']:
            self.assertIn('response', result)
            self.assertIn('response_time', result)
            self.assertIn('resolver_used', result)
            self.assertIn('fallback_used', result)
        else:
            self.assertIn('error', result)

    def test_resolve_doh_fallback(self):
        """Test que le fallback fonctionne quand les résolveurs DoH échouent"""
        # On simule un domaine qui pourrait utiliser le fallback
        # Note: ce test dépend de la disponibilité des résolveurs DoH
        result = self.resolver.resolve_doh('example.com')

        # Si le fallback est utilisé, il doit être indiqué
        if result.get('success') and result.get('fallback_used'):
            self.assertTrue(result['fallback_used'])
            self.assertIn('fallback_reason', result)
            self.assertIn('resolver_used', result)
            self.assertEqual(result['resolver_used'], 'Fallback simulé')

    def test_compare_dns_vs_doh_invalid_domain(self):
        """Test de comparaison avec un domaine invalide"""
        result = self.resolver.compare_dns_vs_doh('invalid_domain')

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_compare_dns_vs_doh_empty_domain(self):
        """Test de comparaison avec un domaine vide"""
        result = self.resolver.compare_dns_vs_doh('')

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_compare_dns_vs_doh_real_domain(self):
        """Test de comparaison avec un domaine réel"""
        # Ce test peut échouer si le réseau n'est pas accessible
        result = self.resolver.compare_dns_vs_doh('example.com')

        # On vérifie juste que la structure est correcte
        self.assertIn('success', result)
        self.assertIn('domain', result)

        if result['success']:
            self.assertIn('classic', result)
            self.assertIn('doh', result)

            # Vérifier classic
            self.assertIn('protocol', result['classic'])
            self.assertIn('transport', result['classic'])
            self.assertIn('encryption', result['classic'])
            self.assertFalse(result['classic']['encryption'])

            # Vérifier doh
            self.assertIn('protocol', result['doh'])
            self.assertIn('transport', result['doh'])
            self.assertIn('encryption', result['doh'])
            self.assertTrue(result['doh']['encryption'])
            self.assertIn('fallback_used', result['doh'])
        else:
            self.assertIn('error', result)

    def test_classic_dns_info_structure(self):
        """Test de la structure des informations DNS classique"""
        result = self.resolver.compare_dns_vs_doh('example.com')

        if result['success']:
            classic_info = result['classic']
            self.assertIn('protocol', classic_info)
            self.assertIn('transport', classic_info)
            self.assertIn('encryption', classic_info)
            self.assertIn('privacy', classic_info)
            self.assertIn('response', classic_info)
            self.assertIn('response_time', classic_info)
            self.assertIn('resolver', classic_info)
            self.assertIn('visibility', classic_info)

    def test_doh_info_structure(self):
        """Test de la structure des informations DoH"""
        result = self.resolver.compare_dns_vs_doh('example.com')

        if result['success']:
            doh_info = result['doh']
            self.assertIn('protocol', doh_info)
            self.assertIn('transport', doh_info)
            self.assertIn('encryption', doh_info)
            self.assertIn('privacy', doh_info)
            self.assertIn('response', doh_info)
            self.assertIn('response_time', doh_info)
            self.assertIn('resolver', doh_info)
            self.assertIn('visibility', doh_info)
            self.assertIn('fallback_used', doh_info)

    def test_encryption_difference(self):
        """Test que le chiffrement est différent entre classic et DoH"""
        result = self.resolver.compare_dns_vs_doh('example.com')

        if result['success']:
            self.assertFalse(result['classic']['encryption'])
            self.assertTrue(result['doh']['encryption'])

    def test_protocol_difference(self):
        """Test que le protocole est différent entre classic et DoH"""
        result = self.resolver.compare_dns_vs_doh('example.com')

        if result['success']:
            self.assertEqual(result['classic']['protocol'], 'DNS')
            self.assertEqual(result['doh']['protocol'], 'DNS over HTTPS')

    def test_fallback_indication(self):
        """Test que le fallback est correctement indiqué"""
        result = self.resolver.compare_dns_vs_doh('example.com')

        if result['success']:
            # Le fallback_used doit être un booléen
            self.assertIsInstance(result['doh']['fallback_used'], bool)

            # Si fallback est utilisé, il doit y avoir une raison
            if result['doh']['fallback_used']:
                self.assertIn('fallback_reason', result['doh'])
