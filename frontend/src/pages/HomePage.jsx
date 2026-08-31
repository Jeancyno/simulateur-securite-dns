import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

const HomePage = () => {
  const [backendStatus, setBackendStatus] = useState('loading');
  const [backendMessage, setBackendMessage] = useState('');

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await apiService.healthCheck();
        setBackendStatus('connected');
        setBackendMessage(response.message);
      } catch (error) {
        setBackendStatus('disconnected');
        setBackendMessage('Impossible de se connecter au backend');
      }
    };

    checkBackend();
  }, []);

  const getStatusColor = () => {
    switch (backendStatus) {
      case 'connected': return '#10b981';
      case 'disconnected': return '#ef4444';
      default: return '#f59e0b';
    }
  };

  const getStatusText = () => {
    switch (backendStatus) {
      case 'connected': return '✅ Backend connecté';
      case 'disconnected': return '❌ Backend déconnecté';
      default: return '⏳ Vérification du backend...';
    }
  };

  return (
    <div className="home-page">
      <div className="container">
        <h1>Simulateur de Sécurité DNS</h1>
        <p>Application de simulation et d'apprentissage des attaques DNS et des mécanismes de sécurité</p>
        
        <div className="status">
          <h2>Statut du système</h2>
          <p>✅ Frontend React fonctionnel</p>
          <p style={{ color: getStatusColor() }}>{getStatusText()}</p>
          {backendMessage && <p className="backend-message">{backendMessage}</p>}
        </div>
        
        <div className="features">
          <h3>Modules disponibles :</h3>
          <ul>
            <li>🔍 Simulation DNS</li>
            <li>🔒 DNSSEC</li>
            <li>🛡️ DNS over HTTPS (DoH)</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
