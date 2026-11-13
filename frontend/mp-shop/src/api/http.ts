import { getToken, removeToken } from '@/utils/storage'

export type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE'

export interface RequestOptions {
  url: string
  method?: HttpMethod
  data?: Record<string, unknown>
}

interface ApiErrorBody {
  code?: string
  message?: string
  detail?: unknown
}

export class ApiRequestError extends Error {
  readonly status: number
  readonly code: string

  constructor(message: string, status: number, code = '') {
    super(message)
    this.name = 'ApiRequestError'
    this.status = status
    this.code = code
  }
}

function buildUrl(path: string): string {
  const fallback = import.meta.env.DEV ? 'http://127.0.0.1:8000' : 'https://api.example.com'
  const baseURL = import.meta.env.VITE_API_BASE_URL || fallback
  return `${baseURL.replace(/\/$/, '')}${path}`
}

export function request<T>(options: RequestOptions): Promise<T> {
  const token = getToken()
  return new Promise<T>((resolve, reject) => {
    uni.request({
      url: buildUrl(options.url),
      method: (options.method ?? 'GET') as unknown as UniApp.RequestOptions['method'],
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      timeout: 10_000,
      success: (res) => {
        const status = res.statusCode
        if (status >= 200 && status < 300) {
          resolve(res.data as T)
          return
        }
        if (status === 401) {
          removeToken()
          uni.$emit('auth:unauthorized')
        }
        const body = res.data as ApiErrorBody | undefined
        reject(new ApiRequestError(body?.message || `请求失败(${status})`, status, body?.code))
      },
      fail: (error) => {
        reject(new Error(error.errMsg || '网络异常，请检查网络后重试'))
      },
    })
  })
}

export function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message) return error.message
  return fallback
}
