import { Routes, Route, Navigate } from 'react-router-dom'
import { useThemeStore } from './hooks/useThemeStore'
import Sidebar from './components/Sidebar'
import ChatPage from './pages/ChatPage'
import ModelsPage from './pages/ModelsPage'
import ModelDetailPage from './pages/ModelDetailPage'
import LibraryPage from './pages/LibraryPage'
import ProvidersPage from './pages/ProvidersPage'
import SettingsPage from './pages/SettingsPage'
import StatusPage from './pages/StatusPage'

export default function App() {
  const { theme } = useThemeStore()

  return (
    <div className={theme === 'dark' ? 'dark' : ''}>
      <div className="flex h-screen bg-white dark:bg-gray-900">
        <Sidebar />
        <main className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
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
