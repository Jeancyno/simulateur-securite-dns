from rest_framework import serializers


class DnsResolveSerializer(serializers.Serializer):
    """
    Valide les données reçues pour une résolution DNS normale.
    """

    domain = serializers.CharField(
        max_length=253,
        required=True,
        allow_blank=False
    )


class DnsResponseSerializer(serializers.Serializer):
    """
    Structure la réponse d'une résolution DNS.
    """

    success = serializers.BooleanField()
    domain = serializers.CharField(required=False, allow_blank=True)
    ip = serializers.CharField(required=False, allow_blank=True)
    time = serializers.CharField(required=False, allow_blank=True)
    steps = serializers.IntegerField(required=False)
    status = serializers.CharField(required=False, allow_blank=True)
    timestamp = serializers.CharField(required=False, allow_blank=True)
    requestType = serializers.CharField(required=False, allow_blank=True)
    protocol = serializers.CharField(required=False, allow_blank=True)
    resolution_steps = serializers.ListField(
        required=False
    )
    error = serializers.CharField(required=False, allow_blank=True)