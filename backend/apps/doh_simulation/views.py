from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DohCompareSerializer, DohResponseSerializer
from .services.doh_resolver import doh_resolver


class DohCompareView(APIView):
    """
    API de comparaison DNS vs DNS over HTTPS.

    POST /api/doh/compare/
    """

    def post(self, request):
        serializer = DohCompareSerializer(data=request.data)

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

        result = doh_resolver.compare_dns_vs_doh(domain)

        if not result.get("success"):
            response_serializer = DohResponseSerializer(data=result)

            if response_serializer.is_valid():
                return Response(
                    response_serializer.validated_data,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = DohResponseSerializer(data=result)

        if not response_serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "error": "Réponse DoH invalide.",
                    "details": response_serializer.errors,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            response_serializer.validated_data,
            status=status.HTTP_200_OK,
        )
