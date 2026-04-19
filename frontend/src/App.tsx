import { Route, Routes } from 'react-router-dom'
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

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/home" element={<LandingPage />} />
      <Route path="/register" element={<RegisterFirm />} />
      <Route path="/onboard/:firmSlug" element={<ClientSelfRegister />} />
      <Route path="/login" element={<Login />} />
      <Route path="/clients" element={<ClientList />} />
      <Route path="/clients/new" element={<NewClient />} />
      <Route path="/clients/:id" element={<ClientDetail />} />
      <Route path="/settings" element={<FirmSettings />} />
      <Route path="/portal/:firmSlug/:token" element={<DocumentPortal />} />
    </Routes>
  )
}
