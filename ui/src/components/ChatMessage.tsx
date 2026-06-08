import { User, Bot, FileText } from 'lucide-react'
import clsx from 'clsx'

interface ChatMessageProps {
  role: string
  content: string
  files?: { name: string; type: string; data: string; size: number }[]
}

export default function ChatMessage({ role, content, files }: ChatMessageProps) {
  const isUser = role === 'user'

  return (
    <div
      className={clsx(
        'flex gap-3 py-4',
        isUser ? 'justify-end' : 'justify-start',
      )}
    >
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center flex-shrink-0 ring-2 ring-brand-200 dark:ring-brand-800">
          <Bot className="w-4 h-4 text-brand-600" />
        </div>
      )}
      <div
        className={clsx(
          'max-w-[70%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap',
          isUser
            ? 'bg-brand-600 text-white rounded-br-sm'
            : 'bg-neutral-100 dark:bg-neutral-800 rounded-bl-sm',
        )}
      >
        {files && files.length > 0 && (
          <div className={clsx('flex flex-wrap gap-2 mb-2', isUser && 'justify-end')}>
            {files.map((f, i) => (
              f.type.startsWith('image/') ? (
                <img
                  key={i}
                  src={f.data}
                  alt={f.name}
                  className="max-w-[200px] max-h-[200px] rounded-lg object-cover"
                />
              ) : (
                <div key={i} className={clsx(
                  'flex items-center gap-1.5 px-2 py-1 rounded text-xs',
                  isUser ? 'bg-brand-700' : 'bg-neutral-200 dark:bg-neutral-700'
                )}>
                  <FileText className="w-3 h-3" />
                  <span className="truncate max-w-[100px]">{f.name}</span>
                </div>
              )
            ))}
          </div>
        )}
        {content || <span className="italic opacity-60">empty</span>}
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-neutral-200 dark:bg-neutral-700 flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-neutral-600 dark:text-neutral-300" />
        </div>
      )}
    </div>
  )
}
