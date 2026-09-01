import React from 'react';
import { Clock, MapPin, CheckCircle2, XCircle, Trash2, AlertCircle } from 'lucide-react';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import IconButton from '../components/ui/IconButton';
import { useHistory } from '../contexts/HistoryContext';

const HistoryPage = () => {
  const { history, clearHistory } = useHistory();

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <section className="flex items-start gap-4">
        <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center flex-shrink-0">
          <Clock className="w-6 h-6 text-primary-600" />
        </div>
        <div className="flex-1">
          <h1 className="text-3xl sm:text-4xl font-bold text-secondary-900 mb-2">Historique</h1>
          <p className="text-lg text-secondary-600">
            Consultez l'historique de vos résolutions DNS lors de cette session.
          </p>
        </div>
        {history.length > 0 && (
          <Button
            variant="outline"
            icon={Trash2}
            iconPosition="left"
            onClick={clearHistory}
          >
            Effacer
          </Button>
        )}
      </section>

      {/* Empty State */}
      {history.length === 0 && (
        <Card variant="default" padding="xl">
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto bg-secondary-100 rounded-full flex items-center justify-center mb-4">
              <Clock className="w-8 h-8 text-secondary-400" />
            </div>
            <h3 className="text-xl font-semibold text-secondary-900 mb-2">Aucune résolution</h3>
            <p className="text-secondary-600">
              Effectuez une résolution DNS pour voir l'historique s'afficher ici.
            </p>
          </div>
        </Card>
      )}

      {/* History List */}
      {history.length > 0 && (
        <div className="space-y-4">
          {history.map((item, index) => (
            <Card key={index} variant="elevated" padding="md">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-secondary-900 text-lg">{item.domain}</h3>
                    <span className={`flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full ${
                      item.status === 'success' 
                        ? 'bg-success-100 text-success-700' 
                        : 'bg-danger-100 text-danger-700'
                    }`}>
                      {item.status === 'success' ? (
                        <CheckCircle2 className="w-3 h-3" />
                      ) : (
                        <XCircle className="w-3 h-3" />
                      )}
                      {item.status === 'success' ? 'Succès' : 'Échec'}
                    </span>
                  </div>
                  
                  <div className="flex flex-wrap gap-4 text-sm">
                    <div className="flex items-center gap-2 text-secondary-600">
                      <MapPin className="w-4 h-4" />
                      <span className="font-medium">{item.ip}</span>
                    </div>
                    <div className="flex items-center gap-2 text-secondary-600">
                      <Clock className="w-4 h-4" />
                      <span>{item.time} s</span>
                    </div>
                    <div className="flex items-center gap-2 text-secondary-600">
                      <span className="text-xs text-secondary-500">{formatDate(item.timestamp)}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <div className="text-right text-sm text-secondary-500">
                    <div className="text-xs">Étapes</div>
                    <div className="font-medium text-secondary-900">{item.steps}</div>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Info Card */}
      {history.length > 0 && (
        <Card variant="flat" padding="md">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <AlertCircle className="w-4 h-4 text-primary-600" />
            </div>
            <div className="text-sm text-secondary-600">
              <span className="font-medium text-secondary-900">Note :</span> L'historique est stocké uniquement en mémoire pour cette session. Il sera effacé lorsque vous fermerez l'application.
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default HistoryPage;
