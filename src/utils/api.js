import axios from 'axios'
import { useUserStore } from '../stores/user'
// 获取API基础URL，支持开发环境和生产环境
const getBaseURL = () => {
  // 在Vite中，只有VITE_前缀的环境变量才会被注入
  const env = import.meta.env
  
  // 如果环境变量中定义了API URL，则使用该URL
  if (env.VITE_API_URL) {
    return env.VITE_API_URL
  }
  
  // 生产环境使用相对路径
  if (env.MODE === 'production') {
    return env.VITE_API_URL
  }
  
  // 默认开发环境使用本地后端地址
  return 'http://127.0.0.1:5000'
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    console.log(error)
    if (error.response && error.response.status === 401) {
      // token过期或无效，清除本地存储
      console.error("token过期或无效，清除本地存储")
      const userStore = useUserStore()
      userStore.logout()
      
      // 跳转到登录页
      router.push('/login')

    } else if (error.response && error.response.status >= 500) {
      // 服务器错误
      console.error('服务器错误:', error.response.data)
    } 
    else if (error.response && error.response.status >= 400 && error.response.status != 404 && error.response.status != 403){
      // 客户端错误
      console.error('请求错误:', error.response.data)
    }
    return Promise.reject(error)
  }
)

export default api