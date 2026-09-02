import React, { useState } from 'react';
import { Globe, User, Server, Network, Shield, MapPin, Clock, FileText, ChevronRight, ChevronDown, CheckCircle2, AlertCircle, Zap, Info } from 'lucide-react';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import IconButton from '../components/ui/IconButton';
import dnsService from '../services/dnsService';
import { useHistory } from '../contexts/HistoryContext';

const DnsResolutionPage = () => {
  const [domain, setDomain] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [animationComplete, setAnimationComplete] = useState(false);
  const [showDetails, setShowDetails] = useState(true);
  const { addToHistory } = useHistory();

  const steps = [
    { id: 1, name: 'Utilisateur', icon: User, description: 'Requête initiée' },
    { id: 2, name: 'Résolveur DNS', icon: Server, description: 'Cache vérifié' },
    { id: 3, name: 'Serveur Racine', icon: Globe, description: 'Redirection vers TLD' },
    { id: 4, name: 'Serveur TLD', icon: Network, description: 'Redirection vers autoritaire' },
    { id: 5, name: 'Serveur Autoritaire', icon: Shield, description: 'Adresse IP fournie' },
    { id: 6, name: 'Adresse IP', icon: MapPin, description: 'Résolution terminée' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setCurrentStep(0);
    setAnimationComplete(false);

    if (!domain.trim()) {
      setError('Veuillez entrer un nom de domaine');
      return;
    }

    if (!dnsService.isValidDomain(domain)) {
      setError('Format de domaine invalide');
      return;
    }

    setLoading(true);

    try {
      await animateSteps();
      const resolution = await dnsService.resolveDomain(domain);
      setResult(resolution);
      addToHistory(resolution);
    } catch (err) {
      setError('Erreur lors de la résolution DNS');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const animateSteps = async () => {
    for (let i = 0; i < steps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 500));
      setCurrentStep(i + 1);
    }
    await new Promise(resolve => setTimeout(resolve, 300));
    setAnimationComplete(true);
  };

    const getStepStatus = (stepId) => {
      if (animationComplete || stepId <= currentStep) {
        return 'completed';
      }

      if (stepId === currentStep + 1) {
        return 'active';
      }

      return 'inactive';
    };
    
  const StepCard = ({ step, status }) => {
    const Icon = step.icon;
    const statusStyles = {
      completed: 'bg-emerald-50 border-emerald-300 shadow-lg shadow-emerald-100/50',
      active: 'bg-blue-50 border-blue-400 shadow-xl shadow-blue-200/50 ring-2 ring-blue-300 ring-offset-2',
      inactive: 'bg-white border-gray-200 opacity-50 hover:opacity-75 transition-opacity'
    };

    const iconStyles = {
      completed: 'text-emerald-600',
      active: 'text-blue-600',
      inactive: 'text-gray-400'
    };

    return (
      <div 
        className={`flex flex-col items-center p-4 rounded-xl border-2 transition-all duration-500 min-w-[120px] ${statusStyles[status]}`}
      >
        <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-all duration-500 ${
          status === 'active' ? 'scale-110 bg-blue-100' : 
          status === 'completed' ? 'bg-emerald-100' : 'bg-gray-50'
        }`}>
          {status === 'completed' ? (
            <CheckCircle2 className="w-6 h-6 text-emerald-600" />
          ) : (
            <Icon className={`w-6 h-6 transition-all duration-300 ${iconStyles[status]}`} />
          )}
        </div>
        <div className="text-center">
          <h4 className="font-semibold text-sm text-gray-900 mb-0.5">{step.name}</h4>
          <p className="text-xs text-gray-500">{step.description}</p>
          {status === 'active' && (
            <span className="inline-block mt-1.5 px-2 py-0.5 bg-blue-100 text-blue-700 text-[10px] font-medium rounded-full animate-pulse">
              En cours
            </span>
          )}
          {status === 'completed' && (
            <span className="inline-block mt-1.5 px-2 py-0.5 bg-emerald-100 text-emerald-700 text-[10px] font-medium rounded-full">
              ✓ Terminé
            </span>
          )}
        </div>
      </div>
    );
  };

  const educationalContent = [
    {
      id: 1,
      icon: User,
      title: '1. Utilisateur',
      description: 'Votre appareil initie une requête DNS pour convertir un nom de domaine en adresse IP.',
    },
    {
      id: 2,
      icon: Server,
      title: '2. Résolveur DNS',
      description: 'Le résolveur de votre FAI vérifie d\'abord son cache local avant de contacter d\'autres serveurs.',
    },
    {
      id: 3,
      icon: Globe,
      title: '3. Serveur Racine',
      description: 'Si le cache est vide, le résolveur contacte l\'un des 13 serveurs racine mondiaux.',
    },
    {
      id: 4,
      icon: Network,
      title: '4. Serveur TLD',
      description: 'Le serveur racine dirige vers le serveur du TLD (Top-Level Domain) comme .com ou .fr.',
    },
    {
      id: 5,
      icon: Shield,
      title: '5. Serveur Autoritaire',
      description: 'Le serveur TLD dirige vers le serveur autoritaire qui connaît l\'adresse IP exacte.',
    },
    {
      id: 6,
      icon: MapPin,
      title: '6. Adresse IP',
      description: 'L\'adresse IP est retournée à votre appareil qui peut alors établir la connexion.',
    },
  ];

  // Rendu des étapes avec des éléments wrapper pour éviter les Fragments
  const renderSteps = () => {
    const elements = [];
    steps.forEach((step, index) => {
      elements.push(
        <StepCard key={`step-${step.id}`} step={step} status={getStepStatus(step.id)} />
      );
      if (index < steps.length - 1) {
        elements.push(
          <div 
            key={`arrow-${step.id}`}
            className={`flex-shrink-0 transition-all duration-500 ${
              index < currentStep ? 'text-emerald-400' : 'text-gray-300'
            }`}
          >
            <ChevronRight className="w-5 h-5" />
          </div>
        );
      }
    });
    return elements;
  };

  const renderMobileSteps = () => {
    const elements = [];
    steps.forEach((step, index) => {
      elements.push(
        <StepCard key={`step-${step.id}`} step={step} status={getStepStatus(step.id)} />
      );
      if (index < steps.length - 1) {
        elements.push(
          <div 
            key={`arrow-down-${step.id}`}
            className={`flex justify-center transition-all duration-500 ${
              index < currentStep ? 'text-emerald-400' : 'text-gray-300'
            }`}
          >
            <ChevronDown className="w-5 h-5" />
          </div>
        );
      }
    });
    return elements;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Header */}
      <div className="flex items-start gap-5">
        <div className="w-14 h-14 bg-gradient-to-br from-blue-100 to-blue-200 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md shadow-blue-200/50">
          <Globe className="w-7 h-7 text-blue-600" />
        </div>
        <div>
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2 tracking-tight">
            Résolution DNS
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl">
            Visualisez le parcours complet d'une requête DNS à travers la hiérarchie des serveurs.
          </p>
        </div>
      </div>

      {/* Search Form */}
      <div>
        <div className="bg-white rounded-2xl shadow-lg shadow-gray-100/70 border border-gray-100 p-6 transition-all hover:shadow-xl hover:shadow-gray-200/50">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="domain" className="block text-sm font-semibold text-gray-700 mb-2">
                Nom de domaine
              </label>
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Globe className="w-4 h-4 text-gray-400" />
                  </div>
                  <input
                    id="domain"
                    type="text"
                    placeholder="exemple.com"
                    value={domain}
                    onChange={(e) => setDomain(e.target.value)}
                    disabled={loading}
                    className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white transition-all disabled:opacity-50 disabled:cursor-not-allowed text-gray-900 placeholder-gray-400"
                  />
                </div>
                <Button
                  type="submit"
                  size="lg"
                  disabled={loading}
                  className="sm:flex-shrink-0"
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Résolution...
                    </span>
                  ) : (
                    'Lancer la résolution'
                  )}
                </Button>
              </div>
            </div>
            {error && (
              <div className="flex items-center gap-3 text-red-600 bg-red-50/80 px-4 py-3 rounded-xl border border-red-200/50">
                <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <AlertCircle className="w-4 h-4 text-red-600" />
                </div>
                <span className="text-sm font-medium">{error}</span>
              </div>
            )}
          </form>
        </div>
      </div>

      {/* DNS Path Visualization */}
      {(loading || result) && (
        <div>
          <div className="flex items-center gap-3 mb-5">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center">
              <Zap className="w-4 h-4 text-blue-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Parcours de résolution</h2>
            <span className="text-xs text-gray-400 font-medium bg-gray-100 px-2.5 py-0.5 rounded-full">
              {currentStep}/{steps.length}
            </span>
          </div>
          
          <div className="bg-white rounded-2xl shadow-lg shadow-gray-100/70 border border-gray-100 p-6">
            {/* Desktop: Horizontal layout */}
            <div className="hidden lg:flex items-center gap-3 overflow-x-auto pb-2">
              {renderSteps()}
            </div>

            {/* Mobile/Tablet: Vertical layout */}
            <div className="lg:hidden space-y-3">
              {renderMobileSteps()}
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {result && animationComplete && (
        <div>
          <div className="flex items-center gap-3 mb-5">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-100 to-emerald-200 rounded-xl flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Résultat</h2>
          </div>
          
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-2xl p-5 border border-blue-200/50 shadow-sm">
              <div className="flex items-center gap-2 text-blue-600 mb-2">
                <MapPin className="w-4 h-4" />
                <span className="text-xs font-semibold uppercase tracking-wide">Adresse IP</span>
              </div>
              <div className="text-2xl font-bold text-gray-900 font-mono">{result.ip}</div>
            </div>
            
            <div className="bg-gradient-to-br from-indigo-50 to-indigo-100/50 rounded-2xl p-5 border border-indigo-200/50 shadow-sm">
              <div className="flex items-center gap-2 text-indigo-600 mb-2">
                <Clock className="w-4 h-4" />
                <span className="text-xs font-semibold uppercase tracking-wide">Temps</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">{result.time} <span className="text-sm font-normal text-gray-500">s</span></div>
            </div>
            
            <div className="bg-gradient-to-br from-amber-50 to-amber-100/50 rounded-2xl p-5 border border-amber-200/50 shadow-sm">
              <div className="flex items-center gap-2 text-amber-600 mb-2">
                <Zap className="w-4 h-4" />
                <span className="text-xs font-semibold uppercase tracking-wide">Étapes</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">{result.steps}</div>
            </div>
            
            <div className="bg-gradient-to-br from-emerald-50 to-emerald-100/50 rounded-2xl p-5 border border-emerald-200/50 shadow-sm">
              <div className="flex items-center gap-2 text-emerald-600 mb-2">
                <CheckCircle2 className="w-4 h-4" />
                <span className="text-xs font-semibold uppercase tracking-wide">Statut</span>
              </div>
              <div className="text-2xl font-bold text-emerald-600">✓ Succès</div>
            </div>
          </div>
        </div>
      )}

      {/* Technical Details */}
      {result && (
        <div>
          <div className="bg-white rounded-2xl shadow-lg shadow-gray-100/70 border border-gray-100 overflow-hidden transition-all">
                  <button
              onClick={() => setShowDetails(!showDetails)}
              className="flex items-center justify-between w-full p-5 hover:bg-gray-50/80 transition-colors"
              type="button"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-100 to-purple-200 rounded-xl flex items-center justify-center">
                  <FileText className="w-4 h-4 text-purple-600" />
                </div>

                <h3 className="font-semibold text-gray-900">
                  Détails techniques
                </h3>

                <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                  {showDetails ? 'Masquer' : 'Afficher'}
                </span>
              </div>

              {showDetails ? (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronRight className="w-5 h-5 text-gray-400" />
              )}
            </button>
            
            {showDetails && (
              <div className="px-5 pb-5 pt-3 border-t border-gray-100">
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="bg-gray-50/70 rounded-xl p-4">
                    <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Horodatage</div>
                    <div className="text-sm font-medium text-gray-900">
                      {new Date(result.timestamp).toLocaleString('fr-FR')}
                    </div>
                  </div>
                  <div className="bg-gray-50/70 rounded-xl p-4">
                    <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Type de requête</div>
                    <div className="text-sm font-medium text-gray-900">{result.requestType} <span className="text-xs text-gray-400">(IPv4)</span></div>
                  </div>
                  <div className="bg-gray-50/70 rounded-xl p-4">
                    <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Protocole</div>
                    <div className="text-sm font-medium text-gray-900">{result.protocol}</div>
                  </div>
                  <div className="bg-gray-50/70 rounded-xl p-4">
                    <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Domaine</div>
                    <div className="text-sm font-medium text-gray-900 break-all">{result.domain}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Educational Section */}
      <div>
        <div className="flex items-center gap-3 mb-5">
          <div className="w-8 h-8 bg-gradient-to-br from-sky-100 to-sky-200 rounded-xl flex items-center justify-center">
            <Info className="w-4 h-4 text-sky-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-900">Comprendre la résolution DNS</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {educationalContent.map((item) => {
            const Icon = item.icon;
            return (
              <div 
                key={`edu-${item.id}`}
                className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md hover:shadow-gray-100/50 transition-all duration-200 group h-full"
              >
                <div className="space-y-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                    <Icon className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 text-sm mb-1.5">{item.title}</h3>
                    <p className="text-xs text-gray-500 leading-relaxed">{item.description}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

  
      </div>
    </div>
  );
};

export default DnsResolutionPage;