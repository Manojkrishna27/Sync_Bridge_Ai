import React, { useState, useEffect } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import CommandPalette from './CommandPalette';
import { Building2, Layers, Key, PlaySquare, History, Sparkles, LogOut, Menu, X, Activity, Cpu, Bot, ShieldCheck, Search } from 'lucide-react';

const SidebarItem = ({ to, icon: Icon, label, isActive }) => (
  <Link
    to={to}
    className={`flex items-center space-x-3 rounded-xl px-4 py-2.5 text-sm font-medium transition-all ${
      isActive 
        ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-semibold shadow-sm' 
        : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
    }`}
  >
    <Icon className="h-4 w-4 shrink-0" />
    <span>{label}</span>
  </Link>
);

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const navItems = [
    { to: '/', icon: Activity, label: 'Dashboard' },
    { to: '/clients', icon: Building2, label: 'Clients' },
    { to: '/integrations', icon: Layers, label: 'Integrations' },
    { to: '/integrations/studio', icon: Sparkles, label: 'Visual Studio' },
    { to: '/integrations/playground', icon: PlaySquare, label: 'Playground' },
    { to: '/integrations/history', icon: History, label: 'Execution History' },
    { to: '/monitoring', icon: Cpu, label: 'Monitoring & Health' },
    { to: '/copilot', icon: Bot, label: 'AI Copilot' },
    { to: '/admin', icon: ShieldCheck, label: 'Administration' },
    { to: '/apikeys', icon: Key, label: 'API Keys' },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans overflow-hidden">
      
      {/* Mobile Menu Header */}
      <div className="fixed top-0 left-0 z-50 flex h-16 w-full items-center justify-between bg-slate-900 border-b border-slate-800 px-4 md:hidden">
        <span className="text-lg font-bold text-white">SyncBridge AI</span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsCommandPaletteOpen(true)}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
          >
            <Search className="w-5 h-5" />
          </button>
          <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="text-slate-400">
            {isMobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </div>

      {/* Sidebar Navigation */}
      <aside className={`fixed inset-y-0 left-0 z-40 w-64 transform border-r border-slate-800/80 bg-slate-900/90 backdrop-blur-xl transition-transform duration-300 md:relative md:translate-x-0 ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex h-full flex-col justify-between">
          <div>
            <div className="hidden h-16 items-center px-6 md:flex border-b border-slate-800/80 justify-between">
              <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-400 bg-clip-text text-transparent">
                SyncBridge AI
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">
                v2.4
              </span>
            </div>

            {/* Quick Search Cmd+K Trigger */}
            <div className="px-4 pt-4">
              <button
                onClick={() => setIsCommandPaletteOpen(true)}
                className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 hover:border-slate-700 text-xs text-slate-400 hover:text-slate-200 transition-all"
              >
                <div className="flex items-center gap-2">
                  <Search className="w-3.5 h-3.5 text-slate-500" />
                  <span>Search commands...</span>
                </div>
                <kbd className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                  ⌘K
                </kbd>
              </button>
            </div>
            
            <nav className="space-y-1 p-4 overflow-y-auto max-h-[calc(100vh-220px)]">
              {navItems.map(item => (
                <SidebarItem 
                  key={item.to}
                  {...item}
                  isActive={location.pathname === item.to || (item.to !== '/' && item.to !== '/integrations' && location.pathname.startsWith(item.to))}
                />
              ))}
            </nav>
          </div>

          <div className="border-t border-slate-800/80 p-4 bg-slate-900/50">
            <div className="mb-3 px-2 text-xs text-slate-400">
              <p className="font-semibold text-slate-200">{user?.first_name || 'Admin'} {user?.last_name || 'User'}</p>
              <p className="text-[10px] font-mono uppercase mt-0.5 text-blue-400">{user?.role?.name || 'Super Admin'}</p>
            </div>
            <button 
              onClick={logout}
              className="flex w-full items-center space-x-3 rounded-xl px-3.5 py-2 text-xs font-medium text-slate-400 transition-all hover:bg-red-500/10 hover:text-red-400 border border-transparent hover:border-red-500/30"
            >
              <LogOut className="h-4 w-4 shrink-0" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto bg-slate-950 p-4 pt-20 md:p-6">
        <div className="mx-auto max-w-7xl">
          <Outlet />
        </div>
      </main>

      {/* Command Palette Modal */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
      />
    </div>
  );
}
