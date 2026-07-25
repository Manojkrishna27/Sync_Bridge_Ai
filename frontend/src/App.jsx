import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './pages/Auth/Login';
import ProtectedRoute from './components/common/ProtectedRoute';
import Layout from './components/common/Layout';

import DashboardOverview from './pages/Dashboard/Overview';
import ClientList from './pages/Clients/ClientList';
import ClientDetail from './pages/Clients/ClientDetail';
import IntegrationList from './pages/Integrations/IntegrationList';
import IntegrationDetail from './pages/Integrations/IntegrationDetail';
import Playground from './pages/Integrations/Playground';
import ExecutionHistory from './pages/Integrations/ExecutionHistory';
import VisualStudio from './pages/Integrations/VisualStudio';
import MonitoringDashboard from './pages/Monitoring/MonitoringDashboard';
import CopilotChat from './pages/Copilot/CopilotChat';
import AdminDashboard from './pages/Admin/AdminDashboard';

function Unauthorized() {
  return (
    <div className="flex h-screen items-center justify-center dark:text-white">
      <h1 className="text-3xl font-bold">403 - Unauthorized Access</h1>
    </div>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/unauthorized" element={<Unauthorized />} />
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<DashboardOverview />} />
        <Route path="dashboard" element={<DashboardOverview />} />
        <Route path="clients" element={<ClientList />} />
        <Route path="clients/:id" element={<ClientDetail />} />
        <Route path="integrations" element={<IntegrationList />} />
        <Route path="integrations/studio" element={<VisualStudio />} />
        <Route path="integrations/playground" element={<Playground />} />
        <Route path="integrations/history" element={<ExecutionHistory />} />
        <Route path="integrations/:id" element={<IntegrationDetail />} />
        <Route path="monitoring" element={<MonitoringDashboard />} />
        <Route path="copilot" element={<CopilotChat />} />
        <Route path="admin" element={<AdminDashboard />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
