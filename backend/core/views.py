from django.http import JsonResponse
from django.shortcuts import render


def health_check(request):
    return JsonResponse({
        "status": "success",
        "message": "Backend DNS Security Simulator is running",
        "version": "1.0.0"
    })
