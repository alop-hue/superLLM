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
  PanelLeftClose,
  PanelLeft,
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

type Props = {
  collapsed: boolean
  onToggle: () => void
}

export default function Sidebar({ collapsed, onToggle }: Props) {
  const { theme, toggle } = useThemeStore()
  const navigate = useNavigate()

  const { data: status } = useQuery({
    queryKey: ['status'],
    queryFn: api.status,
    refetchInterval: 10000,
  })

  return (
    <aside
      className={clsx(
        'border-r border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900/50 flex flex-col transition-all duration-200',
        collapsed ? 'w-16' : 'w-60',
      )}
    >
      <div className="flex items-center justify-between p-3 border-b border-neutral-200 dark:border-neutral-800">
        {!collapsed && (
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-base font-bold"
          >
            <Zap className="w-5 h-5 text-brand-500" />
            <span>superLLM</span>
          </button>
        )}
        {collapsed && (
          <button onClick={() => navigate('/')} className="mx-auto">
            <Zap className="w-5 h-5 text-brand-500" />
          </button>
        )}
        <button onClick={onToggle} className="btn-ghost">
          {collapsed ? <PanelLeft className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
        </button>
      </div>

      <nav className="flex-1 p-2 space-y-0.5">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'sidebar-link',
                isActive ? 'sidebar-link-active' : 'sidebar-link-inactive',
                collapsed && 'justify-center px-2',
              )
            }
            title={collapsed ? label : undefined}
          >
            <Icon className="w-5 h-5 shrink-0" />
            {!collapsed && <span className="truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="p-2 border-t border-neutral-200 dark:border-neutral-800 space-y-1">
        <button
          onClick={toggle}
          className={clsx('sidebar-link sidebar-link-inactive w-full', collapsed && 'justify-center px-2')}
          title={theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          {!collapsed && <span>{theme === 'dark' ? 'Light' : 'Dark'}</span>}
        </button>

        {!collapsed && status && (
          <div className="px-3 py-2 text-xs text-neutral-500 dark:text-neutral-300">
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
