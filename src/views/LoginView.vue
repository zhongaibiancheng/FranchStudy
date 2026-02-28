<template>
  <div class="w-full flex items-center justify-center px-4 py-10">

    <div class="bg-white w-full max-w-md rounded-xl shadow-lg p-6 sm:p-8">

      <h2 class="text-2xl font-bold text-center text-gray-800 mb-6">
        欢迎登录
      </h2>

      <form @submit.prevent="handleLogin" class="space-y-5">

        <!-- 用户名 -->
        <div>
          <label class="form-label">用户名</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
            </svg>
            <input
              v-model="form.username"
              type="text"
              class="form-input"
              :class="{'border-red-500': errors.username}"
              placeholder="请输入用户名"
            />
          </div>
          <p v-if="errors.username" class="form-error">
            {{ errors.username }}
          </p>
        </div>

        <!-- 密码 -->
        <div>
          <label class="form-label">密码</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/>
            </svg>

            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input pr-10"
              :class="{'border-red-500': errors.password}"
              placeholder="请输入密码"
            />

            <button
              type="button"
              @click="togglePasswordVisibility"
              class="absolute right-3 text-gray-500"
            >
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>

          <p v-if="errors.password" class="form-error">
            {{ errors.password }}
          </p>
        </div>

        <!-- 全局错误 -->
        <div v-if="errors.general" class="bg-red-50 border border-red-200 rounded-md p-3">
          <p class="text-sm text-red-700">
            {{ errors.general }}
          </p>
        </div>

        <!-- 按钮 -->
        <button
          type="submit"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50"
          :disabled="loading"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>

        <!-- 注册 -->
        <div class="text-center text-sm text-gray-600">
          还没有账号？
          <router-link to="/register" class="text-blue-600 hover:underline">
            立即注册
          </router-link>
        </div>

      </form>
    </div>

  </div>
</template>


<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import api from '../utils/api'

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    const form = ref({
      username: '',
      password: ''
    })
    const errors = ref({
      username: '',
      password: '',
      general: ''
    })
    const loading = ref(false)
    const showPassword = ref(false)
    
    const togglePasswordVisibility = () => {
      showPassword.value = !showPassword.value
    }
    
    // 验证输入字段
    const validateForm = () => {
      // 清除之前的错误信息
      errors.value.username = ''
      errors.value.password = ''
      errors.value.general = ''
      
      let isValid = true
      
      // 验证用户名
      if (!form.value.username.trim()) {
        errors.value.username = '用户名不能为空'
        isValid = false
      } else if (form.value.username.trim().length < 6) {
        errors.value.username = '用户名长度不能少于6个字符'
        isValid = false
      } else if (form.value.username.trim().length > 20) {
        errors.value.username = '用户名长度不能超过20个字符'
        isValid = false
      } else if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(form.value.username.trim())) {
        errors.value.username = '用户名只能包含字母、数字、下划线和中文字符'
        isValid = false
      }
      
      // 验证密码
      if (!form.value.password) {
        errors.value.password = '密码不能为空'
        isValid = false
      } else if (form.value.password.length < 6) {
        errors.value.password = '密码长度不能少于6个字符'
        isValid = false
      } else if (form.value.password.length > 20) {
        errors.value.password = '密码长度不能超过20个字符'
        isValid = false
      }
      
      return isValid
    }
    
    const handleLogin = async () => {
      // 验证表单
      if (!validateForm()) {
        return
      }
      
      loading.value = true
      try {
        const response = await api.post('/auth/login', form.value)
        if (response.data && response.data.user) {
          const { user, token } = response.data
          userStore.setUser(user)
          const actualToken = token || 'default-token-' + Date.now()
          userStore.setToken(actualToken, 3600000)
          router.push('/')
        } else {
          console.log('响应中缺少用户数据')
          errors.value.general = '登录失败'
        }
      } catch (error) {
        console.error('登录失败:', error)
        // 处理后端返回的错误信息
        if (error.response && error.response.data && error.response.data.error) {
          if (error.response.data.error.includes('用户名或密码错误')) {
            errors.value.general = '用户名或密码错误，请检查后重试'
          } else if (error.response.data.error.includes('缺少必要参数')) {
            errors.value.general = '请输入完整的登录信息'
          } else {
            errors.value.general = error.response.data.error
          }
        } else {
          errors.value.general = '登录失败，请稍后重试'
        }
      } finally {
        loading.value = false
      }
    }
    
    return {
      form,
      errors,
      loading,
      showPassword,
      togglePasswordVisibility,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login .max-h-\[520px\] {
  min-height: 400px;
  height: auto;
}

/* 响应式高度控制 */
@media (min-height: 800px) {
  .login .max-h-\[520px\] {
    height: 520px;
  }
  .login .pt-20 {
    padding-top: 8rem;
  }
}

@media (max-height: 700px) {
  .login .max-h-\[520px\] {
    height: 450px;
  }
  .login .pt-20 {
    padding-top: 4rem;
  }
}

@media (max-height: 600px) {
  .login .max-h-\[520px\] {
    height: 380px;
  }
  .login .pt-20 {
    padding-top: 2rem;
  }
  .login .pb-8 {
    padding-bottom: 1rem;
  }
}

/* 确保表单内容不会溢出 */
.login form {
  min-height: 0;
}

.form-label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.input-wrapper {
  @apply relative;
}

.input-icon {
  @apply absolute left-3 top-3 w-5 h-5 text-gray-400;
}

.form-input {
  @apply w-full pl-10 py-3 border border-gray-300 rounded-lg 
         focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.form-error {
  @apply text-sm text-red-600 mt-1;
}
</style>
