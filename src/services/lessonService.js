// LessonService.js
import lesson_01 from "@/data/lecon1_rester_ou_partir.json";

// 将来有第二课、第三课可以继续加：
// import wordData_02 from '@/data/words_02.json'
// import wordData_03 from '@/data/words_03.json'

const lessonDatas = {
  1: lesson_01,
  // 2: wordData_02,
  // 3: wordData_03,
}

// 小工具函数：根据课号拿到对应的 wordData
function getLessonDataByLesson(lesson) {
  const data = lessonDatas[lesson]
  if (!data) {
    console.warn('[LessonService] 未找到该课号的数据，lesson =', lesson)
    return {}        // 返回空对象，避免报错
  }
  return data
}

export default getLessonDataByLesson
