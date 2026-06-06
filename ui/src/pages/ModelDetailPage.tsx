import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Cpu, Memory, BookOpen } from 'lucide-react'
import { api } from '../lib/api'

export default function ModelDetailPage() {
  const { name } = useParams<{ name: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['model', name],
    queryFn: () => api.models.get(name!),
    enabled: !!name,
  })

  const deleteMutation = useMutation({
    mutationFn: () => api.models.delete(name!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] })
      navigate('/models')
    },
  })

  if (isLoading) return <div className="p-6">Loading...</div>
  if (error || !data)
    return (
      <div className="p-6">
        <button onClick={() => navigate('/models')} className="btn-secondary mb-4">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <p className="text-red-500">Model not found</p>
      </div>
    )

  const lib = data.library_info

  return (
    <div className="p-6 overflow-y-auto h-full">
      <div className="max-w-3xl mx-auto">
        <button onClick={() => navigate('/models')} className="btn-secondary mb-4">
          <ArrowLeft className="w-4 h-4" /> Back to Models
        </button>

        <div className="card p-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold">{data.display_name}</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400 font-mono">
                {data.name}
              </p>
            </div>
            <button
              onClick={() => deleteMutation.mutate()}
              className="btn-secondary !text-red-500"
            >
              Delete Model
            </button>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                <Cpu className="w-4 h-4" /> Parameters
              </div>
              <p className="font-semibold">{data.parameter_count || 'Unknown'}</p>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                <Memory className="w-4 h-4" /> Size
              </div>
              <p className="font-semibold">{data.size_display}</p>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                <BookOpen className="w-4 h-4" /> Context
              </div>
              <p className="font-semibold">{data.context_length} tokens</p>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                Architecture
              </div>
              <p className="font-semibold">{data.architecture || 'Unknown'}</p>
            </div>
          </div>

          {lib && (
            <>
              <h2 className="font-semibold mb-2">About</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                {lib.description}
              </p>

              <div className="flex flex-wrap gap-2 mb-4">
                <span className="px-3 py-1 text-xs rounded-full bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-300 capitalize">
                  {lib.category}
                </span>
                <span className="px-3 py-1 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400">
                  RAM: {lib.recommended_ram}
                </span>
              </div>

              {lib.quantizations && (
                <div>
                  <h3 className="text-sm font-semibold mb-2">Available Quantizations</h3>
                  <div className="flex flex-wrap gap-2">
                    {lib.quantizations.map((q) => (
                      <span
                        key={q}
                        className={`px-3 py-1 text-xs rounded-full ${
                          q === data.quant
                            ? 'bg-brand-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                        }`}
                      >
                        {q}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {data.tags && data.tags.length > 0 && (
            <div className="mt-4">
              <h3 className="text-sm font-semibold mb-2">Tags</h3>
              <div className="flex flex-wrap gap-1">
                {data.tags.map((tag: string) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {data.capabilities && Object.keys(data.capabilities).length > 0 && (
            <div className="mt-4">
              <h3 className="text-sm font-semibold mb-2">Capabilities</h3>
              <div className="flex flex-wrap gap-2">
                {Object.entries(data.capabilities)
                  .filter(([, v]) => v)
                  .map(([k]) => (
                    <span
                      key={k}
                      className="px-3 py-1 text-xs rounded-full bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 capitalize"
                    >
                      {k}
                    </span>
                  ))}
              </div>
            </div>
          )}

          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-400">
            <p>Path: {data.path}</p>
            <p>Downloaded: {data.download_date || 'N/A'}</p>
            <p>Last used: {data.last_used || 'Never'}</p>
            <p>Uses: {data.use_count}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
