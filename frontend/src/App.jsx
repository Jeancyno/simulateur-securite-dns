import React from 'react';
import AppLayout from './components/layout/AppLayout';
import { HistoryProvider } from './contexts/HistoryContext';

function App() {
  return (
    <HistoryProvider>
      <AppLayout />
    </HistoryProvider>
  );
}

export default App;
