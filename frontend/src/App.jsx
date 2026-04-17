import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import BaseDetail from './pages/BaseDetail'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/base/:nome" element={<BaseDetail />} />
    </Routes>
  )
}
