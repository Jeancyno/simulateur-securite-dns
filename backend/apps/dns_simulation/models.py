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
    ]

    domain_name = models.CharField(max_length=255)
    record_type = models.CharField(max_length=10, choices=RECORD_TYPES, default="A")
    value = models.CharField(max_length=255)
    ttl = models.PositiveIntegerField(default=300)
    authoritative = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["domain_name", "record_type", ]
        

    def __str__(self):
        return f"{self.domain_name} -> {self.record_type} -> {self.value}"


class DNSCacheEntry(models.Model):
    domain_name = models.CharField(max_length=255)
    record_type = models.CharField(max_length=10)
    value = models.CharField(max_length=255)
    ttl = models.PositiveIntegerField(default=300)
    cached_at = models.DateTimeField(auto_now_add=True)
    poisoned = models.BooleanField(default=False)

    class Meta:
        ordering = ["domain_name", "record_type"]

    def __str__(self):
        status = "Poisoned" if self.poisoned else "Valid"
        return f"{self.domain_name} -> {self.value} [{status}]"


class DNSQuery(models.Model):

    STATUS_CHOICES = [
        ("cache_hit", "Cache Hit"),
        ("cache_miss", "Cache Miss"),
        ("poisoned", "Poisoned Response"),
    ]

    domain_name = models.CharField(max_length=255)
    record_type = models.CharField(max_length=10, default="A")
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    response_value = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="cache_miss")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.domain_name} [{self.status}]"