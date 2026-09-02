import React from 'react';
import { Shield, Globe, ShieldCheck, Lock, ArrowRight, BookOpen, Network, AlertTriangle, CheckCircle2, Zap, Layers, ShieldAlert } from 'lucide-react';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import IconButton from '../components/ui/IconButton';

const HomePage = () => {
  const modules = [
    {
      id: 'dns-resolution',
      title: 'Résolution DNS',
      icon: Globe,
      description: 'Comprendre le processus de résolution des noms de domaine et le fonctionnement des serveurs DNS.',
      badge: 'Disponible',
      badgeColor: 'success',
      available: true,
    },
    {
      id: 'dns-poisoning',
      title: 'Empoisonnement DNS',
      icon: AlertTriangle,
      description: 'Simuler et comprendre les attaques par empoisonnement de cache DNS.',
      badge: 'À venir',
      badgeColor: 'secondary',
      available: false,
    },
    {
      id: 'dnssec',
      title: 'DNSSEC',
      icon: ShieldCheck,
      description: 'Apprendre le fonctionnement de DNSSEC et la signature cryptographique des enregistrements DNS.',
      badge: 'À venir',
      badgeColor: 'secondary',
      available: false,
    },
    {
      id: 'doh',
      title: 'DNS over HTTPS',
      icon: Lock,
      description: 'Découvrir comment DNS over HTTPS protège la confidentialité des requêtes DNS.',
      badge: 'À venir',
      badgeColor: 'secondary',
      available: false,
    },
  ];

  const educationalPoints = [
    {
      icon: Network,
      title: 'Résolution des noms',
      description: 'Comment les noms de domaine sont convertis en adresses IP',
    },
    {
      icon: Layers,
      title: 'Hiérarchie DNS',
      description: 'Structure organisationnelle du système DNS mondial',
    },
    {
      icon: ShieldAlert,
      title: 'Attaques DNS',
      description: 'Comprendre les vulnérabilités et les risques de sécurité',
    },
    {
      icon: ShieldCheck,
      title: 'Mécanismes de protection',
      description: 'DNSSEC, DNS over HTTPS et autres solutions de sécurité',
    },
  ];

  return (
    <div className="space-y-1">
      {/* Hero Section */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 bg-primary-50 text-primary-700 px-4 py-2 rounded-full text-sm font-medium">
            <Shield className="w-4 h-4" />
            <span>Simulateur de Sécurité DNS</span>
          </div>
          
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-secondary-900 leading-tight">
            Simulateur de Sécurité DNS
          </h1>
          
          <p className="text-lg sm:text-xl text-secondary-600 leading-relaxed">
            Comprenez et simulez le fonctionnement du DNS et ses mécanismes de sécurité à travers des expériences interactives et éducatives.
          </p>
          
          <div className="flex flex-wrap gap-4">
            <Button 
              size="lg" 
              icon={ArrowRight}
              iconPosition="right"
              onClick={() => console.log('Navigation vers dns-resolution')}
            >
              Commencer la simulation
            </Button>
            <Button 
              variant="outline" 
              size="lg"
              icon={BookOpen}
              iconPosition="left"
            >
              En savoir plus
            </Button>
          </div>
        </div>
        
        <div className="hidden lg:flex justify-center">
          <Card variant="gradient" padding="xl" className="w-full max-w-md">
            <div className="text-center space-y-4">
              <div className="w-32 h-32 mx-auto bg-primary-100 rounded-full flex items-center justify-center">
                <Shield className="w-16 h-16 text-primary-600" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-semibold text-secondary-900">Sécurité DNS</h3>
                <p className="text-secondary-600 text-sm">
                  Explorez les mécanismes de protection du système de noms de domaine
                </p>
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* Modules Section */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <Layers className="w-6 h-6 text-primary-600" />
          <h2 className="text-2xl sm:text-3xl font-bold text-secondary-900">Modules du simulateur</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {modules.map((module) => {
            const Icon = module.icon;
            return (
              <Card
                key={module.id}
                variant={module.available ? 'elevated' : 'default'}
                padding="md"
                className={`h-full ${!module.available ? 'opacity-75' : ''}`}
              >
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                      module.available ? 'bg-primary-100' : 'bg-secondary-100'
                    }`}>
                      <Icon className={`w-6 h-6 ${
                        module.available ? 'text-primary-600' : 'text-secondary-400'
                      }`} />
                    </div>
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                      module.badgeColor === 'success' 
                        ? 'bg-success-100 text-success-700' 
                        : 'bg-secondary-100 text-secondary-600'
                    }`}>
                      {module.badge}
                    </span>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-secondary-900 mb-2">{module.title}</h3>
                    <p className="text-sm text-secondary-600 leading-relaxed">
                      {module.description}
                    </p>
                  </div>
                  
                  {module.available && (
                    <div className="pt-2">
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        fullWidth
                        icon={ArrowRight}
                        iconPosition="right"
                      >
                        Ouvrir le module
                      </Button>
                    </div>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Educational Section */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <BookOpen className="w-6 h-6 text-primary-600" />
          <h2 className="text-2xl sm:text-3xl font-bold text-secondary-900">Pourquoi comprendre le DNS ?</h2>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {educationalPoints.map((point, index) => {
            const Icon = point.icon;
            return (
              <Card key={index} variant="default" padding="md" className="h-full">
                <div className="space-y-3">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Icon className="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-secondary-900 text-sm mb-1">
                      {point.title}
                    </h3>
                    <p className="text-xs text-secondary-600 leading-relaxed">
                      {point.description}
                    </p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </section>

  
    </div>
  );
};

export default HomePage;
