import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
const FrenchLesson = () => import('@/views/FrenchLesson.vue')
const LessonReader = () =>import('@/views/LessonReader.vue')
const WordList = () =>import('@/views/WordList.vue')
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue')
  },
  {
    path: '/book2/lesson',
    name: 'FrenchLesson',
    component: FrenchLesson
  },
  {
    path: '/lessonReader',
    name: 'LessonReader',
    component: LessonReader
  },
    {
    path: '/wordList',
    name: 'WordList',
    component: WordList
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router