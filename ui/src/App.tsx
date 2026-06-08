import { useState } from 'react'
import { Routes, Route, Navigate, useSearchParams } from 'react-router-dom'
import { useThemeStore } from './hooks/useThemeStore'
import Sidebar from './components/Sidebar'
import ChatPage from './pages/ChatPage'
import ModelsPage from './pages/ModelsPage'
import ModelDetailPage from './pages/ModelDetailPage'
import LibraryPage from './pages/LibraryPage'
import ProvidersPage from './pages/ProvidersPage'
import SettingsPage from './pages/SettingsPage'
import StatusPage from './pages/StatusPage'

function HomeRedirect() {
  const [searchParams] = useSearchParams()
  const model = searchParams.get('model')
  const path = model ? `/chat?model=${encodeURIComponent(model)}` : '/chat'
  return <Navigate to={path} replace />
}

export default function App() {
  const { theme } = useThemeStore()
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  return (
    <div className={theme === 'dark' ? 'dark' : ''}>
      <div className="flex h-screen bg-white dark:bg-neutral-950">
        <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(v => !v)} />
        <main className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<HomeRedirect />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/chat/:id" element={<ChatPage />} />
            <Route path="/models" element={<ModelsPage />} />
            <Route path="/models/:name" element={<ModelDetailPage />} />
            <Route path="/library" element={<LibraryPage />} />
            <Route path="/providers" element={<ProvidersPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/status" element={<StatusPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
