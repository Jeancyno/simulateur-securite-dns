import apiService from './api.js';

// Service dédié à la résolution DNS normale
const dnsService = {

  // Résoudre un nom de domaine
  async resolveDomain(domain) {
    try {
      const response = await apiService.post(
        '/api/dns/resolve/',
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

  // Valider le format d'un nom de domaine
  isValidDomain(domain) {
    if (typeof domain !== 'string') {
      return false;
    }

    const value = domain.trim();

    if (!value || value.length > 253) {
      return false;
    }

    const domainRegex =
      /^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/;

    return domainRegex.test(value);
  },
};

export default dnsService;