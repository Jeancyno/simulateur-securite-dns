from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DnssecVerifySerializer, DnssecResponseSerializer
from .services.dnssec_validator import dnssec_validator


class DnssecVerifyView(APIView):
    """
    API de vérification DNSSEC.

    POST /api/dnssec/verify/
    """

    def post(self, request):
        serializer = DnssecVerifySerializer(data=request.data)

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

        result = dnssec_validator.verify_dnssec(domain)

        if not result.get("success"):
            response_serializer = DnssecResponseSerializer(data=result)

            if response_serializer.is_valid():
                return Response(
                    response_serializer.validated_data,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = DnssecResponseSerializer(data=result)

        if not response_serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "error": "Réponse DNSSEC invalide.",
                    "details": response_serializer.errors,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            response_serializer.validated_data,
            status=status.HTTP_200_OK,
        )
