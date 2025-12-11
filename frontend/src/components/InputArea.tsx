import { useState, useRef, useEffect } from 'react'
import { Send, Type, X, Upload, Loader2, Video, ImageIcon } from 'lucide-react'
import type { GenerateMode, FeatureType } from '../types'
import * as api from '../api'

interface InputAreaProps {
  featureType: FeatureType
  onFeatureTypeChange: (type: FeatureType) => void
  mode: GenerateMode
  onModeChange: (mode: GenerateMode) => void
  onGenerate: (prompt: string, imageUrl?: string) => void
  loading: boolean
  disabled: boolean
  editingMessage?: { content: string; imageUrl?: string } | null
  onCancelEdit?: () => void
}

export function InputArea({ featureType, onFeatureTypeChange, mode, onModeChange, onGenerate, loading, disabled, editingMessage, onCancelEdit }: InputAreaProps) {
  const [prompt, setPrompt] = useState('')
  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // 编辑模式：填充内容
  useEffect(() => {
    if (editingMessage) {
      setPrompt(editingMessage.content)
      if (editingMessage.imageUrl) {
        setImagePreview(editingMessage.imageUrl)
        setImageUrl(editingMessage.imageUrl)
        onModeChange('image')
      }
      textareaRef.current?.focus()
    }
  }, [editingMessage])

  // 处理粘贴图片 (Ctrl+V)
  const handlePaste = async (e: React.ClipboardEvent) => {
    const items = e.clipboardData?.items
    if (!items) return

    for (const item of items) {
      if (item.type.startsWith('image/')) {
        e.preventDefault()
        
        // 已有图片时提示
        if (imagePreview) {
          alert('最多只能上传一张图片，请先移除现有图片')
          return
        }
        
        const file = item.getAsFile()
        if (file) {
          // 自动切换到图生视频模式
          onModeChange('image')
          await uploadFile(file)
        }
        break
      }
    }
  }

  // 上传文件（复用逻辑）
  const uploadFile = async (file: File) => {
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

  // 处理图片上传（复用 uploadFile）
  const handleImageSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) await uploadFile(file)
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
        {/* 功能类型切换（图片/视频） */}
        <div className="flex gap-3 mb-4">
          {/* 图片生成 */}
          <div className={`flex rounded-lg overflow-hidden border ${featureType === 'image' ? 'border-primary' : 'border-transparent'}`}>
            <button
              onClick={() => { onFeatureTypeChange('image'); onModeChange('text') }}
              className={`flex items-center gap-2 px-3 py-2 text-sm transition-colors
                         ${featureType === 'image' && mode === 'text'
                           ? 'bg-primary text-white' 
                           : featureType === 'image'
                           ? 'bg-gray-100 text-secondary hover:bg-gray-200'
                           : 'bg-gray-50 text-gray-400 hover:bg-gray-100'}`}
            >
              <Type size={16} />
              文生图片
            </button>
            <button
              onClick={() => { onFeatureTypeChange('image'); onModeChange('image') }}
              className={`flex items-center gap-2 px-3 py-2 text-sm transition-colors
                         ${featureType === 'image' && mode === 'image'
                           ? 'bg-primary text-white' 
                           : featureType === 'image'
                           ? 'bg-gray-100 text-secondary hover:bg-gray-200'
                           : 'bg-gray-50 text-gray-400 hover:bg-gray-100'}`}
            >
              <ImageIcon size={16} />
              图生图片
            </button>
          </div>
          
          {/* 分隔 */}
          <div className="w-px bg-gray-200" />
          
          {/* 视频生成 */}
          <div className={`flex rounded-lg overflow-hidden border ${featureType === 'video' ? 'border-primary' : 'border-transparent'}`}>
            <button
              onClick={() => { onFeatureTypeChange('video'); onModeChange('text') }}
              className={`flex items-center gap-2 px-3 py-2 text-sm transition-colors
                         ${featureType === 'video' && mode === 'text'
                           ? 'bg-primary text-white' 
                           : featureType === 'video'
                           ? 'bg-gray-100 text-secondary hover:bg-gray-200'
                           : 'bg-gray-50 text-gray-400 hover:bg-gray-100'}`}
            >
              <Type size={16} />
              文生视频
            </button>
            <button
              onClick={() => { onFeatureTypeChange('video'); onModeChange('image') }}
              className={`flex items-center gap-2 px-3 py-2 text-sm transition-colors
                         ${featureType === 'video' && mode === 'image'
                           ? 'bg-primary text-white' 
                           : featureType === 'video'
                           ? 'bg-gray-100 text-secondary hover:bg-gray-200'
                           : 'bg-gray-50 text-gray-400 hover:bg-gray-100'}`}
            >
              <Video size={16} />
              图生视频
            </button>
          </div>
        </div>

        {/* 图生模式：图片上传区（图生视频或图生图片） */}
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

        {/* 编辑模式提示 */}
        {editingMessage && (
          <div className="flex items-center justify-between mb-2 px-2 py-1 bg-yellow-50 border border-yellow-200 rounded-lg">
            <span className="text-sm text-yellow-700">编辑消息</span>
            <button
              onClick={() => {
                setPrompt('')
                handleRemoveImage()
                onCancelEdit?.()
              }}
              className="text-sm text-yellow-700 hover:text-yellow-900"
            >
              取消
            </button>
          </div>
        )}

        {/* 输入框 */}
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              onPaste={handlePaste}
              placeholder={
                featureType === 'video'
                  ? (mode === 'text' ? '描述你想生成的视频内容...' : '描述视频动作和效果... (可粘贴图片)')
                  : (mode === 'text' ? '描述你想生成的图片内容...' : '描述如何修改这张图片... (可粘贴图片)')
              }
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
