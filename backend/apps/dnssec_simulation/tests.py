from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from .services.dnssec_validator import dnssec_validator


class DnssecAPITestCase(TestCase):
    """Tests pour l'API DNSSEC"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = APIClient()

    def test_verify_valid_domain_format(self):
        """Test de vérification avec un format de domaine valide"""
        url = reverse('dnssec-verify')
        data = {'domain': 'example.com'}
        response = self.client.post(url, data, format='json')

        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
        # Le domaine peut être valide mais non signé, ou signer une erreur

    def test_verify_empty_domain(self):
        """Test de vérification avec un domaine vide"""
        url = reverse('dnssec-verify')
        data = {'domain': ''}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_verify_invalid_domain_format(self):
        """Test de vérification avec un format de domaine invalide"""
        url = reverse('dnssec-verify')
        data = {'domain': 'invalid_domain_format'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_verify_too_long_domain(self):
        """Test de vérification avec un domaine trop long"""
        url = reverse('dnssec-verify')
        long_domain = 'a.' * 200 + 'com'
        data = {'domain': long_domain}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_verify_missing_domain_field(self):
        """Test de vérification sans le champ domaine"""
        url = reverse('dnssec-verify')
        data = {}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_response_structure(self):
        """Test de la structure de la réponse JSON"""
        url = reverse('dnssec-verify')
        data = {'domain': 'example.com'}
        response = self.client.post(url, data, format='json')

        if response.status_code == status.HTTP_200_OK:
            self.assertIn('success', response.data)
            self.assertIn('domain', response.data)
            self.assertIn('status', response.data)
            self.assertIn('dnskey', response.data)
            self.assertIn('ds', response.data)
            self.assertIn('rrsig', response.data)
        else:
            self.assertIn('success', response.data)
            self.assertIn('error', response.data)


class DnssecValidatorServiceTestCase(TestCase):
    """Tests pour le service de validateur DNSSEC"""

    def setUp(self):
        """Configuration initiale"""
        self.validator = dnssec_validator

    def test_is_domain_valid_valid_domain(self):
        """Test de validation d'un domaine valide"""
        self.assertTrue(self.validator.is_domain_valid('example.com'))
        self.assertTrue(self.validator.is_domain_valid('sub.example.com'))
        self.assertTrue(self.validator.is_domain_valid('test-domain.example.com'))

    def test_is_domain_valid_invalid_domain(self):
        """Test de validation d'un domaine invalide"""
        self.assertFalse(self.validator.is_domain_valid(''))
        self.assertFalse(self.validator.is_domain_valid('invalid_domain'))
        self.assertFalse(self.validator.is_domain_valid('-example.com'))
        self.assertFalse(self.validator.is_domain_valid('example-.com'))

    def test_is_domain_valid_too_long(self):
        """Test de validation d'un domaine trop long"""
        long_domain = 'a.' * 200 + 'com'
        self.assertFalse(self.validator.is_domain_valid(long_domain))

    def test_is_domain_valid_none(self):
        """Test de validation avec None"""
        self.assertFalse(self.validator.is_domain_valid(None))
        self.assertFalse(self.validator.is_domain_valid(123))

    def test_verify_dnssec_invalid_domain(self):
        """Test de vérification DNSSEC avec un domaine invalide"""
        result = self.validator.verify_dnssec('invalid_domain')

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_verify_dnssec_empty_domain(self):
        """Test de vérification DNSSEC avec un domaine vide"""
        result = self.validator.verify_dnssec('')

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_verify_dnssec_real_domain(self):
        """Test de vérification DNSSEC avec un domaine réel"""
        # Ce test peut échouer si le DNS n'est pas accessible
        # ou si le domaine n'existe pas
        result = self.validator.verify_dnssec('example.com')

        # On vérifie juste que la structure est correcte
        self.assertIn('success', result)
        self.assertIn('domain', result)

        if result['success']:
            self.assertIn('status', result)
            self.assertIn('dnskey', result)
            self.assertIn('ds', result)
            self.assertIn('rrsig', result)
            self.assertIn(result['status'], ['VALID', 'UNSIGNED', 'INVALID'])
        else:
            self.assertIn('error', result)

    def test_verify_dnssec_nonexistent_domain(self):
        """Test de vérification DNSSEC avec un domaine inexistant"""
        result = self.validator.verify_dnssec('this-domain-definitely-does-not-exist-12345.com')

        # Le domaine peut ne pas exister (NXDOMAIN)
        self.assertIn('success', result)
        if not result['success']:
            self.assertIn('error', result)

    def test_dnskey_info_structure(self):
        """Test de la structure des informations DNSKEY"""
        result = self.validator.verify_dnssec('example.com')

        if result['success']:
            dnskey_info = result['dnskey']
            self.assertIn('exists', dnskey_info)
            self.assertIsInstance(dnskey_info['exists'], bool)

            if dnskey_info['exists']:
                self.assertIn('count', dnskey_info)
                self.assertIn('records', dnskey_info)
                self.assertIn('description', dnskey_info)
            else:
                self.assertIn('error', dnskey_info)

    def test_ds_info_structure(self):
        """Test de la structure des informations DS"""
        result = self.validator.verify_dnssec('example.com')

        if result['success']:
            ds_info = result['ds']
            self.assertIn('exists', ds_info)
            self.assertIsInstance(ds_info['exists'], bool)

            if ds_info['exists']:
                self.assertIn('count', ds_info)
                self.assertIn('records', ds_info)
                self.assertIn('description', ds_info)
            else:
                self.assertIn('error', ds_info)

    def test_rrsig_info_structure(self):
        """Test de la structure des informations RRSIG"""
        result = self.validator.verify_dnssec('example.com')

        if result['success']:
            rrsig_info = result['rrsig']
            self.assertIn('exists', rrsig_info)
            self.assertIsInstance(rrsig_info['exists'], bool)

            if rrsig_info['exists']:
                self.assertIn('count', rrsig_info)
                self.assertIn('records', rrsig_info)
                self.assertIn('description', rrsig_info)
            else:
                self.assertIn('error', rrsig_info)

    def test_chain_details_structure(self):
        """Test de la structure des détails de la chaîne"""
        result = self.validator.verify_dnssec('example.com')

        if result['success']:
            self.assertIn('chain_details', result)
            if result['chain_details']:
                self.assertIsInstance(result['chain_details'], dict)

    def test_status_values(self):
        """Test que le status prend les bonnes valeurs"""
        result = self.validator.verify_dnssec('example.com')

        if result['success']:
            self.assertIn(result['status'], ['VALID', 'UNSIGNED', 'INVALID'])

    def test_message_field(self):
        """Test que le champ message est présent"""
        result = self.validator.verify_dnssec('example.com')

        if result['success']:
            self.assertIn('message', result)
            self.assertIsInstance(result['message'], str)
