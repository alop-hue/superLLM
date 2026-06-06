import { useState, useRef, useEffect, useCallback } from 'react'
import { MessageSquare } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { api, chatStream } from '../lib/api'
import ChatMessage from '../components/ChatMessage'
import ChatInput from '../components/ChatInput'

interface ChatEntry {
  role: string
  content: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  const { data: models } = useQuery({
    queryKey: ['models'],
    queryFn: () => api.models.list(),
  })

  const { data: config } = useQuery({
    queryKey: ['config'],
    queryFn: () => api.config.get(),
  })

  const selectedModel = (config?.default_model as string) || models?.models?.[0]?.name || 'default'

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = useCallback(
    (text: string) => {
      setError(null)
      const userMessage: ChatEntry = { role: 'user', content: text }
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
      <div className="flex items-center justify-between px-6 py-3 border-b border-gray-200 dark:border-gray-700">
        <h1 className="text-lg font-semibold flex items-center gap-2">
          <MessageSquare className="w-5 h-5" />
          Chat
        </h1>
        {messages.length > 0 && (
          <button onClick={handleClear} className="btn-secondary text-sm">
            Clear
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-4">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-gray-400 dark:text-gray-500 py-20">
              <MessageSquare className="w-12 h-12 mb-4" />
              <h2 className="text-xl font-semibold mb-2">superLLM Chat</h2>
              <p className="text-sm">Start a conversation with your local or cloud model.</p>
              <p className="text-xs mt-2">
                Model: <span className="font-mono">{selectedModel}</span>
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <ChatMessage key={i} role={msg.role} content={msg.content} />
          ))}

          {loading && messages[messages.length - 1]?.content === '' && (
            <div className="flex gap-3 py-4">
              <div className="w-8 h-8 rounded-full bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center">
                <div className="w-5 h-5 text-brand-600">
                  <span className="animate-pulse">...</span>
                </div>
              </div>
              <div className="max-w-[70%] rounded-2xl rounded-bl-sm px-4 py-3 bg-gray-100 dark:bg-gray-800">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 my-2 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 rounded-lg">
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
      />
    </div>
  )
}
