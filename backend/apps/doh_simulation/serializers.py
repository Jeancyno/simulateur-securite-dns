"""
Serializers pour l'API DNS over HTTPS.
"""

from rest_framework import serializers


class DohCompareSerializer(serializers.Serializer):
    """Serializer pour la requête de comparaison DNS vs DoH"""
    domain = serializers.CharField(
        max_length=253,
        required=True,
        allow_blank=False,
        help_text="Domaine à comparer (ex: example.com)"
    )


class ClassicDnsInfoSerializer(serializers.Serializer):
    """Serializer pour les informations DNS classique"""
    protocol = serializers.CharField(required=False, allow_blank=True)
    transport = serializers.CharField(required=False, allow_blank=True)
    encryption = serializers.BooleanField(required=False)
    privacy = serializers.CharField(required=False, allow_blank=True)
    response = serializers.CharField(required=False, allow_blank=True)
    response_time = serializers.CharField(required=False, allow_blank=True)
    resolver = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.CharField(required=False, allow_blank=True)


class DohInfoSerializer(serializers.Serializer):
    """Serializer pour les informations DoH"""
    protocol = serializers.CharField(required=False, allow_blank=True)
    transport = serializers.CharField(required=False, allow_blank=True)
    encryption = serializers.BooleanField(required=False)
    privacy = serializers.CharField(required=False, allow_blank=True)
    response = serializers.CharField(required=False, allow_blank=True)
    response_time = serializers.CharField(required=False, allow_blank=True)
    resolver = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.CharField(required=False, allow_blank=True)
    fallback_used = serializers.BooleanField(required=False)
    fallback_reason = serializers.CharField(required=False, allow_blank=True)
    message = serializers.CharField(required=False, allow_blank=True)


class DohResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse de comparaison DNS vs DoH"""
    success = serializers.BooleanField()
    domain = serializers.CharField(required=False, allow_blank=True)
    classic = ClassicDnsInfoSerializer(required=False, allow_null=True)
    doh = DohInfoSerializer(required=False, allow_null=True)
    error = serializers.CharField(required=False, allow_blank=True)
