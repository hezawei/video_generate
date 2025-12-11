import { useState } from 'react'
import { User, Bot, Loader2, AlertCircle, Download, Play, Pencil, Copy, Check } from 'lucide-react'
import type { Message } from '../types'

interface MessageBubbleProps {
  message: Message
  onEdit?: (message: Message) => void
}

export function MessageBubble({ message, onEdit }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const [isPlaying, setIsPlaying] = useState(false)
  const [showImageModal, setShowImageModal] = useState(false)

  // 双击编辑
  const handleDoubleClick = () => {
    if (isUser && onEdit) {
      onEdit(message)
    }
  }

  // 播放视频
  const handlePlay = () => {
    setIsPlaying(true)
    const video = document.getElementById(`video-${message.id}`) as HTMLVideoElement
    video?.play()
  }

  // 复制尾帧到剪贴板（通过后端提取）
  const [extracting, setExtracting] = useState(false)
  const [copySuccess, setCopySuccess] = useState(false)
  
  const handleCopyLastFrame = async () => {
    if (!message.video_url || extracting) return
    
    setExtracting(true)
    setCopySuccess(false)
    try {
      // 调用后端 API 提取尾帧
      const response = await fetch(`/api/generate/extract-frame?video_url=${encodeURIComponent(message.video_url)}`)
      
      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || '提取失败')
      }
      
      const data = await response.json()
      
      // 将 base64 转换为 blob
      const base64Data = data.image.split(',')[1]
      const byteCharacters = atob(base64Data)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], { type: 'image/png' })
      
      // 复制到剪贴板
      try {
        await navigator.clipboard.write([
          new ClipboardItem({ 'image/png': blob })
        ])
        // 显示成功状态
        setCopySuccess(true)
        setTimeout(() => setCopySuccess(false), 2000)
      } catch (e) {
        // 降级：打开新窗口
        const url = URL.createObjectURL(blob)
        window.open(url, '_blank')
      }
    } catch (e) {
      console.error('提取尾帧失败:', e)
    } finally {
      setExtracting(false)
    }
  }

  // 下载视频
  const handleDownload = async () => {
    if (!message.video_url) return
    
    try {
      const response = await fetch(message.video_url)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `video_${message.id}.mp4`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (e) {
      console.error('下载失败:', e)
    }
  }

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* 头像 */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
                      ${isUser ? 'bg-primary text-white' : 'bg-gray-100 text-secondary'}`}>
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>

      {/* 内容 */}
      <div className={`flex-1 ${isUser ? 'text-right' : ''}`}>
        {/* 用户消息 - 双击可编辑 */}
        {isUser && (
          <div 
            className="group cursor-pointer" 
            onDoubleClick={handleDoubleClick}
            title="双击编辑"
          >
            <div className="inline-flex items-center gap-2">
              {/* 参考图片（小图） */}
              {message.reference_image && (
                <img
                  src={message.reference_image}
                  alt="参考图片"
                  className="w-10 h-10 rounded-lg object-cover border border-border"
                />
              )}
              <div className="bg-primary text-white px-4 py-2 rounded-2xl rounded-tr-sm text-sm max-w-md">
                {message.content}
              </div>
              <Pencil 
                size={14} 
                className="text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" 
              />
            </div>
          </div>
        )}

        {/* AI消息（视频或图片） */}
        {!isUser && (
          <div className="bg-gray-50 rounded-2xl rounded-tl-sm p-4 inline-block max-w-md">
            {/* 状态显示 */}
            {(message.status === 'pending' || message.status === 'queued') && (
              <div className="flex items-center gap-2 text-secondary text-sm">
                <Loader2 size={16} className="animate-spin" />
                <span>排队中...</span>
              </div>
            )}

            {message.status === 'processing' && (
              <div className="flex items-center gap-2 text-secondary text-sm">
                <Loader2 size={16} className="animate-spin" />
                <span>生成中...</span>
              </div>
            )}

            {message.status === 'failed' && (
              <div className="flex items-center gap-2 text-red-500 text-sm">
                <AlertCircle size={16} />
                <span>生成失败: {message.error_message || '未知错误'}</span>
              </div>
            )}

            {/* 生成的图片 */}
            {message.status === 'success' && message.content_type === 'image' && message.video_url && (
              <div className="space-y-3">
                <img
                  src={message.video_url}
                  alt="生成的图片"
                  className="w-full rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
                  style={{ maxHeight: '400px', objectFit: 'contain' }}
                  onClick={() => setShowImageModal(true)}
                />
                <div className="flex gap-2">
                  <a
                    href={message.video_url}
                    download
                    className="flex items-center gap-1 px-3 py-1.5 text-xs bg-white 
                               border border-border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <Download size={12} />
                    下载图片
                  </a>
                  <button
                    onClick={async () => {
                      try {
                        const response = await fetch(message.video_url!)
                        const blob = await response.blob()
                        await navigator.clipboard.write([
                          new ClipboardItem({ [blob.type]: blob })
                        ])
                      } catch (e) {
                        console.error('复制图片失败:', e)
                      }
                    }}
                    className="flex items-center gap-1 px-3 py-1.5 text-xs bg-white 
                               border border-border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <Copy size={12} />
                    复制图片
                  </button>
                </div>
              </div>
            )}

            {/* 生成的视频 */}
            {message.status === 'success' && message.content_type === 'video' && message.video_url && (
              <div className="space-y-3">
                {/* 视频播放器 - 带大播放按钮 */}
                <div className="relative group">
                  <video
                    id={`video-${message.id}`}
                    src={message.video_url}
                    controls={isPlaying}
                    className="w-full rounded-lg"
                    style={{ maxHeight: '400px' }}
                    onPlay={() => setIsPlaying(true)}
                    onPause={() => setIsPlaying(false)}
                    onEnded={() => setIsPlaying(false)}
                  >
                    您的浏览器不支持视频播放
                  </video>
                  
                  {/* 大播放按钮覆盖层 */}
                  {!isPlaying && (
                    <div 
                      onClick={handlePlay}
                      className="absolute inset-0 flex items-center justify-center 
                                 bg-black/30 rounded-lg cursor-pointer
                                 hover:bg-black/40 transition-colors"
                    >
                      <div className="w-16 h-16 bg-white/90 rounded-full flex items-center justify-center
                                      shadow-lg hover:scale-110 transition-transform">
                        <Play size={32} className="text-primary ml-1" fill="currentColor" />
                      </div>
                    </div>
                  )}
                </div>

                {/* 操作按钮 */}
                <div className="flex gap-2">
                  <button
                    onClick={handleDownload}
                    className="flex items-center gap-1 px-3 py-1.5 text-xs bg-white 
                               border border-border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <Download size={12} />
                    下载视频
                  </button>
                  <button
                    onClick={async () => {
                      try {
                        const response = await fetch(message.video_url!)
                        const blob = await response.blob()
                        await navigator.clipboard.write([
                          new ClipboardItem({ [blob.type]: blob })
                        ])
                      } catch (e) {
                        console.error('复制视频失败:', e)
                      }
                    }}
                    className="flex items-center gap-1 px-3 py-1.5 text-xs bg-white 
                               border border-border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <Copy size={12} />
                    复制视频
                  </button>
                  <button
                    onClick={handleCopyLastFrame}
                    disabled={extracting || copySuccess}
                    className={`flex items-center gap-1 px-3 py-1.5 text-xs rounded-lg transition-all
                               ${copySuccess 
                                 ? 'bg-green-50 border border-green-300 text-green-600' 
                                 : 'bg-white border border-border hover:bg-gray-50'}
                               disabled:cursor-wait`}
                  >
                    {copySuccess ? (
                      <><Check size={12} /> 已复制</>
                    ) : extracting ? (
                      <><Loader2 size={12} className="animate-spin" /> 提取中...</>
                    ) : (
                      <><Copy size={12} /> 复制尾帧</>
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* 提示词显示 */}
            {message.prompt && (
              <p className="text-xs text-secondary mt-2 pt-2 border-t border-border">
                {message.prompt}
              </p>
            )}
          </div>
        )}
      </div>

      {/* 图片放大弹窗 */}
      {showImageModal && message.video_url && (
        <div 
          className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center cursor-pointer"
          onClick={() => setShowImageModal(false)}
        >
          <img
            src={message.video_url}
            alt="放大图片"
            className="max-w-[90vw] max-h-[90vh] object-contain"
            onClick={(e) => e.stopPropagation()}
          />
          <button
            onClick={() => setShowImageModal(false)}
            className="absolute top-4 right-4 text-white hover:text-gray-300 text-2xl"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  )
}
