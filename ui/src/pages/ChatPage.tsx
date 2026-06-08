import { useState, useRef, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { MessageSquare, ChevronDown, Trash2, Bot } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { api, chatStream, type ModelData, type LibraryModel } from '../lib/api'
import ChatMessage from '../components/ChatMessage'
import ChatInput from '../components/ChatInput'

interface FileAttach {
  name: string
  type: string
  data: string
  size: number
}

interface ChatEntry {
  role: string
  content: string
  files?: FileAttach[]
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [modelSearch, setModelSearch] = useState('')
  const [showModelPicker, setShowModelPicker] = useState(false)
  const abortRef = useRef<AbortController | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const pickerRef = useRef<HTMLDivElement>(null)
  const [searchParams] = useSearchParams()

  const { data: models } = useQuery({
    queryKey: ['models'],
    queryFn: () => api.models.list(),
  })

  const { data: libraryData } = useQuery({
    queryKey: ['library'],
    queryFn: () => api.models.library(),
  })

  const { data: config } = useQuery({
    queryKey: ['config'],
    queryFn: () => api.config.get(),
  })

  const urlModel = searchParams.get('model')
  const [selectedModel, setSelectedModel] = useState(urlModel || '')

  useEffect(() => {
    if (!selectedModel) {
      const fromUrl = searchParams.get('model')
      setSelectedModel(fromUrl || (config?.default_model as string) || '')
    }
  }, [])

  const installedModels = models?.models || []
  const libraryModels = libraryData?.models || []
  const allModelOptions = [
    ...installedModels.map((m: ModelData) => ({ id: m.name, installed: true })),
    ...libraryModels
      .filter((lm: LibraryModel) => !installedModels.some((im: ModelData) => im.name === lm.name))
      .map((lm: LibraryModel) => ({ id: lm.name, installed: false })),
  ]
  const modelList = selectedModel
    ? [selectedModel, ...allModelOptions.filter(m => m.id !== selectedModel).map(m => m.id)]
    : allModelOptions.map(m => m.id)
  const filteredModels = modelSearch
    ? modelList.filter(m => m.toLowerCase().includes(modelSearch.toLowerCase()))
    : modelList

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(e.target as Node)) {
        setShowModelPicker(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = useCallback(
    (text: string, files?: FileAttach[]) => {
      if (!selectedModel) {
        setError('Select a model first')
        return
      }
      setError(null)
      const userMessage: ChatEntry = { role: 'user', content: text, files }
      const assistantMessage: ChatEntry = { role: 'assistant', content: '' }
      setMessages((prev) => [...prev, userMessage, assistantMessage])
      setLoading(true)

      const abort = new AbortController()
      abortRef.current = abort

      const allMessages = [...messages, userMessage]

      chatStream(
        selectedModel,
        allMessages,
        (chunk) => {
          setMessages((prev) => {
            const copy = [...prev]
            const last = copy[copy.length - 1]
            if (last && last.role === 'assistant') {
              copy[copy.length - 1] = { ...last, content: last.content + chunk }
            }
            return copy
          })
        },
        () => {
          setLoading(false)
          abortRef.current = null
        },
        (err) => {
          setError(err)
          setLoading(false)
          abortRef.current = null
        },
        abort.signal,
        files,
      )
    },
    [messages, selectedModel],
  )

  const handleStop = useCallback(() => {
    abortRef.current?.abort()
    setLoading(false)
    abortRef.current = null
  }, [])

  const handleClear = () => {
    setMessages([])
    setError(null)
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-2 border-b border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-950">
        <div className="flex items-center gap-2 min-w-0">
          <MessageSquare className="w-4 h-4 text-brand-500 shrink-0" />
          <div className="relative" ref={pickerRef}>
            <button
              onClick={() => setShowModelPicker(v => !v)}
              className="flex items-center gap-1.5 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:text-brand-600 dark:hover:text-brand-400 transition-colors"
            >
              {selectedModel || (
                <span className="text-neutral-400 italic">Select a model...</span>
              )}
              <ChevronDown className="w-3.5 h-3.5" />
            </button>

            {showModelPicker && (
              <div className="absolute top-full left-0 mt-1 w-72 max-h-72 overflow-y-auto bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl shadow-lg z-50 p-1">
                <input
                  type="text"
                  value={modelSearch}
                  onChange={e => setModelSearch(e.target.value)}
                  placeholder="Search models..."
                  className="input text-xs mb-1"
                  autoFocus
                />
                {filteredModels.length === 0 ? (
                  <div className="px-3 py-4 text-xs text-neutral-400 text-center">
                    No models found
                  </div>
                ) : (
                  filteredModels.map((id) => {
                    const isInstalled = installedModels.some((m: ModelData) => m.name === id)
                    return (
                      <button
                        key={id}
                        onClick={() => {
                          setSelectedModel(id)
                          setShowModelPicker(false)
                          setModelSearch('')
                        }}
                        className={`w-full text-left px-3 py-1.5 rounded-lg text-xs transition-colors flex items-center gap-2 ${
                          selectedModel === id
                            ? 'bg-brand-100 dark:bg-brand-900/30 text-brand-800 dark:text-brand-300'
                            : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800'
                        }`}
                      >
                        <span className="truncate flex-1">{id}</span>
                        {isInstalled && (
                          <span className="badge text-[10px]">installed</span>
                        )}
                      </button>
                    )
                  })
                )}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1">
          {messages.length > 0 && (
            <button onClick={handleClear} className="btn-ghost text-xs gap-1" title="Clear chat">
              <Trash2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Clear</span>
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-neutral-400 dark:text-neutral-300 py-20">
              <div className="w-16 h-16 rounded-2xl bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center mb-4">
                <MessageSquare className="w-8 h-8 text-brand-500" />
              </div>
              <h2 className="text-xl font-semibold mb-1 text-neutral-800 dark:text-neutral-200">
                superLLM Chat
              </h2>
              <p className="text-sm text-neutral-500 dark:text-neutral-300">
                Select a model and start chatting.
              </p>
              {selectedModel && (
                <div className="mt-6 flex items-center gap-2 px-4 py-2 rounded-full bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-300 text-xs font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-500" />
                  {selectedModel}
                </div>
              )}
            </div>
          )}

          {messages.map((msg, i) => (
            <ChatMessage key={i} role={msg.role} content={msg.content} files={msg.files} />
          ))}

          {loading && messages[messages.length - 1]?.content === '' && (
            <div className="flex gap-3 py-4">
              <div className="w-8 h-8 rounded-full bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center flex-shrink-0 ring-2 ring-brand-200 dark:ring-brand-800">
                <Bot className="w-4 h-4 text-brand-600" />
              </div>
              <div className="max-w-[70%] rounded-2xl rounded-bl-sm px-4 py-3 bg-neutral-100 dark:bg-neutral-800">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 my-2 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
              {error}
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      <ChatInput
        onSend={handleSend}
        onStop={handleStop}
        loading={loading}
        disabled={!selectedModel}
      />
    </div>
  )
}
