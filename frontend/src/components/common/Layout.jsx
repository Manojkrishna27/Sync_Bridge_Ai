import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Building2, Layers, Key, PlaySquare, History, Sparkles, LogOut, Menu, X, Activity, Cpu, Bot, ShieldCheck } from 'lucide-react';

const SidebarItem = ({ to, icon: Icon, label, isActive }) => (
  <Link
    to={to}
    className={`flex items-center space-x-3 rounded-lg px-4 py-3 transition-colors ${
      isActive 
        ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-400 font-bold' 
        : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800 font-medium'
    }`}
  >
    <Icon className="h-5 w-5" />
    <span>{label}</span>
  </Link>
);

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

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
    <div className="flex h-screen bg-slate-50 dark:bg-slate-900">
      
      {/* Mobile Menu Button */}
      <div className="fixed top-0 left-0 z-50 flex h-16 w-full items-center justify-between bg-white px-4 shadow-sm dark:bg-slate-900 md:hidden">
        <span className="text-xl font-bold text-slate-800 dark:text-white">SyncBridge</span>
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="text-slate-500 dark:text-slate-400">
          {isMobileMenuOpen ? <X /> : <Menu />}
        </button>
      </div>

      {/* Sidebar Navigation */}
      <aside className={`fixed inset-y-0 left-0 z-40 w-64 transform border-r border-slate-200 bg-white transition-transform duration-300 dark:border-slate-800 dark:bg-slate-900 md:relative md:translate-x-0 ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex h-full flex-col">
          <div className="hidden h-16 items-center px-6 md:flex border-b border-slate-200 dark:border-slate-800">
            <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text text-transparent">SyncBridge AI</h1>
          </div>
          
          <nav className="flex-1 space-y-1.5 overflow-y-auto p-4 mt-16 md:mt-0">
            {navItems.map(item => (
              <SidebarItem 
                key={item.to}
                {...item}
                isActive={location.pathname === item.to || (item.to !== '/' && item.to !== '/integrations' && location.pathname.startsWith(item.to))}
              />
            ))}
          </nav>

          <div className="border-t border-slate-200 p-4 dark:border-slate-800">
            <div className="mb-4 px-4 text-sm text-slate-500 dark:text-slate-400">
              <p className="font-medium text-slate-800 dark:text-slate-200">{user?.first_name || 'Admin'} {user?.last_name || 'User'}</p>
              <p className="text-xs uppercase mt-1 text-indigo-500">{user?.role?.name || 'Super Admin'}</p>
            </div>
            <button 
              onClick={logout}
              className="flex w-full items-center space-x-3 rounded-lg px-4 py-2 text-slate-600 transition-colors hover:bg-slate-50 hover:text-red-600 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-red-400"
            >
              <LogOut className="h-5 w-5" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto bg-slate-50 p-4 pt-20 md:p-8 dark:bg-slate-950">
        <div className="mx-auto max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
