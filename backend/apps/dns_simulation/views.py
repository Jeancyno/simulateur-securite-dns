from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DnsResolveSerializer, DnsResponseSerializer
from .services.dns_resolver import dns_resolver


class DnsResolveView(APIView):
    """
    API de résolution DNS normale simulée.

    POST /api/dns/resolve/
    """

    def post(self, request):
        serializer = DnsResolveSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "error": "Données invalides.",
                    "details": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        domain = serializer.validated_data["domain"].strip()

        result = dns_resolver.resolve(domain)

        if not result.get("success"):
            response_serializer = DnsResponseSerializer(data=result)

            if response_serializer.is_valid():
                return Response(
                    response_serializer.validated_data,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = DnsResponseSerializer(data=result)

        if not response_serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "error": "Réponse DNS invalide.",
                    "details": response_serializer.errors,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            response_serializer.validated_data,
            status=status.HTTP_200_OK,
        )