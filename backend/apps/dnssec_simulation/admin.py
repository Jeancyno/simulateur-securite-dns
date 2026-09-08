from django.contrib import admin
from .models import DNSRecord, DNSCacheEntry, DNSQuery, TrustAnchor

# Register your models here.
@admin.register(DNSRecord)
class DNSRecordAdmin(admin.ModelAdmin):
    list_display = ('domain_name', 'record_type', 'value', 'ttl', 'is_dnssec_signed', 'created_at')
    list_filter = ('record_type', 'is_dnssec_signed', 'authoritative')
    search_fields = ('domain_name', 'value')
    readonly_fields = ('created_at',)


@admin.register(DNSCacheEntry)
class DNSCacheEntryAdmin(admin.ModelAdmin):
    list_display = ('domain_name', 'record_type', 'value', 'ttl', 'poisoned', 'dnssec_status', 'cached_at')
    list_filter = ('record_type', 'poisoned', 'dnssec_status')
    search_fields = ('domain_name', 'value')
    readonly_fields = ('cached_at', 'validated_at')


@admin.register(DNSQuery)
class DNSQueryAdmin(admin.ModelAdmin):
    list_display = ('domain_name', 'record_type', 'client_ip', 'response_value', 'status', 'created_at')
    list_filter = ('record_type', 'status')
    search_fields = ('domain_name', 'client_ip')
    readonly_fields = ('created_at',)


@admin.register(TrustAnchor)
class TrustAnchorAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_tag', 'algorithm', 'is_active', 'created_at')
    list_filter = ('algorithm', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')