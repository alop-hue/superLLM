import { useState } from 'react'
import { BookOpen, Search } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, type LibraryModel } from '../lib/api'
import ModelCard from '../components/ModelCard'

export default function LibraryPage() {
  const queryClient = useQueryClient()
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['library', query],
    queryFn: () => api.models.library(query),
  })

  const { data: categories } = useQuery({
    queryKey: ['model-categories'],
    queryFn: () => api.models.categories(),
  })

  const pullMutation = useMutation({
    mutationFn: (name: string) => api.models.pull(name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] })
    },
  })

  const results = data?.models || []
  const filtered = category
    ? results.filter((m) => m.category === category)
    : results

  return (
    <div className="p-6 overflow-y-auto h-full">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <BookOpen className="w-6 h-6" />
          <h1 className="text-xl font-semibold">Model Library</h1>
        </div>

        <div className="flex gap-2 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search models..."
              className="input pl-10"
            />
          </div>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="input w-40"
          >
            <option value="">All Categories</option>
            {categories?.categories.map((c: string) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        {isLoading && (
          <div className="text-center py-10 text-gray-400">Loading...</div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((model: LibraryModel) => (
            <ModelCard
              key={model.name}
              model={model}
              onDownload={(name) => pullMutation.mutate(name)}
            />
          ))}
        </div>

        {!isLoading && filtered.length === 0 && (
          <div className="text-center py-10 text-gray-400">
            <p>No models found.</p>
          </div>
        )}
      </div>
    </div>
  )
}
