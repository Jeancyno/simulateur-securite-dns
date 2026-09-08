from django.db import models

# Create your models here.

class DNSRecord(models.Model):
    RECORD_TYPES = [
        ("A", "A"),
        ("AAAA", "AAAA"),
        ("CNAME", "CNAME"),
        ("MX", "MX"),
        ("NS", "NS"),
        ("PTR", "PTR"),
        ("SOA", "SOA"),
        ("SRV", "SRV"),
        ("TXT", "TXT"),
        ("DNSKEY", "DNSKEY"),
        ("RRSIG", "RRSIG"),
        ("DS", "DS"),
        ("NSEC", "NSEC"),
        ("NSEC3", "NSEC3"),
    ]

    domain_name = models.CharField(max_length=255, db_index=True)
    record_type = models.CharField(max_length=10, choices=RECORD_TYPES, default="A")
    value = models.CharField(max_length=255)
    ttl = models.PositiveIntegerField(default=300)
    authoritative = models.BooleanField(default=True)
    is_dnssec_signed = models.BooleanField(default=False)
    algorithm = models.IntegerField(null=True, blank=True)
    key_tag = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["domain_name", "record_type", "value"]
        indexes = [
            models.Index(fields=['domain_name', 'record_type']),
        ]

    def __str__(self):
        return f"{self.domain_name} ({self.record_type}) -> {self.value}"


class DNSCacheEntry(models.Model):
    DNSEC_STATUS_CHOICES = [
        ("SECURE", "Sécurisé"),
        ("INSECURE", "Non sécurisé"),
        ("BOGUS", "Erroné"),
        ("UNKNOWN", "Inconnu"),
    ]

    domain_name = models.CharField(max_length=255, db_index=True)
    record_type = models.CharField(max_length=10, default="A")
    value = models.CharField(max_length=255)
    ttl = models.PositiveIntegerField(default=300)
    cached_at = models.DateTimeField(auto_now_add=True)
    poisoned = models.BooleanField(default=False)
    dnssec_status = models.CharField(
        max_length=20,
        choices=DNSEC_STATUS_CHOICES,
        default="UNKNOWN"
    )
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["domain_name", "record_type"]
        indexes = [
            models.Index(fields=['domain_name', 'record_type']),
            models.Index(fields=['poisoned']),
        ]

    def __str__(self):
        poisoned_marker = "⚠️ " if self.poisoned else ""
        return f"{poisoned_marker}{self.domain_name} -> {self.value} [{self.dnssec_status}]"


class DNSQuery(models.Model):
    STATUS_CHOICES = [
        ("cache_hit", "Cache Hit"),
        ("cache_miss", "Cache Miss"),
        ("not_found", "Not Found"),
        ("poisoned", "Poisoned"),
        ("dnssec_secure", "DNSSEC Secure"),
        ("dnssec_bogus", "DNSSEC Bogus"),
        ("dnssec_insecure", "DNSSEC Insecure"),
    ]

    domain_name = models.CharField(max_length=255, db_index=True)
    record_type = models.CharField(max_length=10, default="A")
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    response_value = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="cache_miss")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['domain_name', 'status']),
        ]

    def __str__(self):
        return f"{self.domain_name} -> {self.status} ({self.created_at})"


class TrustAnchor(models.Model):
    name = models.CharField(max_length=255, default=".")
    key_tag = models.IntegerField()
    algorithm = models.IntegerField()
    public_key = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("name", "key_tag", "algorithm")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (tag: {self.key_tag}, algo: {self.algorithm})"