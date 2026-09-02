from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from .services.fake_dns_resolver import fake_dns_resolver
from .services.dns_cache import dns_cache, CacheStatus


class DnsPoisoningAPITestCase(TestCase):
    """Tests pour l'API d'empoisonnement DNS"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = APIClient()
        # Réinitialiser le cache avant chaque test
        dns_cache.reset()
    
    def test_get_fake_domains(self):
        """Test de récupération des domaines fictifs"""
        url = reverse('dns_poisoning:get_fake_domains')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIsInstance(response.data['domains'], list)
        self.assertIn('www.banque-demo.test', response.data['domains'])
    
    def test_resolve_known_domain(self):
        """Test de résolution d'un domaine connu"""
        url = reverse('dns_poisoning:resolve_dns')
        data = {'domain': 'www.banque-demo.test'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['domain'], 'www.banque-demo.test')
        self.assertEqual(response.data['legitimate_ip'], '192.168.1.10')
        self.assertEqual(response.data['resolved_ip'], '192.168.1.10')
        self.assertEqual(response.data['cache_status'], 'CLEAN')
        self.assertEqual(response.data['response_source'], 'LEGITIMATE')
    
    def test_resolve_unknown_domain(self):
        """Test de résolution d'un domaine inconnu"""
        url = reverse('dns_poisoning:resolve_dns')
        data = {'domain': 'unknown-domain.com'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data)
    
    def test_resolve_empty_domain(self):
        """Test de résolution avec un domaine vide"""
        url = reverse('dns_poisoning:resolve_dns')
        data = {'domain': ''}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_simulate_poisoning(self):
        """Test de simulation d'empoisonnement"""
        url = reverse('dns_poisoning:simulate_poisoning')
        data = {
            'domain': 'www.banque-demo.test',
            'falsified_ip': '192.168.1.99'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['domain'], 'www.banque-demo.test')
        self.assertEqual(response.data['legitimate_ip'], '192.168.1.10')
        self.assertEqual(response.data['resolved_ip'], '192.168.1.99')
        self.assertEqual(response.data['cache_status'], 'POISONED')
        self.assertEqual(response.data['response_source'], 'FALSIFIED')
    
    def test_simulate_poisoning_unknown_domain(self):
        """Test d'empoisonnement sur un domaine inconnu"""
        url = reverse('dns_poisoning:simulate_poisoning')
        data = {
            'domain': 'unknown-domain.com',
            'falsified_ip': '192.168.1.99'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_simulate_poisoning_invalid_ip(self):
        """Test d'empoisonnement avec une IP invalide"""
        url = reverse('dns_poisoning:simulate_poisoning')
        data = {
            'domain': 'www.banque-demo.test',
            'falsified_ip': 'invalid-ip'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_resolve_after_poisoning(self):
        """Test de résolution après empoisonnement"""
        # D'abord empoisonner
        poison_url = reverse('dns_poisoning:simulate_poisoning')
        poison_data = {
            'domain': 'www.banque-demo.test',
            'falsified_ip': '192.168.1.99'
        }
        self.client.post(poison_url, poison_data, format='json')
        
        # Ensuite résoudre
        resolve_url = reverse('dns_poisoning:resolve_dns')
        resolve_data = {'domain': 'www.banque-demo.test'}
        response = self.client.post(resolve_url, resolve_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['resolved_ip'], '192.168.1.99')
        self.assertEqual(response.data['cache_status'], 'POISONED')
        self.assertEqual(response.data['response_source'], 'FALSIFIED')
    
    def test_reset_cache(self):
        """Test de réinitialisation du cache"""
        # D'abord empoisonner
        poison_url = reverse('dns_poisoning:simulate_poisoning')
        poison_data = {
            'domain': 'www.banque-demo.test',
            'falsified_ip': '192.168.1.99'
        }
        self.client.post(poison_url, poison_data, format='json')
        
        # Réinitialiser
        reset_url = reverse('dns_poisoning:reset_cache')
        response = self.client.post(reset_url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Vérifier que le cache est bien réinitialisé
        resolve_url = reverse('dns_poisoning:resolve_dns')
        resolve_data = {'domain': 'www.banque-demo.test'}
        resolve_response = self.client.post(resolve_url, resolve_data, format='json')
        
        self.assertEqual(resolve_response.data['resolved_ip'], '192.168.1.10')
        self.assertEqual(resolve_response.data['cache_status'], 'CLEAN')
    
    def test_multiple_resolutions_same_domain(self):
        """Test de résolutions multiples du même domaine"""
        url = reverse('dns_poisoning:resolve_dns')
        data = {'domain': 'www.banque-demo.test'}
        
        # Première résolution
        response1 = self.client.post(url, data, format='json')
        self.assertEqual(response1.data['cache_status'], 'CLEAN')
        
        # Deuxième résolution (devrait être dans le cache)
        response2 = self.client.post(url, data, format='json')
        self.assertEqual(response2.data['cache_status'], 'CLEAN')
        self.assertEqual(response2.data['resolved_ip'], '192.168.1.10')


class DnsCacheServiceTestCase(TestCase):
    """Tests pour le service de cache DNS"""
    
    def setUp(self):
        """Configuration initiale"""
        self.cache = dns_cache
        self.cache.reset()
    
    def test_cache_entry_creation(self):
        """Test de création d'une entrée de cache"""
        from .services.dns_cache import DnsCacheEntry
        
        entry = DnsCacheEntry(
            domain='test.com',
            ip='192.168.1.1',
            source='TEST',
            status=CacheStatus.CLEAN
        )
        
        self.assertEqual(entry.domain, 'test.com')
        self.assertEqual(entry.ip, '192.168.1.1')
        self.assertEqual(entry.source, 'TEST')
        self.assertEqual(entry.status, CacheStatus.CLEAN)
    
    def test_cache_set_and_get(self):
        """Test d'ajout et récupération dans le cache"""
        from .services.dns_cache import DnsCacheEntry
        
        entry = DnsCacheEntry(
            domain='test.com',
            ip='192.168.1.1',
            source='TEST',
            status=CacheStatus.CLEAN
        )
        
        self.cache.set(entry)
        retrieved = self.cache.get('test.com')
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.domain, 'test.com')
        self.assertEqual(retrieved.ip, '192.168.1.1')
    
    def test_cache_exists(self):
        """Test de vérification d'existence"""
        from .services.dns_cache import DnsCacheEntry
        
        entry = DnsCacheEntry(
            domain='test.com',
            ip='192.168.1.1',
            source='TEST',
            status=CacheStatus.CLEAN
        )
        
        self.assertFalse(self.cache.exists('test.com'))
        self.cache.set(entry)
        self.assertTrue(self.cache.exists('test.com'))
    
    def test_cache_reset(self):
        """Test de réinitialisation du cache"""
        from .services.dns_cache import DnsCacheEntry
        
        entry = DnsCacheEntry(
            domain='test.com',
            ip='192.168.1.1',
            source='TEST',
            status=CacheStatus.CLEAN
        )
        
        self.cache.set(entry)
        self.assertTrue(self.cache.exists('test.com'))
        
        self.cache.reset()
        self.assertFalse(self.cache.exists('test.com'))
    
    def test_cache_poisoned_status(self):
        """Test du statut empoisonné"""
        from .services.dns_cache import DnsCacheEntry
        
        entry = DnsCacheEntry(
            domain='test.com',
            ip='192.168.1.1',
            source='TEST',
            status=CacheStatus.POISONED
        )
        
        self.cache.set(entry)
        self.assertTrue(self.cache.is_poisoned('test.com'))
        self.assertEqual(self.cache.get_status('test.com'), CacheStatus.POISONED)


class FakeDnsResolverServiceTestCase(TestCase):
    """Tests pour le service de résolveur DNS fictif"""
    
    def setUp(self):
        """Configuration initiale"""
        self.resolver = fake_dns_resolver
        dns_cache.reset()
    
    def test_is_domain_known(self):
        """Test de vérification de domaine connu"""
        self.assertTrue(self.resolver.is_domain_known('www.banque-demo.test'))
        self.assertFalse(self.resolver.is_domain_known('unknown.com'))
    
    def test_get_legitimate_ip(self):
        """Test de récupération de l'IP légitime"""
        ip = self.resolver.get_legitimate_ip('www.banque-demo.test')
        self.assertEqual(ip, '192.168.1.10')
    
    def test_get_legitimate_ip_unknown_domain(self):
        """Test de récupération d'IP pour un domaine inconnu"""
        with self.assertRaises(ValueError):
            self.resolver.get_legitimate_ip('unknown.com')
    
    def test_resolve_known_domain(self):
        """Test de résolution d'un domaine connu"""
        result = self.resolver.resolve('www.banque-demo.test')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['domain'], 'www.banque-demo.test')
        self.assertEqual(result['legitimate_ip'], '192.168.1.10')
        self.assertEqual(result['resolved_ip'], '192.168.1.10')
        self.assertEqual(result['cache_status'], 'CLEAN')
        self.assertEqual(result['response_source'], 'LEGITIMATE')
    
    def test_resolve_unknown_domain(self):
        """Test de résolution d'un domaine inconnu"""
        result = self.resolver.resolve('unknown.com')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_simulate_poisoning(self):
        """Test de simulation d'empoisonnement"""
        result = self.resolver.simulate_poisoning('www.banque-demo.test', '192.168.1.99')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['domain'], 'www.banque-demo.test')
        self.assertEqual(result['legitimate_ip'], '192.168.1.10')
        self.assertEqual(result['resolved_ip'], '192.168.1.99')
        self.assertEqual(result['cache_status'], 'POISONED')
        self.assertEqual(result['response_source'], 'FALSIFIED')
    
    def test_simulate_poisoning_invalid_ip(self):
        """Test d'empoisonnement avec IP invalide"""
        result = self.resolver.simulate_poisoning('www.banque-demo.test', 'invalid')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_reset_cache(self):
        """Test de réinitialisation du cache"""
        # Empoisonner d'abord
        self.resolver.simulate_poisoning('www.banque-demo.test', '192.168.1.99')
        
        # Réinitialiser
        result = self.resolver.reset_cache()
        
        self.assertTrue(result['success'])
        
        # Vérifier que le cache est réinitialisé
        resolve_result = self.resolver.resolve('www.banque-demo.test')
        self.assertEqual(resolve_result['resolved_ip'], '192.168.1.10')
        self.assertEqual(resolve_result['cache_status'], 'CLEAN')
    
    def test_get_all_fake_domains(self):
        """Test de récupération de tous les domaines fictifs"""
        domains = self.resolver.get_all_fake_domains()
        
        self.assertIsInstance(domains, list)
        self.assertIn('www.banque-demo.test', domains)
        self.assertIn('www.exemple.test', domains)
        self.assertIn('www.dns-demo.test', domains)

# Create your tests here.
