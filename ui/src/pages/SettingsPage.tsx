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
          <Settings className="w-5 h-5 text-brand-500" />
          <h1 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Settings</h1>
        </div>

        {isLoading && (
          <div className="text-center py-10 text-neutral-400">Loading...</div>
        )}

        {data && (
          <div className="card p-6 space-y-5">
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

            <hr className="border-neutral-200 dark:border-neutral-800" />

            <ToggleRow
              label="Local Inference"
              desc="Run models on this machine"
              checked={Boolean(form.local_inference)}
              onChange={(v) => handleChange('local_inference', v)}
            />
            <ToggleRow
              label="Cloud Routing"
              desc="Route requests to cloud providers"
              checked={Boolean(form.cloud_routing)}
              onChange={(v) => handleChange('cloud_routing', v)}
            />
            <ToggleRow
              label="Cloud Fallback"
              desc="Fall back to cloud if local inference fails"
              checked={Boolean(form.cloud_fallback)}
              onChange={(v) => handleChange('cloud_fallback', v)}
            />
            <ToggleRow
              label="Auth Enabled"
              desc="Require API key for requests"
              checked={Boolean(form.auth_enabled)}
              onChange={(v) => handleChange('auth_enabled', v)}
            />

            <hr className="border-neutral-200 dark:border-neutral-800" />

            <SettingRow
              label="Temperature"
              desc="Response randomness (0.0 – 2.0)"
              value={String(form.temperature ?? '0.7')}
              onChange={(v) => handleChange('temperature', parseFloat(v) || 0.7)}
              type="range"
              min="0"
              max="2"
              step="0.1"
            />
            <SettingRow
              label="Max Tokens"
              desc="Maximum response length"
              value={String(form.max_tokens ?? '2048')}
              onChange={(v) => handleChange('max_tokens', parseInt(v) || 2048)}
              type="number"
            />
            <SettingRow
              label="Context Length"
              desc="Model context window size"
              value={String(form.n_ctx ?? '2048')}
              onChange={(v) => handleChange('n_ctx', parseInt(v) || 2048)}
              type="number"
            />

            <button
              onClick={handleSave}
              disabled={mutation.isPending}
              className="btn-primary w-full"
            >
              <Save className="w-4 h-4" />
              {mutation.isPending ? 'Saving...' : 'Save Settings'}
            </button>

            {mutation.isSuccess && (
              <p className="text-xs text-green-500 text-center">Settings saved.</p>
            )}
            {mutation.isError && (
              <p className="text-xs text-red-500 text-center">
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
  min, max, step,
}: {
  label: string
  desc: string
  value: string
  onChange: (v: string) => void
  type?: string
  options?: string[]
  min?: string; max?: string; step?: string
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-neutral-800 dark:text-neutral-200">{label}</label>
      <p className="text-xs text-neutral-500 dark:text-neutral-300 mb-1.5">{desc}</p>
      {options ? (
        <select value={value} onChange={(e) => onChange(e.target.value)} className="input">
          {options.map((o) => (
            <option key={o} value={o}>{o}</option>
          ))}
        </select>
      ) : type === 'range' ? (
        <div className="flex items-center gap-3">
          <input
            type="range"
            min={min ?? '0'}
            max={max ?? '1'}
            step={step ?? '0.01'}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="flex-1"
          />
          <span className="text-xs font-mono text-neutral-500 dark:text-neutral-300 w-8 text-right">{value}</span>
        </div>
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

function ToggleRow({
  label, desc, checked, onChange,
}: {
  label: string; desc: string; checked: boolean; onChange: (v: boolean) => void
}) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <label className="text-sm font-medium text-neutral-800 dark:text-neutral-200">{label}</label>
        <p className="text-xs text-neutral-500 dark:text-neutral-300">{desc}</p>
      </div>
      <label className="relative inline-flex items-center cursor-pointer">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          className="toggle"
        />
        <div />
      </label>
    </div>
  )
}
