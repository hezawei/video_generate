import { useState, useEffect, useCallback, useRef } from 'react'
import { Sidebar } from './components/Sidebar'
import { ChatArea } from './components/ChatArea'
import { InputArea } from './components/InputArea'
import type { Session, Message, GenerateMode, FeatureType } from './types'
import * as api from './api'

function App() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [featureType, setFeatureType] = useState<FeatureType>('video')
  const [mode, setMode] = useState<GenerateMode>('text')
  const [pollingIds, setPollingIds] = useState<Set<number>>(new Set())
  const [editingMessage, setEditingMessage] = useState<{ id: number; content: string; imageUrl?: string } | null>(null)

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
  const retryCountRef = useRef<Map<number, number>>(new Map())
  
  useEffect(() => {
    if (pollingIds.size === 0) return

    const interval = setInterval(async () => {
      const newPollingIds = new Set<number>()
      
      for (const msgId of pollingIds) {
        try {
          const status = await api.getTaskStatus(msgId)
          
          // 成功获取状态，重置重试计数
          retryCountRef.current.delete(msgId)
          
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
          // failed 或 success 状态不再轮询
        } catch (e) {
          console.error('轮询状态失败:', e)
          // 出错时重试，但最多重试5次
          const retryCount = (retryCountRef.current.get(msgId) || 0) + 1
          retryCountRef.current.set(msgId, retryCount)
          
          if (retryCount < 5) {
            newPollingIds.add(msgId)
          } else {
            console.warn(`轮询 ${msgId} 失败次数过多，停止轮询`)
            retryCountRef.current.delete(msgId)
            // 更新为失败状态
            setMessages(prev => prev.map(m => 
              m.id === msgId 
                ? { ...m, status: 'failed', error_message: '轮询超时' }
                : m
            ))
          }
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
      // 如果是编辑重发，先删除该消息及之后的消息
      if (editingMessage) {
        await api.deleteMessageAndAfter(sessionId, editingMessage.id)
        // 立即更新前端状态，移除被编辑消息及之后的消息
        setMessages(prev => prev.filter(m => m.id < editingMessage.id))
        // 从轮询队列中移除相关的消息ID
        setPollingIds(prev => {
          const newIds = new Set(prev)
          messages.forEach(m => {
            if (m.id >= editingMessage.id) {
              newIds.delete(m.id)
            }
          })
          return newIds
        })
        setEditingMessage(null)
      }

      if (featureType === 'video') {
        // 视频生成
        let response: api.GenerateResponse
        if (mode === 'image' && imageUrl) {
          response = await api.imageToVideo(sessionId, prompt, imageUrl)
        } else {
          response = await api.textToVideo(sessionId, prompt)
        }
        // 开始轮询视频任务
        setPollingIds(prev => new Set([...prev, response.message_id]))
      } else {
        // 图片生成（同步，显示临时加载状态）
        const tempId = Date.now()
        // 添加临时用户消息
        const tempUserMsg: Message = {
          id: tempId,
          session_id: sessionId,
          role: 'user',
          content_type: 'text',
          content: prompt,
          task_id: null,
          status: 'success',
          video_url: null,
          local_path: null,
          error_message: null,
          prompt: null,
          reference_image: imageUrl || null,
          aspect_ratio: '1:1',
          duration: '0',
          created_at: new Date().toISOString(),
        }
        // 添加临时AI加载消息
        const tempAiMsg: Message = {
          id: tempId + 1,
          session_id: sessionId,
          role: 'assistant',
          content_type: 'image',
          content: null,
          task_id: null,
          status: 'processing',
          video_url: null,
          local_path: null,
          error_message: null,
          prompt: prompt,
          reference_image: null,
          aspect_ratio: '1:1',
          duration: '0',
          created_at: new Date().toISOString(),
        }
        setMessages(prev => [...prev, tempUserMsg, tempAiMsg])
        
        try {
          if (mode === 'image' && imageUrl) {
            await api.imageToImage(sessionId, prompt, imageUrl)
          } else {
            await api.textToImage(sessionId, prompt)
          }
        } catch (e) {
          // 图片生成失败，更新临时消息状态
          setMessages(prev => prev.map(m => 
            m.id === tempId + 1 
              ? { ...m, status: 'failed', error_message: String(e) }
              : m
          ))
          throw e
        }
      }

      // 重新加载消息和会话列表
      await loadMessages(sessionId)
      await loadSessions()
    } catch (e) {
      console.error('生成失败:', e)
      // 即使失败也重新加载消息以同步状态
      if (sessionId) await loadMessages(sessionId)
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
            id: msg.id,
            content: msg.content || '', 
            imageUrl: msg.reference_image || undefined
          })}
        />

        {/* 输入区域 */}
        <InputArea
          featureType={featureType}
          onFeatureTypeChange={setFeatureType}
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
