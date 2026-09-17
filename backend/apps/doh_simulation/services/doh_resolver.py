"""
Service de résolution DNS over HTTPS utilisant requests.
Ce service effectue des requêtes DoH réelles vers des résolveurs publics.
"""

import logging
import requests
import json
import time
from typing import Dict, Optional

logger = logging.getLogger("dns_simulator")


class DohResolver:
    """Résolveur DNS over HTTPS utilisant des résolveurs publics"""

    # Résolveurs DoH publics
    DOH_RESOLVERS = [
        {
            "name": "Cloudflare",
            "url": "https://cloudflare-dns.com/dns-query",
            "timeout": 5.0
        },
        {
            "name": "Google",
            "url": "https://dns.google/resolve",
            "timeout": 5.0
        }
    ]

    def __init__(self):
        # Import du résolveur DNS classique pour éviter les imports circulaires
        self._dns_resolver = None

    @property
    def dns_resolver(self):
        """Lazy import du résolveur DNS classique"""
        if self._dns_resolver is None:
            from apps.dns_simulation.services.dns_resolver import dns_resolver
            self._dns_resolver = dns_resolver
        return self._dns_resolver

    def is_domain_valid(self, domain: str) -> bool:
        """Valide le format d'un domaine (réutilise le validateur existant)"""
        return self.dns_resolver.is_domain_valid(domain)

    def resolve_doh(self, domain: str) -> Dict:
        """
        Résout un domaine via DNS over HTTPS.

        Retourne:
        {
            "success": True/False,
            "domain": "example.com",
            "response": "93.184.216.34",
            "response_time": "0.123",
            "resolver_used": "Cloudflare",
            "fallback_used": False,
            "error": "message d'erreur" (si échec)
        }
        """
        if not self.is_domain_valid(domain):
            logger.warning(
                "DoH - domaine invalide : %s",
                domain
            )
            return {
                "success": False,
                "error": "Format de domaine invalide"
            }

        # Essayer chaque résolveur DoH
        for resolver in self.DOH_RESOLVERS:
            try:
                logger.info(
                    "DoH - tentative de résolution via %s pour : %s",
                    resolver["name"],
                    domain
                )

                result = self._query_doh_resolver(domain, resolver)

                if result["success"]:
                    logger.info(
                        "DoH - résolution réussie via %s pour %s : %s",
                        resolver["name"],
                        domain,
                        result["response"]
                    )
                    return result

            except requests.exceptions.Timeout:
                logger.warning(
                    "DoH - timeout avec %s pour %s",
                    resolver["name"],
                    domain
                )
                continue
            except requests.exceptions.RequestException as e:
                logger.warning(
                    "DoH - erreur avec %s pour %s : %s",
                    resolver["name"],
                    domain,
                    str(e)
                )
                continue
            except Exception as e:
                logger.error(
                    "DoH - erreur inattendue avec %s pour %s : %s",
                    resolver["name"],
                    domain,
                    str(e)
                )
                continue

        # Si tous les résolveurs ont échoué, utiliser le fallback
        logger.warning(
            "DoH - tous les résolveurs ont échoué pour %s, utilisation du fallback",
            domain
        )
        return self._get_fallback_response(domain)

    def _query_doh_resolver(self, domain: str, resolver: Dict) -> Dict:
        """
        Interroge un résolveur DoH spécifique.

        Utilise le format JSON de l'API Google DoH:
        https://dns.google/resolve
        """
        start_time = time.time()

        try:
            # Paramètres de la requête DoH
            params = {
                "name": domain,
                "type": "A"  # Enregistrement A (IPv4)
            }

            headers = {
                "Accept": "application/dns-json"
            }

            # Effectuer la requête
            response = requests.get(
                resolver["url"],
                params=params,
                headers=headers,
                timeout=resolver["timeout"]
            )

            response_time = time.time() - start_time

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")

            data = response.json()

            # Analyser la réponse
            if data.get("Status") != 0:
                # Status != 0 indique une erreur DNS
                if data.get("Status") == 3:  # NXDOMAIN
                    raise Exception("Le domaine n'existe pas (NXDOMAIN)")
                else:
                    raise Exception(f"Erreur DNS : status {data.get('Status')}")

            # Extraire l'adresse IP de la réponse
            answer = data.get("Answer", [])
            ip_address = None

            for record in answer:
                if record.get("type") == 1:  # Type A = IPv4
                    ip_address = record.get("data")
                    break

            if not ip_address:
                raise Exception("Pas d'adresse IP trouvée dans la réponse")

            return {
                "success": True,
                "domain": domain,
                "response": ip_address,
                "response_time": f"{response_time:.3f}",
                "resolver_used": resolver["name"],
                "fallback_used": False,
                "raw_response": data
            }

        except json.JSONDecodeError as e:
            raise Exception(f"Réponse JSON invalide : {str(e)}")

    def _get_fallback_response(self, domain: str) -> Dict:
        """
        Génère une réponse de fallback simulée.

        Cette méthode est utilisée quand tous les résolveurs DoH réels
        sont indisponibles. Elle indique clairement qu'il s'agit d'un fallback.
        """
        logger.warning(
            "DoH - génération de réponse fallback pour : %s",
            domain
        )

        # Utiliser le résolveur DNS classique existant pour obtenir une IP
        classic_result = self.dns_resolver.resolve(domain)

        if not classic_result.get("success"):
            return {
                "success": False,
                "error": "Résolveurs DoH indisponibles et résolution DNS classique échouée",
                "fallback_used": True
            }

        # Simuler un temps de réponse réaliste pour DoH
        fallback_response_time = "0.050"  # 50ms simulé

        return {
            "success": True,
            "domain": domain,
            "response": classic_result.get("ip"),
            "response_time": fallback_response_time,
            "resolver_used": "Fallback simulé",
            "fallback_used": True,
            "fallback_reason": "Tous les résolveurs DoH publics sont indisponibles",
            "message": "Mode de secours activé - réponse simulée basée sur DNS classique"
        }

    def compare_dns_vs_doh(self, domain: str) -> Dict:
        """
        Compare la résolution DNS classique avec DNS over HTTPS.

        Retourne:
        {
            "success": True/False,
            "domain": "example.com",
            "classic": {
                "protocol": "DNS",
                "transport": "UDP/TCP",
                "encryption": false,
                "privacy": "Limitée",
                "response": "93.184.216.34",
                "response_time": "0.050",
                "resolver": "Résolveur DNS classique",
                "visibility": "Requête observable"
            },
            "doh": {
                "protocol": "DNS over HTTPS",
                "transport": "HTTPS",
                "encryption": true,
                "privacy": "Améliorée",
                "response": "93.184.216.34",
                "response_time": "0.123",
                "resolver": "Cloudflare",
                "visibility": "Requête chiffrée",
                "fallback_used": false
            },
            "error": "message d'erreur" (si échec)
        }
        """
        if not self.is_domain_valid(domain):
            logger.warning(
                "DoH - domaine invalide pour comparaison : %s",
                domain
            )
            return {
                "success": False,
                "error": "Format de domaine invalide"
            }

        try:
            logger.info(
                "DoH - début comparaison DNS vs DoH pour : %s",
                domain
            )

            # 1. Résolution DNS classique (réutiliser le service existant)
            classic_result = self.dns_resolver.resolve(domain)

            if not classic_result.get("success"):
                return {
                    "success": False,
                    "error": f"Résolution DNS classique échouée : {classic_result.get('error', 'Erreur inconnue')}"
                }

            # 2. Résolution DoH
            doh_result = self.resolve_doh(domain)

            if not doh_result.get("success"):
                return {
                    "success": False,
                    "error": f"Résolution DoH échouée : {doh_result.get('error', 'Erreur inconnue')}"
                }

            # 3. Construire la réponse de comparaison
            comparison = {
                "success": True,
                "domain": domain,
                "classic": {
                    "protocol": "DNS",
                    "transport": "UDP/TCP",
                    "encryption": False,
                    "privacy": "Limitée",
                    "response": classic_result.get("ip"),
                    "response_time": classic_result.get("time"),
                    "resolver": "Résolveur DNS classique",
                    "visibility": "Requête plus directement observable"
                },
                "doh": {
                    "protocol": "DNS over HTTPS",
                    "transport": "HTTPS",
                    "encryption": True,
                    "privacy": "Améliorée",
                    "response": doh_result.get("response"),
                    "response_time": doh_result.get("response_time"),
                    "resolver": doh_result.get("resolver_used"),
                    "visibility": "Requête transportée dans un canal HTTPS chiffré",
                    "fallback_used": doh_result.get("fallback_used", False)
                }
            }

            # Ajouter un message si le fallback a été utilisé
            if doh_result.get("fallback_used"):
                comparison["doh"]["fallback_reason"] = doh_result.get("fallback_reason")
                comparison["doh"]["message"] = doh_result.get("message")

            logger.info(
                "DoH - comparaison réussie pour %s : classique=%s, doh=%s, fallback=%s",
                domain,
                comparison["classic"]["response"],
                comparison["doh"]["response"],
                comparison["doh"]["fallback_used"]
            )

            return comparison

        except Exception as e:
            logger.error(
                "DoH - erreur lors de la comparaison pour %s : %s",
                domain,
                str(e)
            )
            return {
                "success": False,
                "error": f"Erreur lors de la comparaison : {str(e)}"
            }


# Instance singleton du résolveur DoH
doh_resolver = DohResolver()
