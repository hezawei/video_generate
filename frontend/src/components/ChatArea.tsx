import { useEffect, useRef } from 'react'
import { MessageBubble } from './MessageBubble'
import { Video } from 'lucide-react'
import type { Message } from '../types'

interface ChatAreaProps {
  messages: Message[]
  onEditMessage?: (message: Message) => void
}

export function ChatArea({ messages, onEditMessage }: ChatAreaProps) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const prevLengthRef = useRef(0)

  // 只有新消息时才滚动到底部（状态更新不滚动）
  useEffect(() => {
    if (messages.length > prevLengthRef.current) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
    prevLengthRef.current = messages.length
  }, [messages.length])

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-secondary">
        <Video size={48} className="mb-4 opacity-30" />
        <p className="text-lg font-medium">AI视频生成</p>
        <p className="text-sm mt-2">输入提示词开始生成视频</p>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        {messages.map(message => (
          <MessageBubble key={message.id} message={message} onEdit={onEditMessage} />
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
