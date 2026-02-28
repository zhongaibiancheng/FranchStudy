import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'
// 导入页面组件
const FrenchLesson = () => import('@/views/FrenchLesson.vue')
const LessonReader = () =>import('@/views/LessonReader.vue')
const WordList = () =>import('@/views/WordList.vue')
const Word01 = () =>import('@/views/Word01.vue')
const GrammarQuotes = () =>import('@/views/GrammarQuotes.vue')
const Notes = () =>import('@/views/Notes.vue')
const DictationPage = () =>import('@/views/DictationPage.vue')

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue')
  },
  {
    path: '/book2/lesson',
    name: 'FrenchLesson',
    component: FrenchLesson,
    meta: { requiresAuth: true }
  },
  {
    path: '/lessonReader',
    name: 'LessonReader',
    component: LessonReader,
    meta: { requiresAuth: true }
  },
  {
    path: '/wordList',
    name: 'WordList',
    component: WordList,
    meta: { requiresAuth: true }
  },
  {
    path: '/word01',
    name: 'Word01',
    component: Word01,
    meta: { requiresAuth: true }
  },
  {
    path: '/grammarQuotes',
    name: 'GrammarQuotes',
    component: GrammarQuotes,
    meta: { requiresAuth: true }
  },
  {
    path: '/notes',
    name: 'Notes',
    component: Notes,
    meta: { requiresAuth: true }
  },
  {
    path: '/dictationPage',
    name: 'DictationPage',
    component: DictationPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresAuth: false }
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 添加路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    // 检查用户是否已登录
    if (!userStore.isAuthenticated) {
      // 未登录，重定向到登录页面
      next('/login')
      return
    }
    
    // 检查是否需要管理员权限
    if (to.meta.requiresAdmin && !userStore.isAdmin) {
      // 不是管理员，重定向到首页
      next('/')
      return
    }
  }
  
  // 检查是否已经登录却访问登录页面
  if (to.path === '/login' && userStore.isAuthenticated) {
    // 已登录，重定向到题库列表页面
    next('/dictationPage')
    return
  }
  
  // 继续导航
  next()
})

export default router