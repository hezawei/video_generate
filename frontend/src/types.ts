// 会话类型
export interface Session {
  id: number
  title: string
  created_at: string
  updated_at: string
}

// 消息类型
export interface Message {
  id: number
  session_id: number
  role: 'user' | 'assistant'
  content_type: 'text' | 'image' | 'video'
  content: string | null
  task_id: string | null
  status: 'pending' | 'queued' | 'processing' | 'success' | 'failed'
  video_url: string | null
  local_path: string | null
  error_message: string | null
  prompt: string | null
  reference_image: string | null
  aspect_ratio: string
  duration: string
  created_at: string
}

// 生成模式
export type GenerateMode = 'text' | 'image'  // 文生视频 | 图生视频

// 功能类型
export type FeatureType = 'video' | 'image'  // 视频生成 | 图片生成
