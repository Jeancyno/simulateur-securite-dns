import apiService from './api.js';

// Service dédié à la simulation d'empoisonnement DNS
const dnsPoisoningService = {

  // Résolution DNS dans le contexte de la simulation
  async resolveDns(domain) {
    try {
      const response = await apiService.post(
        '/api/dns-poisoning/resolve/',
        {
          domain,
        }
      );

      return response;
    } catch (error) {
      console.error('DNS Resolution Error:', error);
      throw error;
    }
  },

  // Simulation de l'empoisonnement DNS
  async simulateDnsPoisoning(domain, falsifiedIp) {
    try {
      const response = await apiService.post(
        '/api/dns-poisoning/poison/',
        {
          domain,
          falsified_ip: falsifiedIp,
        }
      );

      return response;
    } catch (error) {
      console.error('DNS Poisoning Error:', error);
      throw error;
    }
  },

  // Réinitialisation du cache DNS simulé
  async resetDnsSimulation() {
    try {
      const response = await apiService.post(
        '/api/dns-poisoning/reset/',
        {}
      );

      return response;
    } catch (error) {
      console.error('DNS Reset Error:', error);
      throw error;
    }
  },

  // Récupération des domaines disponibles
  async getFakeDomains() {
    try {
      const response = await apiService.get(
        '/api/dns-poisoning/domains/'
      );

      return response;
    } catch (error) {
      console.error('Get Domains Error:', error);
      throw error;
    }
  },

  // Validation du format d'un domaine
  isValidDomain(domain) {
    const domainRegex =
      /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](\.[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9])*$/;

    return domainRegex.test(domain) && domain.length <= 253;
  },

  // Validation du format d'une adresse IPv4
  isValidIp(ip) {
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;

    if (!ipRegex.test(ip)) {
      return false;
    }

    const parts = ip.split('.');

    return parts.every((part) => {
      const num = parseInt(part, 10);
      return num >= 0 && num <= 255;
    });
  },
};

export default dnsPoisoningService;