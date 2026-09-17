import React, { useState } from 'react';
import {
  ShieldCheck,
  Search,
  CheckCircle2,
  AlertTriangle,
  CircleAlert,
  KeyRound,
  Link2,
  FileCheck2,
  Server,
  ArrowDown as ArrowDownIcon,
  RotateCcw,
  Info,
  Zap,
  Lock,
  Fingerprint,
} from 'lucide-react';

import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import dnssecService from '../services/dnssecService';

const DnssecPage = () => {
  const [domain, setDomain] = useState('example.com');
  const [status, setStatus] = useState(null);
  const [isChecking, setIsChecking] = useState(false);
  const [dnssecData, setDnssecData] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const handleVerify = async () => {
    if (!domain.trim()) {
      setStatus('error');
      setErrorMessage('Nom de domaine requis');
      return;
    }

    if (!dnssecService.isValidDomain(domain)) {
      setStatus('error');
      setErrorMessage('Format de domaine invalide');
      return;
    }

    setIsChecking(true);
    setStatus(null);
    setDnssecData(null);
    setErrorMessage('');

    try {
      const result = await dnssecService.verifyDnssec(domain);

      if (result.success) {
        setStatus(result.status.toLowerCase());
        setDnssecData(result);
      } else {
        setStatus('error');
        setErrorMessage(result.error || 'Erreur lors de la vérification DNSSEC');
      }
    } catch (error) {
      setStatus('error');
      setErrorMessage('Erreur de connexion au serveur');
      console.error('DNSSEC Error:', error);
    } finally {
      setIsChecking(false);
    }
  };

  const handleReset = () => {
    setStatus(null);
    setIsChecking(false);
    setDnssecData(null);
    setErrorMessage('');
  };

  return (
    <div className="w-full max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">

      {/* =====================================================
          HEADER
      ====================================================== */}
      <div className="space-y-4">
        <div className="flex items-start gap-5">
          <div className="w-14 h-14 bg-gradient-to-br from-blue-100 to-blue-200 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md shadow-blue-200/50">
            <ShieldCheck className="w-7 h-7 text-blue-600" />
          </div>

          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight">
              DNSSEC
            </h1>

            <p className="mt-1.5 text-lg text-gray-600 max-w-2xl">
              Vérifiez et visualisez la chaîne de confiance DNSSEC
              d'un nom de domaine.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-4 rounded-2xl border border-blue-200/60 bg-gradient-to-br from-blue-50 to-blue-100/40 p-5 shadow-sm">
          <div className="w-9 h-9 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
            <Info className="w-4 h-4 text-blue-600" />
          </div>

          <div>
            <p className="font-semibold text-blue-900">
              Comprendre DNSSEC
            </p>

            <p className="mt-0.5 text-sm text-blue-800/80 leading-relaxed">
              DNSSEC permet de vérifier l'authenticité des informations DNS
              grâce à une chaîne de confiance cryptographique.
            </p>
          </div>
        </div>
      </div>

      {/* =====================================================
          RECHERCHE
      ====================================================== */}
      <div>
        <div className="bg-white rounded-2xl shadow-lg shadow-gray-100/70 border border-gray-100 p-6 transition-all hover:shadow-xl hover:shadow-gray-200/50">
          <form
            onSubmit={(event) => {
              event.preventDefault();
              handleVerify();
            }}
            className="flex flex-col gap-5 lg:flex-row lg:items-end"
          >
            <div className="flex-1">
              <label
                htmlFor="dnssec-domain"
                className="mb-2 block text-sm font-semibold text-gray-700"
              >
                Nom de domaine
              </label>

              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="w-4 h-4 text-gray-400" />
                </div>
                <input
                  id="dnssec-domain"
                  type="text"
                  value={domain}
                  onChange={(event) => setDomain(event.target.value)}
                  placeholder="exemple.com"
                  className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white transition-all text-gray-900 placeholder-gray-400"
                />
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button
                type="submit"
                size="lg"
                icon={Search}
                iconPosition="left"
                disabled={isChecking}
                className="shadow-lg shadow-blue-200/50 hover:shadow-xl hover:shadow-blue-200/70 transition-shadow"
              >
                {isChecking ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Vérification...
                  </span>
                ) : (
                  'Vérifier DNSSEC'
                )}
              </Button>

              <Button
                type="button"
                variant="outline"
                size="lg"
                icon={RotateCcw}
                iconPosition="left"
                onClick={handleReset}
                disabled={isChecking}
              >
                Réinitialiser
              </Button>
            </div>
          </form>
        </div>
      </div>

      {/* =====================================================
          ERREUR
      ====================================================== */}
      {status === 'error' && (
        <div className="flex items-start gap-4 rounded-2xl border-2 border-red-200/60 bg-gradient-to-br from-red-50 to-red-100/40 p-5 shadow-sm animate-fadeIn">
          <div className="w-9 h-9 bg-red-100 rounded-xl flex items-center justify-center flex-shrink-0">
            <CircleAlert className="w-4 h-4 text-red-600" />
          </div>

          <div>
            <p className="font-semibold text-red-900">
              Erreur
            </p>

            <p className="mt-0.5 text-sm text-red-800/80">
              {errorMessage || 'Une erreur est survenue lors de la vérification DNSSEC.'}
            </p>
          </div>
        </div>
      )}

      {/* =====================================================
          DIAGNOSTIC
      ====================================================== */}
      {status && status !== 'error' && dnssecData && (
        <div className="space-y-4 animate-fadeIn">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-100 to-emerald-200 rounded-xl flex items-center justify-center">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">
              Diagnostic DNSSEC
            </h2>
          </div>

          <StatusBanner status={status} domain={domain} message={dnssecData.message} />
        </div>
      )}

      {/* =====================================================
          ENREGISTREMENTS DNSSEC
      ====================================================== */}
      {status && status !== 'error' && dnssecData && (
        <div className="space-y-4 animate-fadeIn">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-100 to-purple-200 rounded-xl flex items-center justify-center">
              <KeyRound className="w-4 h-4 text-purple-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">
              Enregistrements DNSSEC
            </h2>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <DnssecRecord
              icon={KeyRound}
              title="DNSKEY"
              description={dnssecData.dnskey?.description || 'Non disponible'}
              status={dnssecData.dnskey?.exists ? 'valid' : 'invalid'}
            />

            <DnssecRecord
              icon={Link2}
              title="DS"
              description={dnssecData.ds?.description || 'Non disponible'}
              status={dnssecData.ds?.exists ? 'valid' : 'invalid'}
            />

            <DnssecRecord
              icon={FileCheck2}
              title="RRSIG"
              description={dnssecData.rrsig?.description || 'Non disponible'}
              status={dnssecData.rrsig?.exists ? 'valid' : 'invalid'}
            />
          </div>
        </div>
      )}

      {/* =====================================================
          CHAÎNE DE CONFIANCE
      ====================================================== */}
      {status === 'valid' && (
        <div className="space-y-4 animate-fadeIn">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-100 to-indigo-200 rounded-xl flex items-center justify-center">
              <Fingerprint className="w-4 h-4 text-indigo-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">
              Chaîne de confiance
            </h2>
            <span className="text-xs text-emerald-600 font-medium bg-emerald-100 px-2.5 py-0.5 rounded-full">
              ✓ Validée
            </span>
          </div>

          <div className="bg-white rounded-2xl shadow-lg shadow-gray-100/70 border border-gray-100 p-6">
            <div className="flex flex-col items-center max-w-2xl mx-auto">
              <TrustNode
                icon={Server}
                title="Zone racine"
                description="Point de confiance"
              />

              <ArrowDown />

              <TrustNode
                icon={Link2}
                title="DS"
                description="Lien vers la zone enfant"
              />

              <ArrowDown />

              <TrustNode
                icon={KeyRound}
                title="DNSKEY"
                description="Clé publique de la zone"
              />

              <ArrowDown />

              <TrustNode
                icon={FileCheck2}
                title="RRSIG"
                description="Signature des données DNS"
              />

              <ArrowDown />

              <TrustNode
                icon={ShieldCheck}
                title={domain}
                description="Validation réussie"
                success
              />
            </div>
          </div>
        </div>
      )}


      {/* =====================================================
          CONTRE-MESURES
      ====================================================== */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50/70 rounded-2xl p-6 border border-blue-200/50 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="w-11 h-11 bg-white rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm shadow-blue-200/50">
            <Lock className="w-5 h-5 text-blue-600" />
          </div>

          <div>
            <h2 className="font-semibold text-gray-900">
              Pourquoi DNSSEC est important ?
            </h2>

            <p className="mt-1 text-sm leading-relaxed text-gray-600">
              DNSSEC permet de détecter les réponses DNS qui ne correspondent
              pas aux données authentifiées de la zone. Il contribue ainsi à
              protéger l'intégrité des réponses contre certaines formes de
              falsification.
            </p>
          </div>
        </div>
      </div>

    </div>
  );
};

/* ============================================================
   COMPOSANTS
============================================================ */

const StatusBanner = ({ status, domain, message }) => {
  const configurations = {
    valid: {
      icon: CheckCircle2,
      title: 'DNSSEC VALIDÉ',
      description: message || `La chaîne de confiance de ${domain} est valide.`,
      container: 'border-emerald-200/60 bg-gradient-to-br from-emerald-50 to-emerald-100/40',
      iconContainer: 'bg-emerald-100',
      iconColor: 'text-emerald-600',
      titleColor: 'text-emerald-900',
      textColor: 'text-emerald-800/80',
    },

    unsigned: {
      icon: Info,
      title: 'DNSSEC NON CONFIGURÉ',
      description: message || `Le domaine ${domain} ne possède pas de validation DNSSEC.`,
      container: 'border-amber-200/60 bg-gradient-to-br from-amber-50 to-amber-100/40',
      iconContainer: 'bg-amber-100',
      iconColor: 'text-amber-600',
      titleColor: 'text-amber-900',
      textColor: 'text-amber-800/80',
    },

    invalid: {
      icon: AlertTriangle,
      title: 'VALIDATION ÉCHOUÉE',
      description: message || 'La chaîne de confiance DNSSEC est rompue ou invalide.',
      container: 'border-red-200/60 bg-gradient-to-br from-red-50 to-red-100/40',
      iconContainer: 'bg-red-100',
      iconColor: 'text-red-600',
      titleColor: 'text-red-900',
      textColor: 'text-red-800/80',
    },
  };

  const config = configurations[status];
  if (!config) return null;

  const Icon = config.icon;

  return (
    <div className={`flex items-start gap-4 rounded-2xl border-2 p-5 shadow-sm ${config.container}`}>
      <div className={`w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 ${config.iconContainer}`}>
        <Icon className={`w-5 h-5 ${config.iconColor}`} />
      </div>

      <div>
        <h3 className={`font-bold ${config.titleColor}`}>
          {config.title}
        </h3>

        <p className={`mt-0.5 text-sm ${config.textColor}`}>
          {config.description}
        </p>
      </div>
    </div>
  );
};

const DnssecRecord = ({
  icon: Icon,
  title,
  description,
  status,
}) => {
  const IconComponent = Icon;

  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md hover:shadow-gray-100/50 transition-all duration-200 group">
      <div className="flex items-center justify-between">
        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
          <IconComponent className="w-5 h-5 text-blue-600" />
        </div>

        {status === 'valid' && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-100 rounded-full">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span className="text-[10px] font-semibold text-emerald-700 uppercase tracking-wide">Valide</span>
          </div>
        )}
        {status === 'invalid' && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-red-100 rounded-full">
            <AlertTriangle className="w-3.5 h-3.5 text-red-600" />
            <span className="text-[10px] font-semibold text-red-700 uppercase tracking-wide">Invalide</span>
          </div>
        )}
      </div>

      <h3 className="mt-4 font-semibold text-gray-900">
        {title}
      </h3>

      <p className="mt-1.5 text-sm leading-relaxed text-gray-500">
        {description}
      </p>

      <div className="mt-4 h-1 w-12 bg-gradient-to-r from-blue-400 to-blue-600 rounded-full group-hover:w-full transition-all duration-300" />
    </div>
  );
};

const TrustNode = ({
  icon: Icon,
  title,
  description,
  success = false,
}) => {
  const IconComponent = Icon;

  return (
    <div className={`flex w-full max-w-md items-center gap-4 rounded-2xl border-2 p-4 transition-all duration-300 hover:shadow-md ${
      success
        ? 'border-emerald-200/60 bg-gradient-to-br from-emerald-50 to-emerald-100/40 hover:border-emerald-300'
        : 'border-gray-200/60 bg-white hover:border-gray-300'
    }`}>
      <div className={`w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-300 ${
        success
          ? 'bg-emerald-100 text-emerald-600'
          : 'bg-blue-50 text-blue-600'
      }`}>
        <IconComponent className="w-5 h-5" />
      </div>

      <div className="min-w-0 flex-1">
        <p className="font-semibold text-gray-900">
          {title}
        </p>

        <p className="mt-0.5 text-sm text-gray-500">
          {description}
        </p>
      </div>

      {success && (
        <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
      )}
    </div>
  );
};

const ArrowDown = () => (
  <div className="flex h-12 items-center justify-center">
    <div className="w-px h-6 bg-gradient-to-b from-gray-300 to-gray-400/50" />
    <ArrowDownIcon className="w-5 h-5 text-gray-400 absolute ml-0.5" />
  </div>
);

const EducationalCard = ({
  icon: Icon,
  title,
  description,
}) => {
  const IconComponent = Icon;

  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md hover:shadow-gray-100/50 transition-all duration-200 group h-full">
      <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
        <IconComponent className="w-5 h-5 text-blue-600" />
      </div>

      <h3 className="mt-4 font-semibold text-gray-900">
        {title}
      </h3>

      <p className="mt-1.5 text-sm leading-relaxed text-gray-500">
        {description}
      </p>

      <div className="mt-4 h-1 w-12 bg-gradient-to-r from-blue-400 to-blue-600 rounded-full group-hover:w-full transition-all duration-300" />
    </div>
  );
};

export default DnssecPage;
