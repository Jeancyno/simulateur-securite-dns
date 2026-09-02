import React, { useState } from 'react';
import {
  Search,
  RotateCcw,
  Info,
  ShieldCheck,
  Lock,
  Unlock,
  Server,
  Globe,
  Clock3,
  Network,
  CheckCircle2,
  AlertTriangle,
  CircleAlert,
  ArrowDown as ArrowDownIcon,
  Eye,
} from 'lucide-react';

import Button from '../components/ui/Button';
import Card from '../components/ui/Card';

const DnsVsDohPage = () => {
  const [domain, setDomain] = useState('example.com');
  const [status, setStatus] = useState(null);
  const [isComparing, setIsComparing] = useState(false);

  const [results, setResults] = useState(null);

  const handleCompare = () => {
    if (!domain.trim()) {
      setStatus('error');
      setResults(null);
      return;
    }

    setIsComparing(true);
    setStatus(null);
    setResults(null);

    // Données de démonstration.
    // Elles seront remplacées par l'appel réel au Backend.
    setTimeout(() => {
      setResults({
        classic: {
          protocol: 'DNS',
          transport: 'UDP / TCP',
          encryption: false,
          privacy: 'Limitée',
          response: '93.184.216.34',
          responseTime: '24 ms',
          resolver: 'Résolveur DNS',
          visibility: 'Requête plus directement observable',
        },

        doh: {
          protocol: 'DNS over HTTPS',
          transport: 'HTTPS',
          encryption: true,
          privacy: 'Améliorée',
          response: '93.184.216.34',
          responseTime: '38 ms',
          resolver: 'Résolveur DoH',
          visibility: 'Requête transportée dans un canal HTTPS chiffré',
          fallback: false,
        },
      });

      setStatus('success');
      setIsComparing(false);
    }, 1200);
  };

  const handleReset = () => {
    setDomain('example.com');
    setStatus(null);
    setResults(null);
    setIsComparing(false);
  };

  return (
    <div className="w-full max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">

      {/* =====================================================
          HEADER
      ====================================================== */}
      <div className="space-y-4">

        <div className="flex items-start gap-5">
          <div className="w-14 h-14 bg-gradient-to-br from-blue-100 to-blue-200 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md shadow-blue-200/50">
            <Network className="w-7 h-7 text-blue-600" />
          </div>

          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight">
              DNS classique vs DNS over HTTPS
            </h1>

            <p className="mt-1.5 text-lg text-gray-600 max-w-3xl">
              Comparez visuellement une requête DNS classique avec une
              requête DNS transportée dans HTTPS.
            </p>
          </div>
        </div>

        {/* Information pédagogique */}
        <div className="flex items-start gap-4 rounded-2xl border border-blue-200/60 bg-gradient-to-br from-blue-50 to-blue-100/40 p-5 shadow-sm">
          <div className="w-9 h-9 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
            <Info className="w-4 h-4 text-blue-600" />
          </div>

          <div>
            <p className="font-semibold text-blue-900">
              Comprendre DNS over HTTPS
            </p>

            <p className="mt-0.5 text-sm text-blue-800/80 leading-relaxed">
              DNS over HTTPS (DoH) transporte les requêtes DNS dans une
              connexion HTTPS chiffrée. Cela améliore la confidentialité
              du transport, sans résoudre à lui seul tous les problèmes
              de sécurité liés au DNS.
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
              handleCompare();
            }}
            className="flex flex-col gap-5 lg:flex-row lg:items-end"
          >

            <div className="flex-1">
              <label
                htmlFor="dns-doh-domain"
                className="mb-2 block text-sm font-semibold text-gray-700"
              >
                Nom de domaine
              </label>

              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="w-4 h-4 text-gray-400" />
                </div>

                <input
                  id="dns-doh-domain"
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
                disabled={isComparing}
                className="shadow-lg shadow-blue-200/50 hover:shadow-xl hover:shadow-blue-200/70 transition-shadow"
              >
                {isComparing ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Comparaison...
                  </span>
                ) : (
                  'Comparer'
                )}
              </Button>

              <Button
                type="button"
                variant="outline"
                size="lg"
                icon={RotateCcw}
                iconPosition="left"
                onClick={handleReset}
                disabled={isComparing}
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
              Nom de domaine requis
            </p>

            <p className="mt-0.5 text-sm text-red-800/80">
              Entrez un nom de domaine avant de lancer la comparaison.
            </p>
          </div>
        </div>
      )}

      {/* =====================================================
          RÉSULTATS
      ====================================================== */}
      {status === 'success' && results && (
        <div className="space-y-6 animate-fadeIn">

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-100 to-emerald-200 rounded-xl flex items-center justify-center">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
            </div>

            <h2 className="text-xl font-bold text-gray-900">
              Résultats de la comparaison
            </h2>

            <span className="text-xs text-emerald-600 font-medium bg-emerald-100 px-2.5 py-0.5 rounded-full">
              {domain}
            </span>
          </div>

          {/* =================================================
              CARTES DNS / DOH
          ================================================== */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            <ComparisonCard
              type="classic"
              title="DNS classique"
              icon={Globe}
              data={results.classic}
            />

            <ComparisonCard
              type="doh"
              title="DNS over HTTPS"
              icon={Lock}
              data={results.doh}
            />

          </div>

          {/* =================================================
              COMPARAISON RAPIDE
          ================================================== */}
          <div className="space-y-4">

            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-100 to-purple-200 rounded-xl flex items-center justify-center">
                <Eye className="w-4 h-4 text-purple-600" />
              </div>

              <h2 className="text-xl font-bold text-gray-900">
                Comparaison de confidentialité
              </h2>
            </div>

            <div className="bg-white rounded-2xl shadow-lg shadow-gray-100/70 border border-gray-100 overflow-hidden">

              <div className="grid grid-cols-1 md:grid-cols-3 border-b border-gray-100">

                <ComparisonHeader title="Élément" />

                <ComparisonHeader title="DNS classique" />

                <ComparisonHeader title="DNS over HTTPS" />

              </div>

              <ComparisonRow
                label="Protocole"
                classic={results.classic.protocol}
                doh={results.doh.protocol}
              />

              <ComparisonRow
                label="Transport"
                classic={results.classic.transport}
                doh={results.doh.transport}
              />

              <ComparisonRow
                label="Chiffrement du transport"
                classic="Non"
                doh="Oui"
              />

              <ComparisonRow
                label="Confidentialité"
                classic={results.classic.privacy}
                doh={results.doh.privacy}
              />

              <ComparisonRow
                label="Temps de réponse"
                classic={results.classic.responseTime}
                doh={results.doh.responseTime}
              />

            </div>
          </div>

          {/* =================================================
              PARCOURS DES REQUÊTES
          ================================================== */}
          <div className="space-y-4">

            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-indigo-100 to-indigo-200 rounded-xl flex items-center justify-center">
                <Network className="w-4 h-4 text-indigo-600" />
              </div>

              <h2 className="text-xl font-bold text-gray-900">
                Parcours des requêtes
              </h2>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

              <RequestPath
                type="classic"
                title="DNS classique"
                domain={domain}
              />

              <RequestPath
                type="doh"
                title="DNS over HTTPS"
                domain={domain}
              />

            </div>
          </div>

          {/* =================================================
              EXPLICATION
          ================================================== */}
          <EducationalSection />

        </div>
      )}

      {/* =====================================================
          INFORMATION GÉNÉRALE
      ====================================================== */}
      {!results && status !== 'error' && (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50/70 rounded-2xl p-6 border border-blue-200/50 shadow-sm">

          <div className="flex items-start gap-4">

            <div className="w-11 h-11 bg-white rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm shadow-blue-200/50">
              <Lock className="w-5 h-5 text-blue-600" />
            </div>

            <div>
              <h2 className="font-semibold text-gray-900">
                Pourquoi comparer DNS et DoH ?
              </h2>

              <p className="mt-1 text-sm leading-relaxed text-gray-600">
                Cette comparaison permet de visualiser la différence entre
                une requête DNS traditionnelle et une requête DNS transportée
                dans HTTPS, notamment au niveau du canal de transport et de
                la confidentialité.
              </p>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};

/* ============================================================
   CARTE DE COMPARAISON
============================================================ */

const ComparisonCard = ({
  type,
  title,
  icon: Icon,
  data,
}) => {
  const isDoh = type === 'doh';

  return (
    <div
      className={`bg-white rounded-2xl p-6 border-2 shadow-sm hover:shadow-lg transition-all ${
        isDoh
          ? 'border-blue-200/70'
          : 'border-gray-200/70'
      }`}
    >

      <div className="flex items-center justify-between">

        <div className="flex items-center gap-3">

          <div
            className={`w-12 h-12 rounded-xl flex items-center justify-center ${
              isDoh
                ? 'bg-blue-100 text-blue-600'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            <Icon className="w-6 h-6" />
          </div>

          <div>
            <h3 className="font-bold text-gray-900">
              {title}
            </h3>

            <p className="text-xs text-gray-500">
              {data.protocol}
            </p>
          </div>

        </div>

        <div
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full ${
            data.encryption
              ? 'bg-emerald-100'
              : 'bg-amber-100'
          }`}
        >

          {data.encryption ? (
            <Lock className="w-3.5 h-3.5 text-emerald-600" />
          ) : (
            <Unlock className="w-3.5 h-3.5 text-amber-600" />
          )}

          <span
            className={`text-[10px] font-semibold uppercase tracking-wide ${
              data.encryption
                ? 'text-emerald-700'
                : 'text-amber-700'
            }`}
          >
            {data.encryption ? 'Chiffré' : 'Non chiffré'}
          </span>

        </div>
      </div>

      <div className="mt-6 space-y-4">

        <DataLine
          icon={Network}
          label="Transport"
          value={data.transport}
        />

        <DataLine
          icon={Server}
          label="Résolveur"
          value={data.resolver}
        />

        <DataLine
          icon={Globe}
          label="Réponse DNS"
          value={data.response}
        />

        <DataLine
          icon={Clock3}
          label="Temps de réponse"
          value={data.responseTime}
        />

        <DataLine
          icon={Eye}
          label="Visibilité"
          value={data.visibility}
        />

        <div
          className={`rounded-xl p-4 ${
            data.encryption
              ? 'bg-emerald-50 border border-emerald-100'
              : 'bg-amber-50 border border-amber-100'
          }`}
        >

          <p
            className={`text-xs font-semibold uppercase tracking-wide ${
              data.encryption
                ? 'text-emerald-700'
                : 'text-amber-700'
            }`}
          >
            Confidentialité
          </p>

          <p className="mt-1 text-sm text-gray-700">
            {data.privacy}
          </p>

        </div>

        {data.fallback && (
          <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4">

            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />

            <div>
              <p className="font-semibold text-amber-900">
                Mode de secours utilisé
              </p>

              <p className="mt-1 text-xs text-amber-800">
                Le résolveur DoH externe est indisponible.
                Les données affichées doivent être interprétées
                comme des données de secours et non comme une
                réponse DoH réelle.
              </p>
            </div>

          </div>
        )}

      </div>
    </div>
  );
};

/* ============================================================
   LIGNE DE DONNÉES
============================================================ */

const DataLine = ({
  icon: Icon,
  label,
  value,
}) => (
  <div className="flex items-start gap-3">

    <div className="w-8 h-8 rounded-lg bg-gray-50 flex items-center justify-center flex-shrink-0">
      <Icon className="w-4 h-4 text-gray-500" />
    </div>

    <div className="min-w-0 flex-1">
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">
        {label}
      </p>

      <p className="mt-0.5 text-sm font-medium text-gray-800 break-words">
        {value}
      </p>
    </div>

  </div>
);

/* ============================================================
   TABLEAU
============================================================ */

const ComparisonHeader = ({ title }) => (
  <div className="p-4 bg-gray-50">
    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
      {title}
    </p>
  </div>
);

const ComparisonRow = ({
  label,
  classic,
  doh,
}) => (
  <div className="grid grid-cols-1 md:grid-cols-3 border-b border-gray-100 last:border-b-0">

    <div className="p-4">
      <p className="text-sm font-semibold text-gray-700">
        {label}
      </p>
    </div>

    <div className="p-4 bg-gray-50/40">
      <p className="text-sm text-gray-600">
        {classic}
      </p>
    </div>

    <div className="p-4 bg-blue-50/30">
      <p className="text-sm font-medium text-gray-700">
        {doh}
      </p>
    </div>

  </div>
);

/* ============================================================
   PARCOURS DES REQUÊTES
============================================================ */

const RequestPath = ({
  type,
  title,
  domain,
}) => {
  const isDoh = type === 'doh';

  return (
    <div
      className={`bg-white rounded-2xl border-2 p-6 shadow-sm ${
        isDoh
          ? 'border-blue-200/70'
          : 'border-gray-200/70'
      }`}
    >

      <div className="flex items-center gap-3">

        <div
          className={`w-10 h-10 rounded-xl flex items-center justify-center ${
            isDoh
              ? 'bg-blue-100 text-blue-600'
              : 'bg-gray-100 text-gray-600'
          }`}
        >
          {isDoh ? (
            <Lock className="w-5 h-5" />
          ) : (
            <Globe className="w-5 h-5" />
          )}
        </div>

        <h3 className="font-bold text-gray-900">
          {title}
        </h3>

      </div>

      <div className="mt-6 flex flex-col items-center">

        <PathNode
          icon={Globe}
          title="Utilisateur"
          description={domain}
        />

        <PathArrow encrypted={isDoh} />

        <PathNode
          icon={Server}
          title={isDoh ? 'Résolveur DoH' : 'Résolveur DNS'}
          description={
            isDoh
              ? 'Requête transportée dans HTTPS'
              : 'Requête DNS traditionnelle'
          }
          secure={isDoh}
        />

        <PathArrow encrypted={isDoh} />

        <PathNode
          icon={CheckCircle2}
          title="Réponse DNS"
          description={
            isDoh
              ? 'Réponse transportée via HTTPS'
              : 'Réponse DNS'
          }
          success
        />

      </div>
    </div>
  );
};

/* ============================================================
   NŒUD DU PARCOURS
============================================================ */

const PathNode = ({
  icon: Icon,
  title,
  description,
  secure = false,
  success = false,
}) => (
  <div
    className={`flex w-full max-w-md items-center gap-4 rounded-2xl border-2 p-4 ${
      success
        ? 'border-emerald-200/60 bg-emerald-50'
        : secure
          ? 'border-blue-200/60 bg-blue-50'
          : 'border-gray-200/60 bg-white'
    }`}
  >

    <div
      className={`w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 ${
        success
          ? 'bg-emerald-100 text-emerald-600'
          : secure
            ? 'bg-blue-100 text-blue-600'
            : 'bg-gray-100 text-gray-600'
      }`}
    >
      <Icon className="w-5 h-5" />
    </div>

    <div className="min-w-0 flex-1">

      <p className="font-semibold text-gray-900">
        {title}
      </p>

      <p className="mt-0.5 text-sm text-gray-500">
        {description}
      </p>

    </div>

    {secure && (
      <Lock className="w-5 h-5 text-blue-600 flex-shrink-0" />
    )}

    {success && (
      <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
    )}

  </div>
);

/* ============================================================
   FLÈCHE
============================================================ */

const PathArrow = ({ encrypted = false }) => (
  <div className="flex h-14 items-center justify-center relative">

    <div
      className={`w-px h-7 ${
        encrypted
          ? 'bg-blue-300'
          : 'bg-gray-300'
      }`}
    />

    <ArrowDownIcon
      className={`w-5 h-5 absolute ${
        encrypted
          ? 'text-blue-500'
          : 'text-gray-400'
      }`}
    />

    {encrypted && (
      <span className="absolute left-1/2 -translate-x-1/2 -translate-y-5 whitespace-nowrap text-[10px] font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
        🔒 HTTPS
      </span>
    )}

  </div>
);

/* ============================================================
   SECTION PÉDAGOGIQUE
============================================================ */

const EducationalSection = () => (
  <div className="space-y-4">

    <div className="flex items-center gap-3">

      <div className="w-8 h-8 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center">
        <Info className="w-4 h-4 text-blue-600" />
      </div>

      <h2 className="text-xl font-bold text-gray-900">
        À retenir
      </h2>

    </div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

      <EducationalCard
        icon={Globe}
        title="DNS classique"
        description="La requête DNS traditionnelle utilise généralement UDP ou TCP et son transport n'est pas chiffré par défaut."
      />

      <EducationalCard
        icon={Lock}
        title="DNS over HTTPS"
        description="DoH transporte la requête DNS dans HTTPS, ce qui protège le contenu de la requête sur le canal de transport."
      />

      <EducationalCard
        icon={ShieldCheck}
        title="Une protection partielle"
        description="Le chiffrement HTTPS améliore la confidentialité du transport, mais ne constitue pas à lui seul une solution complète de sécurité DNS."
      />

    </div>
  </div>
);

/* ============================================================
   CARTE PÉDAGOGIQUE
============================================================ */

const EducationalCard = ({
  icon: Icon,
  title,
  description,
}) => (
  <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-all duration-200 group h-full">

    <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
      <Icon className="w-5 h-5 text-blue-600" />
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

export default DnsVsDohPage;