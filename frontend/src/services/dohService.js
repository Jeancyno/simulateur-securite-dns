import apiService from './api.js';

// Service dédié à la comparaison DNS vs DNS over HTTPS
const dohService = {

  // Comparer DNS classique et DNS over HTTPS
  async compareDnsVsDoh(domain) {
    try {
      const response = await apiService.post(
        '/api/doh/compare/',
        {
          domain,
        }
      );

      return response;
    } catch (error) {
      console.error('DoH Comparison Error:', error);
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

export default dohService;
