// Mock DNS service for simulation
export const dnsService = {
  // Mock DNS resolution
  async resolveDomain(domain) {
    return new Promise((resolve) => {
      // Simulate realistic DNS resolution timing
      const baseTime = 2000;
      const randomVariation = Math.random() * 1000;
      const totalTime = baseTime + randomVariation;

      setTimeout(() => {
        // Generate mock IP address based on domain
        const mockIP = this.generateMockIP(domain);
        
        resolve({
          domain: domain,
          ip: mockIP,
          time: (totalTime / 1000).toFixed(2),
          steps: 6,
          status: 'success',
          timestamp: new Date().toISOString(),
          requestType: 'A',
          protocol: 'UDP'
        });
      }, totalTime);
    });
  },

  // Generate consistent mock IP based on domain
  generateMockIP(domain) {
    // Simple hash function to generate consistent IPs
    let hash = 0;
    for (let i = 0; i < domain.length; i++) {
      hash = ((hash << 5) - hash) + domain.charCodeAt(i);
      hash = hash & hash;
    }
    
    // Generate IP from hash
    const octet1 = Math.abs(hash % 255) + 1;
    const octet2 = Math.abs((hash >> 8) % 255) + 1;
    const octet3 = Math.abs((hash >> 16) % 255) + 1;
    const octet4 = Math.abs((hash >> 24) % 255) + 1;
    
    return `${octet1}.${octet2}.${octet3}.${octet4}`;
  },

  // Validate domain format
  isValidDomain(domain) {
    const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\.[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9])*$/;
    return domainRegex.test(domain) && domain.length <= 253;
  }
};

export default dnsService;
