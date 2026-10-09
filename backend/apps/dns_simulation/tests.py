from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from .services.dns_resolver import dns_resolver


class DnsResolverServiceTestCase(TestCase):
    """Tests pour le service de résolveur DNS simulé"""

    def setUp(self):
        """Configuration initiale"""
        self.resolver = dns_resolver

    def test_is_domain_valid(self):
        """Test de validation de format de domaine"""
        self.assertTrue(self.resolver.is_domain_valid('www.regiedeseaux.com'))
        self.assertTrue(self.resolver.is_domain_valid('www.google.com'))
        self.assertTrue(self.resolver.is_domain_valid('exemple.cd'))
        self.assertTrue(self.resolver.is_domain_valid('entreprise.local.test'))
        self.assertFalse(self.resolver.is_domain_valid('bonjour'))
        self.assertFalse(self.resolver.is_domain_valid('abc@'))
        self.assertFalse(self.resolver.is_domain_valid('http://google.com'))
        self.assertFalse(self.resolver.is_domain_valid(''))
        self.assertFalse(self.resolver.is_domain_valid('a' * 254))  # Dépasse 253 caractères

    def test_is_domain_known(self):
        """Test de vérification de domaine connu"""
        self.assertTrue(self.resolver.is_domain_known('example.test'))
        self.assertTrue(self.resolver.is_domain_known('www.banque-demo.test'))
        self.assertFalse(self.resolver.is_domain_known('www.regiedeseaux.com'))

    def test_get_domain_ip_known(self):
        """Test de récupération d'IP pour un domaine connu"""
        ip = self.resolver.get_domain_ip('example.test')
        self.assertEqual(ip, '93.184.216.34')

    def test_get_domain_ip_unknown(self):
        """Test de génération d'IP pour un domaine inconnu"""
        ip = self.resolver.get_domain_ip('www.regiedeseaux.com')
        # L'IP doit être au format IPv4 valide
        parts = ip.split('.')
        self.assertEqual(len(parts), 4)
        self.assertTrue(all(0 <= int(part) <= 255 for part in parts))

    def test_resolve_known_domain(self):
        """Test de résolution d'un domaine connu"""
        result = self.resolver.resolve('example.test')

        self.assertTrue(result['success'])
        self.assertEqual(result['domain'], 'example.test')
        self.assertEqual(result['ip'], '93.184.216.34')
        self.assertIn('time', result)
        self.assertIn('steps', result)
        self.assertEqual(result['status'], 'success')

    def test_resolve_unknown_domain(self):
        """Test de résolution d'un domaine inconnu mais valide"""
        result = self.resolver.resolve('www.regiedeseaux.com')

        self.assertTrue(result['success'])
        self.assertEqual(result['domain'], 'www.regiedeseaux.com')
        # L'IP doit être générée
        self.assertIn('ip', result)
        self.assertEqual(result['status'], 'success')

    def test_resolve_invalid_domain(self):
        """Test de résolution d'un domaine invalide"""
        result = self.resolver.resolve('bonjour')

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_get_available_domains(self):
        """Test de récupération des domaines disponibles"""
        domains = self.resolver.get_available_domains()

        self.assertIsInstance(domains, list)
        self.assertIn('example.test', domains)
        self.assertIn('www.banque-demo.test', domains)


class DnsResolutionAPITestCase(TestCase):
    """Tests pour l'API de résolution DNS"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = APIClient()

    def test_resolve_known_domain_api(self):
        """Test de résolution d'un domaine connu via API"""
        url = reverse('dns_simulation:resolve_dns')
        data = {'domain': 'example.test'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['domain'], 'example.test')
        self.assertEqual(response.data['ip'], '93.184.216.34')

    def test_resolve_free_domain_api(self):
        """Test de résolution d'un domaine libre via API"""
        url = reverse('dns_simulation:resolve_dns')
        data = {'domain': 'www.regiedeseaux.com'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['domain'], 'www.regiedeseaux.com')
        # L'IP doit être générée
        self.assertIn('ip', response.data)

    def test_resolve_invalid_domain_api(self):
        """Test de résolution d'un domaine invalide via API"""
        url = reverse('dns_simulation:resolve_dns')
        data = {'domain': 'bonjour'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_resolve_empty_domain_api(self):
        """Test de résolution avec un domaine vide via API"""
        url = reverse('dns_simulation:resolve_dns')
        data = {'domain': ''}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resolve_domain_with_special_chars_api(self):
        """Test de résolution d'un domaine avec caractères spéciaux via API"""
        url = reverse('dns_simulation:resolve_dns')
        data = {'domain': 'abc@'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_resolve_domain_with_protocol_api(self):
        """Test de résolution d'un domaine avec protocole HTTP via API"""
        url = reverse('dns_simulation:resolve_dns')
        data = {'domain': 'http://google.com'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

