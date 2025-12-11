import { useState, useRef } from 'react'
import { Send, Image, Type, X, Upload, Loader2 } from 'lucide-react'
import type { GenerateMode } from '../types'
import * as api from '../api'

interface InputAreaProps {
  mode: GenerateMode
  onModeChange: (mode: GenerateMode) => void
  onGenerate: (prompt: string, imageUrl?: string) => void
  loading: boolean
  disabled: boolean
}

export function InputArea({ mode, onModeChange, onGenerate, loading, disabled }: InputAreaProps) {
  const [prompt, setPrompt] = useState('')
  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 处理图片上传
  const handleImageSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // 本地预览
    const reader = new FileReader()
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string)
    }
    reader.readAsDataURL(file)

    // 上传到服务器
    setUploading(true)
    try {
      const result = await api.uploadImage(file)
      // 优先使用public_url（图床URL），用于传给视频生成API
      // result.url是本地预览用的
      setImageUrl(result.public_url || result.url)
      if (!result.public_url) {
        console.warn('图床上传失败，使用本地URL（可能导致API调用失败）')
      }
    } catch (e) {
      console.error('上传失败:', e)
      setImagePreview(null)
    } finally {
      setUploading(false)
    }
  }

  // 移除图片
  const handleRemoveImage = () => {
    setImageUrl(null)
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // 提交生成
  const handleSubmit = () => {
    if (!prompt.trim() || disabled) return
    
    if (mode === 'image' && !imageUrl) {
      // 图生视频模式必须有图片
      return
    }

    onGenerate(prompt, mode === 'image' ? imageUrl! : undefined)
    setPrompt('')
    handleRemoveImage()
  }

  // 回车发送
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="border-t border-border bg-surface p-8 pb-4">
      <div className="max-w-5xl mx-auto">
        {/* 模式切换 */}
        <div className="flex gap-3 mb-4">
          <button
            onClick={() => onModeChange('text')}
            className={`flex items-center gap-2 px-4 py-2 text-base rounded-lg transition-colors
                       ${mode === 'text' 
                         ? 'bg-primary text-white' 
                         : 'bg-gray-100 text-secondary hover:bg-gray-200'}`}
          >
            <Type size={18} />
            文生视频
          </button>
          <button
            onClick={() => onModeChange('image')}
            className={`flex items-center gap-2 px-4 py-2 text-base rounded-lg transition-colors
                       ${mode === 'image' 
                         ? 'bg-primary text-white' 
                         : 'bg-gray-100 text-secondary hover:bg-gray-200'}`}
          >
            <Image size={18} />
            图生视频
          </button>
        </div>

        {/* 图生视频模式：图片上传区 */}
        {mode === 'image' && (
          <div className="mb-3">
            {imagePreview ? (
              <div className="relative inline-block">
                <img
                  src={imagePreview}
                  alt="参考图片"
                  className="h-24 rounded-lg border border-border"
                />
                {uploading && (
                  <div className="absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center">
                    <Loader2 className="animate-spin text-white" size={20} />
                  </div>
                )}
                <button
                  onClick={handleRemoveImage}
                  className="absolute -top-2 -right-2 w-5 h-5 bg-primary text-white 
                             rounded-full flex items-center justify-center hover:bg-gray-700"
                >
                  <X size={12} />
                </button>
              </div>
            ) : (
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-2 px-4 py-3 border-2 border-dashed 
                           border-border rounded-lg text-secondary hover:border-gray-400 
                           hover:text-gray-600 transition-colors text-sm"
              >
                <Upload size={18} />
                点击上传参考图片
              </button>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageSelect}
              className="hidden"
            />
          </div>
        )}

        {/* 输入框 */}
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={mode === 'text' ? '描述你想生成的视频内容...' : '描述视频动作和效果...'}
              disabled={disabled}
              className="w-full px-6 py-5 pr-16 border border-border rounded-2xl resize-none
                        focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary
                        disabled:bg-gray-50 disabled:cursor-not-allowed text-lg"
              rows={4}
            />
          </div>
          <button
            onClick={handleSubmit}
            disabled={disabled || !prompt.trim() || (mode === 'image' && !imageUrl)}
            className="px-8 bg-primary text-white rounded-2xl hover:bg-gray-800 
                       disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors
                       flex items-center justify-center"
          >
            {loading ? (
              <Loader2 size={28} className="animate-spin" />
            ) : (
              <Send size={28} />
            )}
          </button>
        </div>

        {/* 提示 */}
        <p className="text-xs text-secondary mt-2 text-center">
          按 Enter 发送，Shift + Enter 换行
        </p>
      </div>
    </div>
  )
}
