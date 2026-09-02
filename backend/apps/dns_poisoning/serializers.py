"""
Serializers pour l'API d'empoisonnement DNS.
"""

from rest_framework import serializers


class DnsResolveSerializer(serializers.Serializer):
    """Serializer pour la requête de résolution DNS"""
    domain = serializers.CharField(
        max_length=253,
        help_text="Domaine à résoudre (ex: www.banque-demo.test)"
    )


class DnsPoisonSerializer(serializers.Serializer):
    """Serializer pour la requête d'empoisonnement DNS"""
    domain = serializers.CharField(
        max_length=253,
        help_text="Domaine à empoisonner (ex: www.banque-demo.test)"
    )
    falsified_ip = serializers.CharField(
        max_length=15,
        help_text="Adresse IP falsifiée à injecter (ex: 192.168.1.99)"
    )


class DnsResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse DNS"""
    success = serializers.BooleanField()
    domain = serializers.CharField(required=False, allow_null=True)
    legitimate_ip = serializers.CharField(required=False, allow_null=True)
    resolved_ip = serializers.CharField(required=False, allow_null=True)
    cache_status = serializers.CharField(required=False, allow_null=True)
    response_source = serializers.CharField(required=False, allow_null=True)
    error = serializers.CharField(required=False, allow_null=True)


class DnsResetSerializer(serializers.Serializer):
    """Serializer pour la réinitialisation du cache (sans payload)"""
    pass


class DnsResetResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse de réinitialisation"""
    success = serializers.BooleanField()
    message = serializers.CharField()
