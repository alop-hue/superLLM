import { User, Bot } from 'lucide-react'
import clsx from 'clsx'

interface ChatMessageProps {
  role: string
  content: string
}

export default function ChatMessage({ role, content }: ChatMessageProps) {
  const isUser = role === 'user'

  return (
    <div
      className={clsx(
        'flex gap-3 py-4',
        isUser ? 'justify-end' : 'justify-start',
      )}
    >
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center flex-shrink-0">
          <Bot className="w-5 h-5 text-brand-600" />
        </div>
      )}
      <div
        className={clsx(
          'max-w-[70%] rounded-2xl px-4 py-3',
          isUser
            ? 'bg-brand-600 text-white rounded-br-sm'
            : 'bg-gray-100 dark:bg-gray-800 rounded-bl-sm',
        )}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center flex-shrink-0">
          <User className="w-5 h-5 text-gray-600 dark:text-gray-300" />
        </div>
      )}
    </div>
  )
}
