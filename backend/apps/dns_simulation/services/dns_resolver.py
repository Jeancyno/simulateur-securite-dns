"""
Service de résolution DNS simulée pour la pédagogie.
Ce service génère les étapes de résolution DNS sans effectuer de requêtes réelles.
"""

import random
import logging
from datetime import datetime

logger = logging.getLogger("dns_simulator")
# Données fictives des domaines et leurs IP
SIMULATION_DOMAINS = {
    "example.test": "93.184.216.34",
    "www.banque-demo.test": "192.168.1.10",
    "www.exemple.test": "192.168.1.20",
    "www.dns-demo.test": "192.168.1.30",
    "www.secure-demo.test": "192.168.1.40",
    "www.corp-demo.test": "192.168.1.50",
    "google.test": "142.250.185.78",
    "facebook.test": "157.240.241.35",
    "amazon.test": "176.32.98.85",
}


class DnsResolver:
    """Résolveur DNS simulé pour la pédagogie"""
    
    def __init__(self):
        self.simulation_domains = SIMULATION_DOMAINS
    
    def is_domain_valid(self, domain: str) -> bool:
        """Valide le format d'un domaine"""
        if not domain or not isinstance(domain, str):
            return False
        
        if len(domain) > 253:
            return False
        
        # Validation basique du format de domaine
        parts = domain.split('.')
        if len(parts) < 2:
            return False
        
        for part in parts:
            if not part:
                return False
            if not part.replace('-', '').isalnum():
                return False
            if part.startswith('-') or part.endswith('-'):
                return False
        
        return True
    
    def is_domain_known(self, domain: str) -> bool:
        """Vérifie si le domaine est connu dans la simulation"""
        return domain in self.simulation_domains
    
    def get_domain_ip(self, domain: str) -> str:
        """Récupère l'IP d'un domaine connu"""
        if not self.is_domain_known(domain):
            # Générer une IP cohérente pour les domaines inconnus
            return self._generate_mock_ip(domain)
        return self.simulation_domains[domain]
    
    def _generate_mock_ip(self, domain: str) -> str:
        """Génère une IP fictive cohérente basée sur le domaine"""
        # Hash simple du domaine pour générer une IP consistante
        hash_value = hash(domain)
        octets = []
        for i in range(4):
            octet = abs((hash_value >> (i * 8))) % 254 + 1
            octets.append(str(octet))
        return '.'.join(octets)
    
    def resolve(self, domain: str) -> dict:
        """
        Résout un domaine et génère les étapes de résolution.
        
        Retourne le format attendu par le Frontend:
        {
            "domain": "example.test",
            "ip": "93.184.216.34",
            "time": "1.25",
            "steps": 6,
            "status": "success",
            "timestamp": "2024-09-01T12:00:00Z",
            "requestType": "A",
            "protocol": "UDP"
        }
        """
        if not self.is_domain_valid(domain):
            logger.warning(
                "Résolution DNS refusée - domaine invalide : %s",
                domain
            )
            return {
                "success": False,
                "error": "Format de domaine invalide"
            }
        
        # Générer un temps de résolution réaliste (entre 50ms et 200ms)
        resolution_time_ms = random.randint(50, 200)
        resolution_time_s = round(resolution_time_ms / 1000, 2)
        
        # Récupérer l'IP
        ip = self.get_domain_ip(domain)
        
        # Générer les étapes de résolution
        resolution_steps = self._generate_resolution_steps(domain, ip)
        logger.info(
            "Résolution DNS réussie - domaine=%s, ip=%s, temps=%ss",
            domain,
            ip,
            resolution_time_s
        )
        return {
            "success": True,
            "domain": domain,
            "ip": ip,
            "time": str(resolution_time_s),
            "steps": len(resolution_steps),
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "requestType": "A",
            "protocol": "UDP",
            "resolution_steps": resolution_steps
        }
    
    def _generate_resolution_steps(self, domain: str, ip: str) -> list:
        """
        Génère les étapes de résolution DNS.
        
        Retourne une liste d'étapes correspondant au parcours DNS:
        1. Utilisateur
        2. Résolveur DNS
        3. Serveur Racine
        4. Serveur TLD
        5. Serveur Autoritaire
        6. Adresse IP
        """
        tld = domain.split('.')[-1] if '.' in domain else 'test'
        
        steps = [
            {
                "id": 1,
                "name": "Utilisateur",
                "description": "Requête initiée",
                "details": f"Votre appareil demande l'adresse IP de {domain}"
            },
            {
                "id": 2,
                "name": "Résolveur DNS",
                "description": "Cache vérifié",
                "details": "Le résolveur vérifie son cache local avant de contacter d'autres serveurs"
            },
            {
                "id": 3,
                "name": "Serveur Racine",
                "description": "Redirection vers TLD",
                "details": f"Le serveur racine dirige vers le serveur TLD .{tld}"
            },
            {
                "id": 4,
                "name": "Serveur TLD",
                "description": "Redirection vers autoritaire",
                "details": f"Le serveur TLD .{tld} dirige vers le serveur autoritaire"
            },
            {
                "id": 5,
                "name": "Serveur Autoritaire",
                "description": "Adresse IP fournie",
                "details": f"Le serveur autoritaire fournit l'adresse IP {ip}"
            },
            {
                "id": 6,
                "name": "Adresse IP",
                "description": "Résolution terminée",
                "details": f"L'adresse IP {ip} est retournée à votre appareil"
            }
        ]
        
        return steps
    
    def get_available_domains(self) -> list:
        """Retourne la liste des domaines disponibles dans la simulation"""
        return list(self.simulation_domains.keys())


# Instance singleton du résolveur DNS
dns_resolver = DnsResolver()
