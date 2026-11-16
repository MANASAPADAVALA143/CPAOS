import { Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ClientDetail from './pages/ClientDetail'
import NewClient from './pages/NewClient'
import DocumentPortal from './pages/DocumentPortal'
import FirmSettings from './pages/FirmSettings'
import ClientList from './pages/ClientList'
import RegisterFirm from './pages/RegisterFirm'
import ClientSelfRegister from './pages/ClientSelfRegister'
import AssignmentList from './pages/AssignmentList'

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/home" element={<LandingPage />} />
      <Route path="/register" element={<RegisterFirm />} />
      <Route path="/login" element={<Login />} />
      <Route path="/onboard/:firmSlug" element={<ClientSelfRegister />} />
      <Route path="/portal/:firmSlug/:token" element={<DocumentPortal />} />
      
      {/* Authenticated routes with Layout */}
      <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
      <Route path="/clients" element={<Layout><ClientList /></Layout>} />
      <Route path="/clients/new" element={<Layout><NewClient /></Layout>} />
      <Route path="/clients/:id" element={<Layout><ClientDetail /></Layout>} />
      <Route path="/settings" element={<Layout><FirmSettings /></Layout>} />
      
      {/* Assignment routes - Phase 1 */}
      <Route path="/assignments" element={<Layout><AssignmentList /></Layout>} />
      <Route path="/my-tasks" element={<Layout><div className="p-8 text-slate-400">My Tasks - Coming soon</div></Layout>} />
      <Route path="/review-queue" element={<Layout><div className="p-8 text-slate-400">Review Queue - Coming soon</div></Layout>} />
    </Routes>
  )
}
