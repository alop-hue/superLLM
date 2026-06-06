import { useState, useEffect } from 'react'
import { Settings, Save } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['config'],
    queryFn: () => api.config.get(),
  })

  const [form, setForm] = useState<Record<string, unknown>>({})

  useEffect(() => {
    if (data) setForm(data as Record<string, unknown>)
  }, [data])

  const mutation = useMutation({
    mutationFn: (vals: Record<string, unknown>) => api.config.update(vals),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['config'] }),
  })

  const handleChange = (key: string, value: unknown) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const handleSave = () => {
    mutation.mutate(form)
  }

  return (
    <div className="p-6 overflow-y-auto h-full">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Settings className="w-6 h-6" />
          <h1 className="text-xl font-semibold">Settings</h1>
        </div>

        {isLoading && <div className="text-center py-10 text-gray-400">Loading...</div>}

        {data && (
          <div className="card p-6 space-y-4">
            <SettingRow
              label="Mode"
              desc="Local, Cloud, or Hybrid"
              value={String(form.mode || '')}
              onChange={(v) => handleChange('mode', v)}
              options={['local', 'cloud', 'hybrid']}
            />
            <SettingRow
              label="Host"
              desc="Server bind address"
              value={String(form.host || '')}
              onChange={(v) => handleChange('host', v)}
            />
            <SettingRow
              label="Port"
              desc="Server port"
              value={String(form.port || '')}
              onChange={(v) => handleChange('port', parseInt(v))}
              type="number"
            />
            <SettingRow
              label="Default Model"
              desc="Model used for chat by default"
              value={String(form.default_model || '')}
              onChange={(v) => handleChange('default_model', v)}
            />
            <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
              <div>
                <label className="text-sm font-medium">Local Inference</label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Run models on this machine
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={Boolean(form.local_inference)}
                  onChange={(e) => handleChange('local_inference', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-brand-300 dark:peer-focus:ring-brand-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-brand-600" />
              </label>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium">Cloud Routing</label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Route requests to cloud providers
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={Boolean(form.cloud_routing)}
                  onChange={(e) => handleChange('cloud_routing', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-brand-300 dark:peer-focus:ring-brand-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-brand-600" />
              </label>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium">Cloud Fallback</label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Fall back to cloud if local inference fails
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={Boolean(form.cloud_fallback)}
                  onChange={(e) => handleChange('cloud_fallback', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-brand-300 dark:peer-focus:ring-brand-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-brand-600" />
              </label>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium">Auth Enabled</label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Require API key for requests
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={Boolean(form.auth_enabled)}
                  onChange={(e) => handleChange('auth_enabled', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-brand-300 dark:peer-focus:ring-brand-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-brand-600" />
              </label>
            </div>

            <button
              onClick={handleSave}
              disabled={mutation.isPending}
              className="btn-primary mt-4"
            >
              <Save className="w-4 h-4" />
              {mutation.isPending ? 'Saving...' : 'Save Settings'}
            </button>
            {mutation.isSuccess && (
              <p className="text-xs text-green-500">Settings saved.</p>
            )}
            {mutation.isError && (
              <p className="text-xs text-red-500">
                {(mutation.error as Error).message}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function SettingRow({
  label,
  desc,
  value,
  onChange,
  type = 'text',
  options,
}: {
  label: string
  desc: string
  value: string
  onChange: (v: string) => void
  type?: string
  options?: string[]
}) {
  return (
    <div>
      <label className="text-sm font-medium">{label}</label>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{desc}</p>
      {options ? (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="input"
        >
          {options.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
      ) : (
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="input"
        />
      )}
    </div>
  )
}
