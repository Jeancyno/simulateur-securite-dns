from django.test import TestCase
from .models import DNSRecord, DNSCacheEntry, DNSQuery, TrustAnchor



# Create your tests here.
class DNSSECModelsTest(TestCase):
    def test_dns_record_creation(self):
        record = DNSRecord.objects.create(
            domain_name="example.com",
            record_type="A",
            value="93.184.216.34",
            ttl=300
        )
        self.assertEqual(record.domain_name, "example.com")
        self.assertEqual(record.value, "93.184.216.34")

    def test_cache_entry_creation(self):
        entry = DNSCacheEntry.objects.create(
            domain_name="example.com",
            record_type="A",
            value="93.184.216.34",
            ttl=300,
            poisoned=False
        )
        self.assertEqual(entry.domain_name, "example.com