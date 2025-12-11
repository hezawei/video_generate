import { useState, useEffect, useCallback } from 'react'
import { Sidebar } from './components/Sidebar'
import { ChatArea } from './components/ChatArea'
import { InputArea } from './components/InputArea'
import type { Session, Message, GenerateMode } from './types'
import * as api from './api'

function App() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState<GenerateMode>('text')
  const [pollingIds, setPollingIds] = useState<Set<number>>(new Set())
  const [editingMessage, setEditingMessage] = useState<{ content: string; imageUrl?: string } | null>(null)

  // 加载会话列表
  const loadSessions = useCallback(async () => {
    try {
      const data = await api.getSessions()
      setSessions(data)
    } catch (e) {
      console.error('加载会话失败:', e)
    }
  }, [])

  // 加载消息
  const loadMessages = useCallback(async (sessionId: number) => {
    try {
      const data = await api.getSessionMessages(sessionId)
      setMessages(data)
      
      // 找出需要轮询的消息
      const needPolling = data.filter(
        m => m.role === 'assistant' && 
        (m.status === 'queued' || m.status === 'processing' || m.status === 'pending')
      )
      if (needPolling.length > 0) {
        setPollingIds(new Set(needPolling.map(m => m.id)))
      }
    } catch (e) {
      console.error('加载消息失败:', e)
    }
  }, [])

  // 轮询任务状态
  useEffect(() => {
    if (pollingIds.size === 0) return

    const interval = setInterval(async () => {
      const newPollingIds = new Set<number>()
      
      for (const msgId of pollingIds) {
        try {
          const status = await api.getTaskStatus(msgId)
          
          // 更新消息状态
          setMessages(prev => prev.map(m => 
            m.id === msgId 
              ? { ...m, status: status.status as Message['status'], video_url: status.video_url, error_message: status.error_message }
              : m
          ))
          
          // 如果还在处理中，继续轮询
          if (status.status === 'queued' || status.status === 'processing' || status.status === 'pending') {
            newPollingIds.add(msgId)
          }
        } catch (e) {
          console.error('轮询状态失败:', e)
          // 出错时保留ID，以便下次重试（关键修复）
          newPollingIds.add(msgId)
        }
      }
      
      setPollingIds(newPollingIds)
    }, 3000)

    return () => clearInterval(interval)
  }, [pollingIds])

  // 初始加载
  useEffect(() => {
    loadSessions()
  }, [loadSessions])

  // 切换会话时加载消息
  useEffect(() => {
    if (currentSessionId) {
      loadMessages(currentSessionId)
    } else {
      setMessages([])
    }
  }, [currentSessionId, loadMessages])

  // 新建会话
  const handleNewSession = async () => {
    try {
      const session = await api.createSession()
      setSessions(prev => [session, ...prev])
      setCurrentSessionId(session.id)
      setMessages([])
    } catch (e) {
      console.error('创建会话失败:', e)
    }
  }

  // 删除会话
  const handleDeleteSession = async (id: number) => {
    try {
      await api.deleteSession(id)
      setSessions(prev => prev.filter(s => s.id !== id))
      if (currentSessionId === id) {
        setCurrentSessionId(null)
        setMessages([])
      }
    } catch (e) {
      console.error('删除会话失败:', e)
    }
  }

  // 发送生成请求
  const handleGenerate = async (prompt: string, imageUrl?: string) => {
    if (!prompt.trim()) return

    let sessionId = currentSessionId

    // 如果没有当前会话，先创建一个
    if (!sessionId) {
      try {
        const session = await api.createSession()
        setSessions(prev => [session, ...prev])
        sessionId = session.id
        setCurrentSessionId(session.id)
      } catch (e) {
        console.error('创建会话失败:', e)
        return
      }
    }

    setLoading(true)
    try {
      let response: api.GenerateResponse

      if (mode === 'image' && imageUrl) {
        response = await api.imageToVideo(sessionId, prompt, imageUrl)
      } else {
        response = await api.textToVideo(sessionId, prompt)
      }

      // 重新加载消息和会话列表
      await loadMessages(sessionId)
      await loadSessions()

      // 开始轮询新任务
      setPollingIds(prev => new Set([...prev, response.message_id]))
    } catch (e) {
      console.error('生成失败:', e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-background">
      {/* 侧边栏 */}
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelect={setCurrentSessionId}
        onNew={handleNewSession}
        onDelete={handleDeleteSession}
      />

      {/* 主内容区 */}
      <div className="flex-1 flex flex-col">
        {/* 聊天区域 */}
        <ChatArea 
          messages={messages} 
          onEditMessage={(msg) => setEditingMessage({ 
            content: msg.content || '', 
            imageUrl: msg.reference_image || undefined
          })}
        />

        {/* 输入区域 */}
        <InputArea
          mode={mode}
          onModeChange={setMode}
          onGenerate={handleGenerate}
          loading={loading}
          disabled={loading}
          editingMessage={editingMessage}
          onCancelEdit={() => setEditingMessage(null)}
        />
      </div>
    </div>
  )
}

export default App
