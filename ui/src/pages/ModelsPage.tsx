import { useState } from 'react'
import { Box, Download } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, type ModelData } from '../lib/api'
import ModelCard from '../components/ModelCard'

export default function ModelsPage() {
  const queryClient = useQueryClient()
  const [pullName, setPullName] = useState('')
  const [pullQuant, setPullQuant] = useState('Q4_K_M')

  const { data, isLoading, error } = useQuery({
    queryKey: ['models'],
    queryFn: () => api.models.list(),
  })

  const deleteMutation = useMutation({
    mutationFn: (name: string) => api.models.delete(name),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['models'] }),
  })

  const pullMutation = useMutation({
    mutationFn: (name: string) => api.models.pull(name, pullQuant),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] })
      setPullName('')
    },
  })

  const handleDelete = (name: string) => {
    if (confirm(`Delete model '${name}'?`)) {
      deleteMutation.mutate(name)
    }
  }

  const handlePull = () => {
    if (!pullName.trim()) return
    pullMutation.mutate(pullName.trim())
  }

  return (
    <div className="p-6 overflow-y-auto h-full">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-semibold flex items-center gap-2">
            <Box className="w-5 h-5" />
            Installed Models
          </h1>
        </div>

        <div className="card p-4 mb-6">
          <h2 className="text-sm font-semibold mb-3">Download Model</h2>
          <div className="flex gap-2">
            <input
              type="text"
              value={pullName}
              onChange={(e) => setPullName(e.target.value)}
              placeholder="Model name (e.g., llama-3.2-1b)"
              className="input"
              onKeyDown={(e) => e.key === 'Enter' && handlePull()}
            />
            <select
              value={pullQuant}
              onChange={(e) => setPullQuant(e.target.value)}
              className="input w-32"
            >
              <option value="Q2_K">Q2_K</option>
              <option value="Q4_K_M">Q4_K_M</option>
              <option value="Q5_K_M">Q5_K_M</option>
              <option value="Q8_0">Q8_0</option>
            </select>
            <button
              onClick={handlePull}
              disabled={pullMutation.isPending || !pullName.trim()}
              className="btn-primary"
            >
              <Download className="w-4 h-4" />
              {pullMutation.isPending ? 'Downloading...' : 'Pull'}
            </button>
          </div>
          {pullMutation.isError && (
            <p className="text-xs text-red-500 mt-2">
              {(pullMutation.error as Error).message}
            </p>
          )}
          {pullMutation.isSuccess && (
            <p className="text-xs text-green-500 mt-2">
              {pullMutation.data.status}: {pullMutation.data.name}
            </p>
          )}
        </div>

        {isLoading && (
          <div className="text-center py-10 text-gray-400 dark:text-gray-300">Loading...</div>
        )}

        {error && (
          <div className="card p-4 text-red-500">
            Error loading models: {(error as Error).message}
          </div>
        )}

        {data && data.models.length === 0 && (
          <div className="text-center py-10 text-gray-400 dark:text-gray-400">
            <Box className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No models installed yet.</p>
            <p className="text-sm mt-1">
              Use the form above or run:{' '}
              <code className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs">
                superllm pull llama-3.2-1b
              </code>
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data?.models.map((model: ModelData) => (
            <ModelCard
              key={model.name}
              model={model}
              isInstalled
              onDelete={handleDelete}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
