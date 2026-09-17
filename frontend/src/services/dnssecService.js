import apiService from './api.js';

// Service dédié à la validation DNSSEC
const dnssecService = {

  // Vérifier la validation DNSSEC d'un domaine
  async verifyDnssec(domain) {
    try {
      const response = await apiService.post(
        '/api/dnssec/verify/',
        {
          domain,
        }
      );

      return response;
    } catch (error) {
      console.error('DNSSEC Verification Error:', error);
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

export default dnssecService;
