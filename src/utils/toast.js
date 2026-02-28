import { useToast } from 'vue-toastification'

const toast = useToast()

// 图标配置（可以使用 emoji、SVG 或 CSS 类）
const icons = {
  success: '✅',
  info: 'ℹ️',
  warning: '⚠️',
  error: '❌'
}

// 背景颜色配置（Tailwind CSS 类）
const backgrounds = {
  success: '!bg-green-500 !text-white',
  info: '!bg-blue-500 !text-white', 
  warning: '!bg-yellow-500 !text-white',
  error: '!bg-red-500 !text-white'
}

// 自定义 Toast 组件配置
const toastConfig = {
  timeout: 4000,
  position: 'top-right',
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  icon: true,
  rtl: false
}

/**
 * 显示成功提示
 * @param {string} message - 提示消息
 * @param {object} options - 自定义选项
 */
export const showSuccess = (message, options = {}) => {
  return toast.success(message, {
    ...toastConfig,
    timeout: 1500,
    icon: icons.success,
    className: backgrounds.success,
    ...options
  })
}

/**
 * 显示信息提示
 * @param {string} message - 信息消息
 * @param {object} options - 自定义选项
 */
export const showInfo = (message, options = {}) => {
  return toast.info(message, {
    ...toastConfig,
    timeout: 1500,
    icon: icons.info,
    className: backgrounds.info,
    ...options
  })
}

/**
 * 显示警告提示
 * @param {string} message - 警告消息
 * @param {object} options - 自定义选项
 */
export const showWarn = (message, options = {}) => {
  return toast.warning(message, {
    ...toastConfig,
    timeout: 1500,
    icon: icons.warning,
    className: backgrounds.warning,
    ...options
  })
}

/**
 * 显示错误提示
 * @param {string} message - 错误消息
 * @param {object} options - 自定义选项
 */
export const showError = (message, options = {}) => {
  return toast.error(message, {
    ...toastConfig,
    timeout: 2000, // 错误提示显示时间最长
    icon: icons.error,
    className: backgrounds.error,
    ...options
  })
}

// 默认导出所有函数
export default {
  toast:toast,
  success: showSuccess,
  info: showInfo,
  warn: showWarn,
  warning: showWarn, // 别名
  error: showError
}