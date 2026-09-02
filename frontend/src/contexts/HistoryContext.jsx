import React, { createContext, useContext, useState } from 'react';

const HistoryContext = createContext();

export const useHistory = () => {
  const context = useContext(HistoryContext);

  if (!context) {
    throw new Error('useHistory must be used within a HistoryProvider');
  }

  return context;
};

export const HistoryProvider = ({ children }) => {
  const [history, setHistory] = useState(() => {
    try {
      const savedHistory = localStorage.getItem('dns_history');
      return savedHistory ? JSON.parse(savedHistory) : [];
    } catch (error) {
      console.error('Erreur lors du chargement de l\'historique :', error);
      return [];
    }
  });

  const addToHistory = (resolution) => {
    setHistory((prev) => {
      const updatedHistory = [resolution, ...prev].slice(0, 50);

      localStorage.setItem(
        'dns_history',
        JSON.stringify(updatedHistory)
      );

      return updatedHistory;
    });
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem('dns_history');
  };

  return (
    <HistoryContext.Provider
      value={{ history, addToHistory, clearHistory }}
    >
      {children}
    </HistoryContext.Provider>
  );
};

export default HistoryContext;