import { Activity, Server, Box, Cpu, MemoryStick as Memory, HardDrive } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

export default function StatusPage() {
  const { data: status, isLoading: statusLoading } = useQuery({
    queryKey: ['status'],
    queryFn: api.status,
    refetchInterval: 5000,
  })

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: api.health,
    refetchInterval: 5000,
  })

  if (statusLoading) {
    return (
      <div className="p-6">
        <div className="text-center py-10 text-gray-400 dark:text-gray-300">Loading...</div>
      </div>
    )
  }

  return (
    <div className="p-6 overflow-y-auto h-full">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Activity className="w-6 h-6" />
          <h1 className="text-xl font-semibold">Status</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="card p-4">
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-300 mb-2">
              <Server className="w-4 h-4" /> Server
            </div>
            <div className="flex items-center gap-2">
              <span
                className={`w-3 h-3 rounded-full ${
                  status?.running ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="font-semibold">
                {status?.running ? 'Running' : 'Stopped'}
              </span>
            </div>
            <p className="text-xs text-gray-400 dark:text-gray-300 mt-1 capitalize">
              Mode: {status?.mode}
            </p>
          </div>

          <div className="card p-4">
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-300 mb-2">
              <Box className="w-4 h-4" /> Models
            </div>
            <p className="text-2xl font-bold">{status?.models?.total_models || 0}</p>
            <p className="text-xs text-gray-400 dark:text-gray-300 mt-1">
              {status?.models?.total_size_display || '0 B'} total
            </p>
          </div>

          <div className="card p-4">
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-300 mb-2">
              <Activity className="w-4 h-4" /> Provider
            </div>
            <p className="font-semibold capitalize">{status?.provider || 'N/A'}</p>
            <div className="flex items-center gap-1 mt-1">
              <span
                className={`w-2 h-2 rounded-full ${
                  status?.provider_healthy ? 'bg-green-500' : 'bg-yellow-500'
                }`}
              />
              <span className="text-xs text-gray-400 dark:text-gray-300">
                {status?.provider_healthy ? 'Healthy' : 'Unhealthy'}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="card p-4">
            <h2 className="font-semibold mb-3 flex items-center gap-2">
              <Server className="w-4 h-4" /> Server Info
            </h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-300">Version</span>
                <span>{status?.version || '0.1.0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-300">API Status</span>
                <span className={health?.status === 'healthy' ? 'text-green-500' : 'text-red-500'}>
                  {health?.status || 'unknown'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-300">Auth</span>
                <span>{status?.auth_enabled ? 'Enabled' : 'Disabled'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-300">UI</span>
                <span>{status?.ui_enabled ? 'Enabled' : 'Disabled'}</span>
              </div>
            </div>
          </div>

          <div className="card p-4">
            <h2 className="font-semibold mb-3 flex items-center gap-2">
              <Cpu className="w-4 h-4" /> Hardware
            </h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-300">Platform</span>
                <span>{navigator.platform || 'Unknown'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-300">CPU Cores</span>
                <span>{navigator.hardwareConcurrency || '?'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-300">Memory</span>
                <span>
                  {'deviceMemory' in navigator
                    ? `${(navigator as any).deviceMemory} GB`
                    : 'Unknown'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-300">Connection</span>
                <span>
                  {'connection' in navigator
                    ? (navigator as any).connection?.effectiveType || 'Unknown'
                    : 'Unknown'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
