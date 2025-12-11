import { Plus, MessageSquare, Trash2 } from 'lucide-react'
import type { Session } from '../types'

interface SidebarProps {
  sessions: Session[]
  currentSessionId: number | null
  onSelect: (id: number) => void
  onNew: () => void
  onDelete: (id: number) => void
}

export function Sidebar({ sessions, currentSessionId, onSelect, onNew, onDelete }: SidebarProps) {
  return (
    <div className="w-64 bg-surface border-r border-border flex flex-col">
      {/* 标题和新建按钮 */}
      <div className="p-4 border-b border-border">
        <button
          onClick={onNew}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 
                     bg-primary text-white rounded-lg hover:bg-gray-800 
                     transition-colors text-sm font-medium"
        >
          <Plus size={18} />
          新建会话
        </button>
      </div>

      {/* 会话列表 */}
      <div className="flex-1 overflow-y-auto p-2">
        {sessions.length === 0 ? (
          <div className="text-center text-secondary text-sm py-8">
            暂无会话
          </div>
        ) : (
          <div className="space-y-1">
            {sessions.map(session => (
              <div
                key={session.id}
                onClick={() => onSelect(session.id)}
                className={`group flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer
                           transition-colors ${
                             currentSessionId === session.id
                               ? 'bg-gray-100'
                               : 'hover:bg-gray-50'
                           }`}
              >
                <MessageSquare size={16} className="text-secondary flex-shrink-0" />
                <span className="flex-1 text-sm text-primary truncate">
                  {session.title}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete(session.id)
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 
                             rounded transition-all"
                  title="删除会话"
                >
                  <Trash2 size={14} className="text-secondary" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 底部信息 */}
      <div className="p-4 border-t border-border">
        <p className="text-xs text-secondary text-center">
          AI视频生成 v1.0
        </p>
      </div>
    </div>
  )
}
