from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    DnsResolveSerializer,
    DnsPoisonSerializer,
    DnsResponseSerializer,
    DnsResetResponseSerializer
)
from .services.fake_dns_resolver import fake_dns_resolver


@api_view(['POST'])
def resolve_dns(request):
    """
    Résout un domaine de manière normale.
    
    POST /api/dns-poisoning/resolve/
    Payload: {"domain": "www.banque-demo.test"}
    """
    serializer = DnsResolveSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                "success": False,
                "error": "Données invalides",
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    domain = serializer.validated_data['domain']
    result = fake_dns_resolver.resolve(domain)
    
    if result['success']:
        response_serializer = DnsResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def simulate_poisoning(request):
    """
    Simule un empoisonnement DNS.
    
    POST /api/dns-poisoning/poison/
    Payload: {"domain": "www.banque-demo.test", "falsified_ip": "192.168.1.99"}
    """
    serializer = DnsPoisonSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                "success": False,
                "error": "Données invalides",
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    domain = serializer.validated_data['domain']
    falsified_ip = serializer.validated_data['falsified_ip']
    result = fake_dns_resolver.simulate_poisoning(domain, falsified_ip)
    
    if result['success']:
        response_serializer = DnsResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def reset_cache(request):
    """
    Réinitialise le cache DNS simulé.
    
    POST /api/dns-poisoning/reset/
    Payload: {}
    """
    result = fake_dns_resolver.reset_cache()
    response_serializer = DnsResetResponseSerializer(result)
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_fake_domains(request):
    """
    Retourne la liste des domaines fictifs disponibles.
    
    GET /api/dns-poisoning/domains/
    """
    domains = fake_dns_resolver.get_all_fake_domains()
    return Response({
        "success": True,
        "domains": domains
    }, status=status.HTTP_200_OK)

# Create your views here.
