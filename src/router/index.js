import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
const FrenchLesson1 = () => import('@/views/FrenchLesson1.vue')
const LessonReader = () =>import('@/views/LessonReader.vue')
const WordList = () =>import('@/views/WordList.vue')
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue')
  },
  {
    path: '/book2/lesson1',
    name: 'FrenchLesson1',
    component: FrenchLesson1
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