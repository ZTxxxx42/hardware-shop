import axios from 'axios'
import { ElMessage } from 'element-plus'

interface ApiErrorBody {
  message?: string
  detail?: string | Array<{ msg?: string }>
}

export function getApiErrorMessage(error: unknown) {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as ApiErrorBody | undefined
    if (data?.message) return data.message
    if (typeof data?.detail === 'string') return data.detail
    if (Array.isArray(data?.detail)) {
      const messages = data.detail.map((item) => item.msg).filter(Boolean)
      if (messages.length) return messages.join('；')
    }
    if (!error.response) return '无法连接后端服务，请确认 API 服务已启动'
  }
  if (error instanceof Error) return error.message
  return ''
}

export function showRequestError(error: unknown, fallback = '请求失败，请稍后重试') {
  ElMessage.error(getApiErrorMessage(error) || fallback)
}
