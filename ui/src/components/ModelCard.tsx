import { useNavigate } from 'react-router-dom'
import { Download, Trash2, Cpu, Memory } from 'lucide-react'
import type { ModelData, LibraryModel } from '../lib/api'

type Props = {
  model: ModelData | LibraryModel
  isInstalled?: boolean
  onDelete?: (name: string) => void
  onDownload?: (name: string) => void
}

export default function ModelCard({ model, isInstalled, onDelete, onDownload }: Props) {
  const navigate = useNavigate()
  const caps = 'capabilities' in model ? model.capabilities : {}
  const tags = 'tags' in model ? model.tags : []

  return (
    <div
      className="card p-4 cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => navigate(`/models/${model.name}`)}
    >
      <div className="flex items-start justify-between mb-2">
        <div>
          <h3 className="font-semibold">{model.display_name || model.name}</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 font-mono">
            {model.name}
          </p>
        </div>
        <div className="flex gap-1">
          {!isInstalled && onDownload && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onDownload(model.name)
              }}
              className="btn-secondary !p-2"
              title="Download"
            >
              <Download className="w-4 h-4" />
            </button>
          )}
          {isInstalled && onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onDelete(model.name)
              }}
              className="btn-secondary !p-2 text-red-500"
              title="Delete"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 mb-2">
        <span className="flex items-center gap-1">
          <Cpu className="w-3 h-3" />
          {'parameter_count' in model ? model.parameter_count : '-'}
        </span>
        <span className="flex items-center gap-1">
          <Memory className="w-3 h-3" />
          {'recommended_ram' in model ? model.recommended_ram : '-'}
        </span>
        {'size_display' in model && model.size_display && (
          <span>{model.size_display}</span>
        )}
        {'context_length' in model && (
          <span>{model.context_length} ctx</span>
        )}
      </div>

      <div className="flex flex-wrap gap-1">
        {Object.entries(caps)
          .filter(([, v]) => v)
          .map(([k]) => (
            <span
              key={k}
              className="px-2 py-0.5 text-xs rounded-full bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-300 capitalize"
            >
              {k}
            </span>
          ))}
        {tags.slice(0, 3).map((tag) => (
          <span
            key={tag}
            className="px-2 py-0.5 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  )
}
