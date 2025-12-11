import axios from 'axios'
import type { Session, Message } from './types'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 会话相关
export async function getSessions(): Promise<Session[]> {
  const { data } = await api.get('/sessions')
  return data
}

export async function createSession(title?: string): Promise<Session> {
  const { data } = await api.post('/sessions', { title })
  return data
}

export async function deleteSession(id: number): Promise<void> {
  await api.delete(`/sessions/${id}`)
}

export async function getSessionMessages(sessionId: number): Promise<Message[]> {
  const { data } = await api.get(`/sessions/${sessionId}/messages`)
  return data
}

// 生成相关
export interface GenerateResponse {
  message_id: number
  task_id: string
  status: string
}

export async function textToVideo(
  sessionId: number,
  prompt: string,
  aspectRatio: string = '9:16',
  duration: string = '10'
): Promise<GenerateResponse> {
  const { data } = await api.post('/generate/text-to-video', {
    session_id: sessionId,
    prompt,
    aspect_ratio: aspectRatio,
    duration,
  })
  return data
}

export async function imageToVideo(
  sessionId: number,
  prompt: string,
  imageUrl: string,
  aspectRatio: string = '9:16',
  duration: string = '10'
): Promise<GenerateResponse> {
  const { data } = await api.post('/generate/image-to-video', {
    session_id: sessionId,
    prompt,
    image_url: imageUrl,
    aspect_ratio: aspectRatio,
    duration,
  })
  return data
}

export interface TaskStatus {
  message_id: number
  status: string
  video_url: string | null
  error_message: string | null
}

export async function getTaskStatus(messageId: number): Promise<TaskStatus> {
  const { data } = await api.get(`/generate/status/${messageId}`)
  return data
}

export async function uploadImage(file: File): Promise<{ filename: string; url: string }> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/generate/upload-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
