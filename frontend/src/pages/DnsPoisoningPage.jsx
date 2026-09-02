import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  ShieldCheck,
  Server,
  Globe,
  RotateCcw,
  ArrowRight,
  Lock,
  Info,
  Zap,
  Network,
  Database,
  Key,
} from 'lucide-react';

import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import dnsPoisoningService from '../services/dnsPoisoningService.js';

const DnsPoisoningPage = () => {
  const [domain, setDomain] = useState('www.banque-demo.test');
  const [falsifiedIp, setFalsifiedIp] = useState('192.168.1.99');
  const [isPoisoned, setIsPoisoned] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isResolving, setIsResolving] = useState(false);
  const [resolveResult, setResolveResult] = useState(null);
  const [poisonResult, setPoisonResult] = useState(null);
  const [error, setError] = useState(null);
  const [availableDomains, setAvailableDomains] = useState([]);

  // Load available domains on mount
  useEffect(() => {
    loadAvailableDomains();
  }, []);

  const loadAvailableDomains = async () => {
    try {
      const response = await dnsPoisoningService.getFakeDomains();
      if (response.success && response.domains.length > 0) {
        setAvailableDomains(response.domains);
        setDomain(response.domains[0]);
      }
    } catch (err) {
      console.error('Failed to load domains:', err);
    }
  };

  const handleResolve = async () => {
    if (!domain.trim()) return;
    
    setIsResolving(true);
    setError(null);
    setResolveResult(null);
    
    try {
      const result = await dnsPoisoningService.resolveDns(domain);
      if (result.success) {
        setResolveResult(result);
        setIsPoisoned(result.cache_status === 'POISONED');
      } else {
        setError(result.error || 'Erreur lors de la résolution DNS');
      }
    } catch (err) {
      setError('Erreur de connexion au serveur');
      console.error('Resolve error:', err);
    } finally {
      setIsResolving(false);
    }
  };

  const handleAttack = async () => {
    if (!domain.trim() || !falsifiedIp.trim()) return;
    
    setIsSimulating(true);
    setError(null);
    setPoisonResult(null);
    
    try {
      const result = await dnsPoisoningService.simulateDnsPoisoning(domain, falsifiedIp);
      if (result.success) {
        setPoisonResult(result);
        setIsPoisoned(true);
        // Also update resolve result to show the poisoned state
        setResolveResult(result);
      } else {
        setError(result.error || 'Erreur lors de la simulation d\'empoisonnement');
      }
    } catch (err) {
      setError('Erreur de connexion au serveur');
      console.error('Poison error:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleReset = async () => {
    setIsSimulating(true);
    setError(null);
    
    try {
      const result = await dnsPoisoningService.resetDnsSimulation();
      if (result.success) {
        setIsPoisoned(false);
        setResolveResult(null);
        setPoisonResult(null);
      } else {
        setError('Erreur lors de la réinitialisation');
      }
    } catch (err) {
      setError('Erreur de connexion au serveur');
      console.error('Reset error:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  // Get the legitimate IP from resolve result or default
  const getLegitimateIp = () => {
    if (resolveResult && resolveResult.legitimate_ip) {
      return resolveResult.legitimate_ip;
    }
    return '192.168.1.10'; // Default fallback
  };

  // Get the resolved IP (which may be poisoned)
  const getResolvedIp = () => {
    if (resolveResult && resolveResult.resolved_ip) {
      return resolveResult.resolved_ip;
    }
    return getLegitimateIp();
  };

  return (
    <div className="w-full max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">

      {/* =====================================================
          HEADER
      ====================================================== */}
      <div className="space-y-4">
        <div className="flex items-start gap-5">
          <div className="w-14 h-14 bg-gradient-to-br from-red-100 to-red-200 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md shadow-red-200/50">
            <AlertTriangle className="w-7 h-7 text-red-600" />
          </div>

          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight">
              Empoisonnement DNS
            </h1>

            <p className="mt-1.5 text-lg text-gray-600 max-w-2xl">
              Visualisez comment une réponse DNS falsifiée peut modifier
              le résultat d'une résolution.
            </p>
          </div>
        </div>

        {/* Avertissement simulation */}
        <div className="flex items-start gap-4 rounded-2xl border border-amber-200/60 bg-gradient-to-br from-amber-50 to-amber-100/40 p-5 shadow-sm">
          <div className="w-9 h-9 bg-amber-100 rounded-xl flex items-center justify-center flex-shrink-0">
            <Info className="w-4 h-4 text-amber-600" />
          </div>

          <div>
            <p className="font-semibold text-amber-900">
              Simulation pédagogique
            </p>

            <p className="mt-0.5 text-sm text-amber-800/80">
              Cette interface reproduit un scénario d'empoisonnement DNS
              dans un environnement fictif. Aucune attaque réelle n'est
              effectuée.
            </p>
          </div>
        </div>
      </div>

      {/* =====================================================
          RÉSULTAT DE RÉSOLUTION
      ====================================================== */}
      {resolveResult && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center">
              <Server className="w-4 h-4 text-blue-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">
              Résultat de la résolution
            </h2>
          </div>

          <div className={`bg-white rounded-2xl shadow-lg border p-6 ${
            resolveResult.cache_status === 'POISONED' 
              ? 'border-red-200/60 shadow-red-100/70' 
              : 'border-gray-100 shadow-gray-100/70'
          }`}>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <p className="text-sm text-gray-500 font-medium">Domaine</p>
                <p className="mt-1 font-mono text-lg font-semibold text-gray-900">{resolveResult.domain}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 font-medium">IP résolue</p>
                <p className={`mt-1 font-mono text-lg font-semibold ${
                  resolveResult.cache_status === 'POISONED' ? 'text-red-600' : 'text-emerald-600'
                }`}>{resolveResult.resolved_ip}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 font-medium">IP légitime</p>
                <p className="mt-1 font-mono text-lg font-semibold text-gray-900">{resolveResult.legitimate_ip}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 font-medium">État du cache</p>
                <p className={`mt-1 font-semibold ${
                  resolveResult.cache_status === 'POISONED' ? 'text-red-600' : 'text-emerald-600'
                }`}>{resolveResult.cache_status === 'POISONED' ? '⚠ Empoisonné' : '✓ Sain'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 font-medium">Source</p>
                <p className={`mt-1 font-semibold ${
                  resolveResult.response_source === 'FALSIFIED' ? 'text-red-600' : 'text-emerald-600'
                }`}>{resolveResult.response_source === 'FALSIFIED' ? 'Falsifiée' : 'Légitime'}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================
          CONFIGURATION
      ====================================================== */}
      <div>
        <div className="bg-white rounded-2xl shadow-lg shadow-gray-100/70 border border-gray-100 p-6 transition-all hover:shadow-xl hover:shadow-gray-200/50">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end">

            <div className="flex-1">
              <label
                htmlFor="dns-domain"
                className="mb-2 block text-sm font-semibold text-gray-700"
              >
                Domaine à simuler
              </label>

              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Globe className="w-4 h-4 text-gray-400" />
                </div>
                <select
                  id="dns-domain"
                  value={domain}
                  onChange={(event) => setDomain(event.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white transition-all text-gray-900"
                >
                  {availableDomains.map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex-1">
              <label
                htmlFor="falsified-ip"
                className="mb-2 block text-sm font-semibold text-gray-700"
              >
                IP falsifiée
              </label>

              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Network className="w-4 h-4 text-gray-400" />
                </div>
                <input
                  id="falsified-ip"
                  type="text"
                  value={falsifiedIp}
                  onChange={(event) => setFalsifiedIp(event.target.value)}
                  placeholder="192.168.1.99"
                  className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white transition-all text-gray-900 placeholder-gray-400"
                />
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button
                size="lg"
                variant="primary"
                icon={ShieldCheck}
                iconPosition="left"
                disabled={isResolving || !domain.trim()}
                onClick={handleResolve}
              >
                {isResolving ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Résolution...
                  </span>
                ) : (
                  'Résoudre'
                )}
              </Button>

              <Button
                size="lg"
                variant="danger"
                icon={AlertTriangle}
                iconPosition="left"
                disabled={isSimulating || !domain.trim() || !falsifiedIp.trim()}
                onClick={handleAttack}
                className="shadow-lg shadow-red-200/50 hover:shadow-xl hover:shadow-red-200/70 transition-shadow"
              >
                {isSimulating ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Simulation en cours...
                  </span>
                ) : (
                  'Simuler l\'attaque'
                )}
              </Button>

              <Button
                size="lg"
                variant="outline"
                icon={RotateCcw}
                iconPosition="left"
                onClick={handleReset}
                disabled={isSimulating}
              >
                Réinitialiser
              </Button>
            </div>
          </div>

          {/* Error message */}
          {error && (
            <div className="mt-4 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4">
              <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>
      </div>

      {/* =====================================================
          PARCOURS NORMAL
      ====================================================== */}
      <div className="space-y-4">

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-emerald-100 to-emerald-200 rounded-xl flex items-center justify-center">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-900">
            Avant l'empoisonnement
          </h2>
          <span className="text-xs text-gray-400 font-medium bg-gray-100 px-2.5 py-0.5 rounded-full">
            Cache sain
          </span>
        </div>

        <div className="bg-white rounded-2xl shadow-lg shadow-gray-100/70 border border-gray-100 p-6">
          <div className="overflow-x-auto pb-2">
            <div className="flex min-w-[850px] items-center justify-between gap-4">

              {/* Utilisateur */}
              <DnsNode
                icon={Globe}
                title="Utilisateur"
                description="Demande DNS"
                status="normal"
              />

              <Arrow />

              {/* Résolveur */}
              <DnsNode
                icon={Server}
                title="Résolveur DNS"
                description="Résolution"
                status="normal"
              />

              <Arrow />

              {/* Cache */}
              <DnsNode
                icon={Database}
                title="Cache légitime"
                description={domain}
                status="success"
              />

              <Arrow />

              {/* IP */}
              <DnsNode
                icon={CheckCircle2}
                title="Adresse IP"
                description={getLegitimateIp()}
                status="success"
              />

            </div>
          </div>
        </div>
      </div>

      {/* =====================================================
          APRÈS EMPOISONNEMENT
      ====================================================== */}
      <div className="space-y-4">

        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-xl flex items-center justify-center transition-all duration-500 ${
            isPoisoned 
              ? 'bg-gradient-to-br from-red-100 to-red-200' 
              : 'bg-gradient-to-br from-gray-100 to-gray-200'
          }`}>
            <AlertTriangle className={`w-4 h-4 transition-all duration-500 ${
              isPoisoned ? 'text-red-600' : 'text-gray-400'
            }`} />
          </div>
          <h2 className="text-xl font-bold text-gray-900">
            Après l'empoisonnement simulé
          </h2>
          <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full transition-all duration-500 ${
            isPoisoned 
              ? 'bg-red-100 text-red-700' 
              : 'bg-gray-100 text-gray-400'
          }`}>
            {isPoisoned ? '⚠ Cache compromis' : 'En attente'}
          </span>
        </div>

        <div className={`bg-white rounded-2xl shadow-lg border transition-all duration-500 ${
          isPoisoned 
            ? 'shadow-red-100/70 border-red-200/60' 
            : 'shadow-gray-100/70 border-gray-100'
        } p-6`}>

          {!isPoisoned ? (
            <div className="flex min-h-[180px] flex-col items-center justify-center text-center">
              <div className="mb-4 w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center">
                <Lock className="w-7 h-7 text-gray-400" />
              </div>

              <h3 className="font-semibold text-gray-900">
                Cache non empoisonné
              </h3>

              <p className="mt-1 max-w-md text-sm text-gray-500">
                Lancez la simulation pour visualiser la modification
                du cache DNS fictif.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto pb-2">
              <div className="flex min-w-[850px] items-center justify-between gap-4">

                <DnsNode
                  icon={Globe}
                  title="Utilisateur"
                  description="Demande DNS"
                  status="normal"
                />

                <Arrow />

                <DnsNode
                  icon={Server}
                  title="Résolveur DNS"
                  description="Résolution"
                  status="normal"
                />

                <Arrow />

                <DnsNode
                  icon={AlertTriangle}
                  title="Cache empoisonné"
                  description={domain}
                  status="danger"
                />

                <Arrow />

                <DnsNode
                  icon={AlertTriangle}
                  title="Adresse IP falsifiée"
                  description={getResolvedIp()}
                  status="danger"
                />

              </div>
            </div>
          )}

        </div>
      </div>

      {/* =====================================================
          COMPARAISON
      ====================================================== */}
      {isPoisoned && (
        <div className="space-y-4 animate-fadeIn">

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center">
              <Network className="w-4 h-4 text-blue-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">
              Comparaison des réponses
            </h2>
          </div>

          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">

            {/* Réponse légitime */}
            <div className="bg-gradient-to-br from-emerald-50 to-emerald-100/50 rounded-2xl p-6 border border-emerald-200/50 shadow-sm hover:shadow-md hover:shadow-emerald-100/50 transition-all">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-xl bg-emerald-100 flex items-center justify-center">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900">
                    Réponse légitime
                  </h3>

                  <p className="text-sm text-emerald-600 font-medium">
                    ✓ Cache sain
                  </p>
                </div>
              </div>

              <div className="mt-6 space-y-3">
                <ComparisonRow
                  label="Domaine"
                  value={domain}
                />

                <ComparisonRow
                  label="Adresse IP attendue"
                  value={getLegitimateIp()}
                />

                <ComparisonRow
                  label="Source"
                  value="Réponse légitime simulée"
                />

                <ComparisonRow
                  label="État du cache"
                  value="Sain"
                  status="success"
                />
              </div>
            </div>

            {/* Réponse falsifiée */}
            <div className="bg-gradient-to-br from-red-50 to-red-100/40 rounded-2xl p-6 border-2 border-red-200 shadow-sm hover:shadow-md hover:shadow-red-100/50 transition-all">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-xl bg-red-100 flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900">
                    Réponse falsifiée
                  </h3>

                  <p className="text-sm text-red-600 font-medium">
                    ⚠ Cache empoisonné
                  </p>
                </div>
              </div>

              <div className="mt-6 space-y-3">
                <ComparisonRow
                  label="Domaine"
                  value={domain}
                />

                <ComparisonRow
                  label="Adresse IP reçue"
                  value={getResolvedIp()}
                  danger
                />

                <ComparisonRow
                  label="Source"
                  value="Réponse falsifiée simulée"
                  danger
                />

                <ComparisonRow
                  label="État du cache"
                  value="Empoisonné"
                  danger
                />
              </div>
            </div>

          </div>

          {/* Alerte */}
          <div className="flex items-start gap-4 rounded-2xl border-2 border-red-200/60 bg-gradient-to-br from-red-50 to-red-100/40 p-5 shadow-sm">
            <div className="w-9 h-9 bg-red-100 rounded-xl flex items-center justify-center flex-shrink-0">
              <AlertTriangle className="w-4 h-4 text-red-600" />
            </div>

            <div>
              <p className="font-semibold text-red-900">
                Résultat de la simulation
              </p>

              <p className="mt-0.5 text-sm leading-relaxed text-red-800/80">
                Le résolveur simulé retourne maintenant l'adresse IP <span className="font-mono font-semibold">{getResolvedIp()}</span> au lieu de <span className="font-mono font-semibold">{getLegitimateIp()}</span>. Dans un scénario réel,
                cela pourrait conduire l'utilisateur vers une destination
                différente.
              </p>
            </div>
          </div>
        </div>
      )}


    </div>
  );
};

/* ============================================================
   SOUS-COMPOSANTS
============================================================ */

const DnsNode = ({
  icon: Icon,
  title,
  description,
  status = 'normal',
}) => {

  const styles = {
    normal: {
      wrapper: 'border-gray-200 bg-white hover:border-gray-300',
      icon: 'bg-gray-100 text-gray-600 group-hover:bg-gray-200',
      title: 'text-gray-900',
      badge: 'bg-gray-100 text-gray-600',
    },

    success: {
      wrapper: 'border-emerald-200 bg-gradient-to-br from-emerald-50 to-emerald-100/50 hover:border-emerald-300',
      icon: 'bg-emerald-100 text-emerald-600 group-hover:bg-emerald-200',
      title: 'text-emerald-900',
      badge: 'bg-emerald-100 text-emerald-700',
    },

    danger: {
      wrapper: 'border-red-200 bg-gradient-to-br from-red-50 to-red-100/40 hover:border-red-300 animate-pulse',
      icon: 'bg-red-100 text-red-600 group-hover:bg-red-200',
      title: 'text-red-900',
      badge: 'bg-red-100 text-red-700',
    },
  };

  const style = styles[status];

  return (
    <div
      className={`
        w-44 shrink-0 rounded-2xl border-2 p-4
        shadow-sm hover:shadow-md
        transition-all duration-300 group
        ${style.wrapper}
      `}
    >
      <div
        className={`
          mx-auto mb-3 w-12 h-12 rounded-xl
          flex items-center justify-center
          transition-all duration-300 group-hover:scale-110
          ${style.icon}
        `}
      >
        <Icon className="w-6 h-6" />
      </div>

      <div className="text-center">
        <p className={`font-semibold text-sm ${style.title}`}>
          {title}
        </p>

        <p className="mt-1 truncate text-xs text-gray-500 font-mono">
          {description}
        </p>

        {status === 'danger' && (
          <span className="inline-block mt-2 px-2 py-0.5 bg-red-100 text-red-700 text-[10px] font-medium rounded-full">
            ⚠ Falsifié
          </span>
        )}

        {status === 'success' && (
          <span className="inline-block mt-2 px-2 py-0.5 bg-emerald-100 text-emerald-700 text-[10px] font-medium rounded-full">
            ✓ Légitime
          </span>
        )}
      </div>
    </div>
  );
};

const Arrow = () => (
  <ArrowRight className="w-5 h-5 shrink-0 text-gray-300 group-hover:text-gray-400 transition-colors" />
);

const ComparisonRow = ({ label, value, danger = false, status = 'normal' }) => {
  const getStatusColor = () => {
    if (danger) return 'text-red-600';
    if (status === 'success') return 'text-emerald-600';
    return 'text-gray-900';
  };

  return (
    <div className="flex items-center justify-between gap-4 border-b border-gray-100/80 pb-3 last:border-0 last:pb-0">
      <span className="text-sm text-gray-500 font-medium">
        {label}
      </span>

      <span className={`text-right text-sm font-mono font-semibold ${getStatusColor()}`}>
        {value}
      </span>
    </div>
  );
};


export default DnsPoisoningPage;