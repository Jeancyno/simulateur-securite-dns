"""
Serializers pour l'API DNSSEC.
"""

from rest_framework import serializers


class DnssecVerifySerializer(serializers.Serializer):
    """Serializer pour la requête de vérification DNSSEC"""
    domain = serializers.CharField(
        max_length=253,
        required=True,
        allow_blank=False,
        help_text="Domaine à vérifier (ex: example.com)"
    )


class DnskeyInfoSerializer(serializers.Serializer):
    """Serializer pour les informations DNSKEY"""
    exists = serializers.BooleanField()
    count = serializers.IntegerField(required=False, allow_null=True)
    records = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_null=True
    )
    description = serializers.CharField(required=False, allow_blank=True)
    error = serializers.CharField(required=False, allow_blank=True)


class DsInfoSerializer(serializers.Serializer):
    """Serializer pour les informations DS"""
    exists = serializers.BooleanField()
    count = serializers.IntegerField(required=False, allow_null=True)
    records = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_null=True
    )
    description = serializers.CharField(required=False, allow_blank=True)
    error = serializers.CharField(required=False, allow_blank=True)


class RrsigInfoSerializer(serializers.Serializer):
    """Serializer pour les informations RRSIG"""
    exists = serializers.BooleanField()
    count = serializers.IntegerField(required=False, allow_null=True)
    records = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_null=True
    )
    description = serializers.CharField(required=False, allow_blank=True)
    error = serializers.CharField(required=False, allow_blank=True)


class DnssecResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse DNSSEC"""
    success = serializers.BooleanField()
    domain = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    dnskey = DnskeyInfoSerializer(required=False, allow_null=True)
    ds = DsInfoSerializer(required=False, allow_null=True)
    rrsig = RrsigInfoSerializer(required=False, allow_null=True)
    chain_details = serializers.DictField(required=False, allow_null=True)
    message = serializers.CharField(required=False, allow_blank=True)
    error = serializers.CharField(required=False, allow_blank=True)
