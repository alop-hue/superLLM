import { useState, useRef, useEffect, KeyboardEvent } from 'react'
import { Send, Square, Paperclip, X } from 'lucide-react'

interface FileAttachment {
  name: string
  type: string
  size: number
  data: string  // base64
}

interface ChatInputProps {
  onSend: (text: string, files?: FileAttachment[]) => void
  onStop: () => void
  loading: boolean
  disabled?: boolean
}

export default function ChatInput({ onSend, onStop, loading, disabled }: ChatInputProps) {
  const [text, setText] = useState('')
  const [files, setFiles] = useState<FileAttachment[]>([])
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }, [text])

  useEffect(() => {
    if (!loading && textareaRef.current) {
      textareaRef.current.focus()
    }
  }, [loading])

  const handleSubmit = () => {
    const trimmed = text.trim()
    if ((!trimmed && files.length === 0) || loading || disabled) return
    onSend(trimmed, files.length > 0 ? files : undefined)
    setText('')
    setFiles([])
  }

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || [])
    const readers = selected.map((f) => new Promise<FileAttachment>((resolve) => {
      const reader = new FileReader()
      reader.onload = () => resolve({
        name: f.name,
        type: f.type,
        size: f.size,
        data: reader.result as string,
      })
      reader.readAsDataURL(f)
    }))
    Promise.all(readers).then(setFiles)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const removeFile = (i: number) => {
    setFiles((prev) => prev.filter((_, idx) => idx !== i))
  }

  return (
    <div className="px-4 py-3 bg-transparent">
      {files.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2 max-w-4xl mx-auto">
          {files.map((f, i) => (
            <div key={i} className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-neutral-100 dark:bg-neutral-800 text-xs text-neutral-700 dark:text-neutral-300 border border-neutral-200 dark:border-neutral-700">
              <span className="truncate max-w-[120px]">{f.name}</span>
              <button onClick={() => removeFile(i)} className="hover:text-red-500">
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}
      <div className="chat-input-container">
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={loading}
          className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center transition-colors disabled:opacity-30 enabled:hover:bg-neutral-100 dark:enabled:hover:bg-neutral-800 text-neutral-400 dark:text-neutral-500"
          title="Attach file"
        >
          <Paperclip className="w-4 h-4" />
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,.pdf,.txt,.py,.js,.ts,.jsx,.tsx,.md,.json,.yaml,.yml,.csv"
          onChange={handleFileChange}
          className="hidden"
        />
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? 'Select a model to start...' : 'Message superLLM...'}
          rows={1}
          disabled={loading || disabled}
          className="input-chat min-h-[24px] max-h-[200px]"
        />
        <button
          onClick={loading ? onStop : handleSubmit}
          disabled={(disabled || (!text.trim() && files.length === 0)) && !loading}
          className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center transition-colors disabled:opacity-30 disabled:cursor-not-allowed enabled:hover:bg-brand-100 dark:enabled:hover:bg-brand-900/30 enabled:text-brand-600 dark:enabled:text-brand-400"
        >
          {loading ? (
            <Square className="w-4 h-4" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </button>
      </div>
    </div>
  )
}
