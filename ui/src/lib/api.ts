const API_BASE = '/api'

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`)
  return res.json()
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`)
  return res.json()
}

export async function apiDelete<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`)
  return res.json()
}

export interface StatusData {
  mode: string
  running: boolean
  models: { total_models: number; total_size_display: string }
  provider: string
  provider_healthy: boolean
  ui_enabled: boolean
  auth_enabled: boolean
  version: string
}

export interface ModelData {
  id: number
  name: string
  display_name: string
  path: string
  model_type: string
  architecture: string | null
  parameter_count: string | null
  context_length: number
  size_bytes: number
  size_display: string
  quant: string | null
  tags: string[]
  capabilities: Record<string, boolean>
  is_pinned: boolean
  download_date: string | null
  last_used: string | null
  use_count: number
  library_info?: {
    description: string
    category: string
    recommended_ram: string
    quantizations: string[]
    url: string
  }
}

export interface LibraryModel {
  name: string
  display_name: string
  description: string
  architecture: string
  parameter_count: string
  context_length: number
  quantizations: string[]
  tags: string[]
  capabilities: Record<string, boolean>
  category: string
  recommended_ram: string
  size_estimates: Record<string, number>
}

export interface ProviderData {
  name: string
  provider_type: string
  is_enabled: boolean
  priority: number
  base_url: string | null
  default_model: string | null
  config: Record<string, unknown>
}

export interface ConversationData {
  id: number
  title: string
  model: string
  provider: string
  mode: string
  created_at: string
  updated_at: string
  message_count: number
}

export interface MessageData {
  id: number
  conversation_id: number
  role: string
  content: string
  created_at: string
  tokens_in: number | null
  tokens_out: number | null
}

export const api = {
  status: () => apiGet<StatusData>('/status'),
  health: () => apiGet<{ status: string }>('/health'),

  models: {
    list: () => apiGet<{ models: ModelData[]; total: number }>('/models'),
    get: (name: string) => apiGet<ModelData>(`/models/${name}`),
    delete: (name: string) => apiDelete<{ status: string }>(`/models/${name}`),
    library: (query?: string) =>
      apiGet<{ models: LibraryModel[]; total: number }>(`/models/library?query=${query || ''}`),
    search: (query: string) =>
      apiGet<{ results: LibraryModel[]; total: number }>(`/models/search?query=${query}`),
    categories: () =>
      apiGet<{ categories: string[]; tags: string[] }>('/models/categories'),
    pull: (name: string, quantization = 'Q4_K_M') =>
      apiPost<{ name: string; status: string; path?: string }>('/pull', { name, quantization }),
  },

  providers: {
    list: () => apiGet<{ providers: ProviderData[]; total: number }>('/providers'),
    types: () => apiGet<{ types: string[] }>('/providers/types'),
    add: (data: Partial<ProviderData>) =>
      apiPost<{ status: string; provider: string }>('/providers', data),
    delete: (name: string) => apiDelete<{ status: string }>(`/providers/${name}`),
  },

  conversations: {
    list: () => apiGet<{ conversations: ConversationData[]; total: number }>('/conversations'),
    create: (data?: Partial<ConversationData>) =>
      apiPost<ConversationData>('/conversations', data),
    get: (id: number) => apiGet<ConversationData>(`/conversations/${id}`),
    delete: (id: number) => apiDelete<{ status: string }>(`/conversations/${id}`),
    messages: (id: number) =>
      apiGet<{ messages: MessageData[]; total: number }>(`/conversations/${id}/messages`),
    addMessage: (id: number, msg: { role: string; content: string }) =>
      apiPost<MessageData>(`/conversations/${id}/messages`, msg),
  },

  config: {
    get: () => apiGet<Record<string, unknown>>('/config'),
    update: (data: Record<string, unknown>) =>
      apiPost<{ status: string }>('/config', data),
  },
}

export function chatStream(
  model: string,
  messages: { role: string; content: string }[],
  onChunk: (text: string) => void,
  onDone: () => void,
  onError: (err: string) => void,
  signal?: AbortSignal,
) {
  fetch('/api/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, messages, stream: true }),
    signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        onError(`HTTP ${res.status}: ${res.statusText}`)
        return
      }
      const reader = res.body?.getReader()
      if (!reader) {
        onError('No response body')
        return
      }
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              onDone()
              return
            }
            try {
              const parsed = JSON.parse(data)
              const content = parsed.choices?.[0]?.delta?.content
              if (content) onChunk(content)
              if (parsed.choices?.[0]?.finish_reason) onDone()
            } catch {
              // ignore parse errors
            }
          }
        }
      }
      onDone()
    })
    .catch((err) => {
      if (err.name !== 'AbortError') onError(err.message)
    })
}
