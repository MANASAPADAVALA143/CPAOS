import { Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import PracticeDashboard from './pages/PracticeDashboard'
import ClientDetail from './pages/ClientDetail'
import NewClient from './pages/NewClient'
import DocumentPortal from './pages/DocumentPortal'
import FirmSettings from './pages/FirmSettings'
import ClientList from './pages/ClientList'
import RegisterFirm from './pages/RegisterFirm'
import ClientSelfRegister from './pages/ClientSelfRegister'
import AssignmentList from './pages/AssignmentList'
import AssignmentDetail from './pages/AssignmentDetail'
import MyTasks from './pages/MyTasks'
import ReviewQueue from './pages/ReviewQueue'
import ComplianceDashboard from './pages/ComplianceDashboard'
import ComplianceCalendar from './pages/ComplianceCalendar'
import BillingDashboard from './pages/BillingDashboard'
import { AuditDashboard } from './pages/AuditDashboard'
import { AccountingDashboard } from './pages/AccountingDashboard'

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
      <Route path="/dashboard" element={<Layout><PracticeDashboard /></Layout>} />
      <Route path="/dashboard/onboarding" element={<Layout><Dashboard /></Layout>} />
      <Route path="/clients" element={<Layout><ClientList /></Layout>} />
      <Route path="/clients/new" element={<Layout><NewClient /></Layout>} />
      <Route path="/clients/:id" element={<Layout><ClientDetail /></Layout>} />
      <Route path="/settings" element={<Layout><FirmSettings /></Layout>} />
      
      {/* Assignment routes - Phase 1 */}
      <Route path="/assignments" element={<Layout><AssignmentList /></Layout>} />
      <Route path="/assignments/:id" element={<Layout><AssignmentDetail /></Layout>} />
      <Route path="/my-tasks" element={<Layout><MyTasks /></Layout>} />
      <Route path="/review-queue" element={<Layout><ReviewQueue /></Layout>} />
      
      {/* Compliance routes - Phase 2 */}
      <Route path="/compliance/dashboard" element={<Layout><ComplianceDashboard /></Layout>} />
      <Route path="/compliance" element={<Layout><ComplianceCalendar /></Layout>} />
      
      {/* Billing routes - Phase 3 */}
      <Route path="/billing" element={<Layout><BillingDashboard /></Layout>} />
      
      {/* Audit routes - Phase 4 */}
      <Route path="/audit/dashboard" element={<Layout><AuditDashboard /></Layout>} />
      
      {/* Accounting routes - Phase 4 */}
      <Route path="/accounting/dashboard" element={<Layout><AccountingDashboard /></Layout>} />
    </Routes>
  )
}
