import React, { useEffect, useState } from 'react';
import {
  Home,
  Globe,
  Search,
  Settings,
  Shield,
  Clock,
  Menu,
  X,
} from 'lucide-react';

import Logo from '../ui/Logo';
import NavItem from '../ui/NavItem';
import IconButton from '../ui/IconButton';
import Card from '../ui/Card';
import HomePage from '../../pages/HomePage';
import DnsResolutionPage from '../../pages/DnsResolutionPage';
import HistoryPage from '../../pages/HistoryPage';
import DnsPoisoningPage from '../../pages/DnsPoisoningPage';
import DnssecPage from '../../pages/DnssecPage';
import DnsVsDohPage from '../../pages/DnsVsDohPage';


const AppLayout = () => {
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [activeItem, setActiveItem] = useState('home');

  const navigationItems = [
    {
      icon: Home,
      label: 'Accueil',
      id: 'home',
    },
    {
      icon: Globe,
      label: 'Résolution DNS',
      id: 'resolution',
    },
    {
      icon: Shield,
      label: 'Poisoning DNS',
      id: 'dnsPoisoning',
    },
    
    {
      icon: Shield,
      label: 'DNSSEC',
      id: 'dnssec',
    },
    {
      icon: Shield,
      label: 'DNS vs DNS over HTTPS',
      id: 'doh',
    },
    {
      icon: Clock,
      label: 'Historique',
      id: 'history',
    },
    {
      icon: Settings,
      label: 'Paramètres',
      id: 'settings',
    },
  ];

  // Fermer le menu avec Escape
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setSidebarOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, []);

  // Bloquer le scroll derrière le menu mobile
  useEffect(() => {
    document.body.style.overflow = isSidebarOpen ? 'hidden' : '';

    return () => {
      document.body.style.overflow = '';
    };
  }, [isSidebarOpen]);

  const handleNavigation = (id) => {
    setActiveItem(id);
    setSidebarOpen(false);
  };

  const renderPage = () => {
    switch (activeItem) {
      case 'home':
        return <HomePage />;
      case 'resolution':
        return <DnsResolutionPage />;
      case 'history':
        return <HistoryPage />;
      case 'dnsPoisoning':
        return <DnsPoisoningPage />;
      case 'dnssec':
        return <DnssecPage />;
      case 'doh':
        return <DnsVsDohPage />;
      default:
        return <HomePage />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary-50 via-white to-primary-50">

      {/* =========================
          MOBILE HEADER
      ========================== */}
      <header
        className="
          lg:hidden
          fixed top-0 left-0 right-0 z-50
          h-16
          bg-white/90 backdrop-blur-md
          border-b border-secondary-200
        "
      >
        <div className="h-full px-4 flex items-center justify-between">
          <Logo size="sm" />

          <IconButton
            icon={isSidebarOpen ? X : Menu}
            onClick={() => setSidebarOpen((previous) => !previous)}
            ariaLabel={
              isSidebarOpen
                ? 'Fermer le menu'
                : 'Ouvrir le menu'
            }
            title={
              isSidebarOpen
                ? 'Fermer le menu'
                : 'Ouvrir le menu'
            }
            variant="ghost"
          />
        </div>
      </header>

      {/* =========================
          MOBILE OVERLAY
      ========================== */}
      {isSidebarOpen && (
        <div
          className="
            lg:hidden
            fixed inset-0 z-40
            bg-black/40
            backdrop-blur-sm
          "
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* =========================
          APPLICATION LAYOUT
      ========================== */}
      <div className="min-h-screen lg:flex">

        {/* =========================
            SIDEBAR
        ========================== */}
        <aside
          className={`
            fixed lg:sticky
            top-0 left-0
            z-50
            h-screen
            w-72
            shrink-0
            bg-white/95
            backdrop-blur-md
            border-r border-secondary-200

            flex flex-col

            transition-transform duration-300 ease-out

            ${
              isSidebarOpen
                ? 'translate-x-0'
                : '-translate-x-full lg:translate-x-0'
            }
          `}
        >

          {/* Logo */}
          <div className="px-6 py-6 border-b border-secondary-200">
            <Logo size="lg" />
          </div>

          {/* Navigation */}
          <nav
            className="flex-1 overflow-y-auto px-4 py-6"
            aria-label="Navigation principale"
          >
            <div className="space-y-1.5">
              {navigationItems.map((item) => (
                <NavItem
                  key={item.id}
                  icon={item.icon}
                  label={item.label}
                  isActive={activeItem === item.id}
                  onClick={() => handleNavigation(item.id)}
                  aria-current={
                    activeItem === item.id
                      ? 'page'
                      : undefined
                  }
                />
              ))}
            </div>
          </nav>

          {/* Information */}
          <div className="p-4 border-t border-secondary-200">
            <Card
              variant="flat"
              padding="sm"
              className="bg-primary-50/70 border-primary-100"
            >
              <div className="space-y-1">
                <p className="text-xs font-semibold text-primary-700">
                  Simulateur de sécurité DNS
                </p>

                <p className="text-xs text-secondary-500 leading-relaxed">
                  Explorez les mécanismes du DNS de manière interactive.
                </p>
              </div>
            </Card>
          </div>

        </aside>

        {/* =========================
            MAIN CONTENT
        ========================== */}
        <main
          className="
            flex-1
            min-w-0
            pt-16 lg:pt-0
          "
        >
          <div
            className="
              w-full
              px-4
              sm:px-6
              lg:px-8
              xl:px-10
              py-6
              lg:py-8
            "
          >
            {renderPage()}
          </div>
        </main>

      </div>
    </div>
  );
};

export default React.memo(AppLayout);