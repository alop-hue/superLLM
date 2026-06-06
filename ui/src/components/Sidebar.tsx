import { NavLink, useNavigate } from 'react-router-dom'
import {
  MessageSquare,
  Box,
  BookOpen,
  Server,
  Settings,
  Activity,
  Sun,
  Moon,
  Zap,
} from 'lucide-react'
import { useThemeStore } from '../hooks/useThemeStore'
import clsx from 'clsx'
import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

const links = [
  { to: '/chat', icon: MessageSquare, label: 'Chat' },
  { to: '/models', icon: Box, label: 'Models' },
  { to: '/library', icon: BookOpen, label: 'Library' },
  { to: '/providers', icon: Server, label: 'Providers' },
  { to: '/status', icon: Activity, label: 'Status' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
  const { theme, toggle } = useThemeStore()
  const navigate = useNavigate()

  const { data: status } = useQuery({
    queryKey: ['status'],
    queryFn: api.status,
    refetchInterval: 10000,
  })

  return (
    <aside className="w-64 border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 flex flex-col">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-lg font-bold"
        >
          <Zap className="w-6 h-6 text-brand-600" />
          <span>superLLM</span>
        </button>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'sidebar-link',
                isActive ? 'sidebar-link-active' : 'sidebar-link-inactive',
              )
            }
          >
            <Icon className="w-5 h-5" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
        <button
          onClick={toggle}
          className="sidebar-link sidebar-link-inactive w-full"
        >
          {theme === 'dark' ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
          {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </button>

        {status && (
          <div className="px-3 py-2 text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-2">
              <span
                className={clsx(
                  'w-2 h-2 rounded-full',
                  status.running ? 'bg-green-500' : 'bg-red-500',
                )}
              />
              {status.running ? 'Running' : 'Stopped'}
              <span className="ml-auto capitalize">{status.mode}</span>
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}
