import { Server, Plus, Trash2 } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, type ProviderData } from '../lib/api'

export default function ProvidersPage() {
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['providers'],
    queryFn: () => api.providers.list(),
  })

  const { data: types } = useQuery({
    queryKey: ['provider-types'],
    queryFn: () => api.providers.types(),
  })

  const deleteMutation = useMutation({
    mutationFn: (name: string) => api.providers.delete(name),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['providers'] }),
  })

  return (
    <div className="p-6 overflow-y-auto h-full">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Server className="w-6 h-6" />
          <h1 className="text-xl font-semibold">Providers</h1>
        </div>

        {isLoading && (
          <div className="text-center py-10 text-gray-400 dark:text-gray-300">Loading...</div>
        )}

        {data && data.providers.length === 0 && (
          <div className="text-center py-10 text-gray-400 dark:text-gray-300">
            <Server className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No providers configured.</p>
            <p className="text-sm mt-1">
              The local provider is used by default. Add cloud providers to enable routing.
            </p>
          </div>
        )}

        <div className="space-y-3">
          {data?.providers.map((provider: ProviderData) => (
            <div key={provider.name} className="card p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">{provider.name}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-300">
                    {provider.provider_type}
                    {provider.base_url && ` - ${provider.base_url}`}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span
                    className={`px-2 py-0.5 text-xs rounded-full ${
                      provider.is_enabled
                        ? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-300'
                    }`}
                  >
                    {provider.is_enabled ? 'Enabled' : 'Disabled'}
                  </span>
                  <span className="text-xs text-gray-400 dark:text-gray-300">Priority: {provider.priority}</span>
                  <button
                    onClick={() => deleteMutation.mutate(provider.name)}
                    className="btn-secondary !p-2 text-red-500"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              {provider.default_model && (
                <p className="text-xs text-gray-400 dark:text-gray-300 mt-2">
                  Default model: {provider.default_model}
                </p>
              )}
            </div>
          ))}
        </div>

        <div className="card p-4 mt-6">
          <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <Plus className="w-4 h-4" /> Add Provider
          </h2>
          <p className="text-xs text-gray-500 dark:text-gray-300 mb-3">
            Configure providers through the CLI: <code className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded">superllm providers add --name openai --type openai</code>
          </p>
          {types && (
            <div className="flex flex-wrap gap-2">
              {types.types.map((t: string) => (
                <span
                  key={t}
                  className="px-3 py-1 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 capitalize"
                >
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
