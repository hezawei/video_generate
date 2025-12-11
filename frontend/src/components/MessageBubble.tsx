import { User, Bot, Loader2, AlertCircle, Download, Play } from 'lucide-react'
import type { Message } from '../types'

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

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
        {/* 用户消息 */}
        {isUser && (
          <div className="space-y-2">
            {message.reference_image && (
              <div className="inline-block">
                <img
                  src={message.reference_image}
                  alt="参考图片"
                  className="max-w-xs rounded-lg border border-border"
                />
              </div>
            )}
            <div className="inline-block bg-primary text-white px-4 py-2 rounded-2xl rounded-tr-sm text-sm">
              {message.content}
            </div>
          </div>
        )}

        {/* AI消息（视频） */}
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

            {message.status === 'success' && message.video_url && (
              <div className="space-y-3">
                {/* 视频播放器 */}
                <video
                  src={message.video_url}
                  controls
                  className="w-full rounded-lg"
                  style={{ maxHeight: '400px' }}
                >
                  您的浏览器不支持视频播放
                </video>

                {/* 操作按钮 */}
                <div className="flex gap-2">
                  <a
                    href={message.video_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 px-3 py-1.5 text-xs bg-white 
                               border border-border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <Play size={12} />
                    预览
                  </a>
                  <button
                    onClick={handleDownload}
                    className="flex items-center gap-1 px-3 py-1.5 text-xs bg-white 
                               border border-border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <Download size={12} />
                    下载
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
    </div>
  )
}
