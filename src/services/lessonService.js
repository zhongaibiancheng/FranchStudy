// LessonService.js
import lesson_01_01 from "@/data/lesson_01_01.json";
import lesson_01_02 from "@/data/lesson_01_02.json";
// 将来有第二课、第三课可以继续加：
// import wordData_02 from '@/data/words_02.json'
// import wordData_03 from '@/data/words_03.json'

const lessonDatas = {
  '1_1': lesson_01_01,
  '1_2': lesson_01_02,
  // 2: wordData_02,
  // 3: wordData_03,
}

// 小工具函数：根据课号拿到对应的 wordData
function getLessonDataByLesson(lesson,part=1) {
  const data = lessonDatas[lesson+"_"+part]

  if (!data) {
    console.warn('[LessonService] 未找到该课号的数据，lesson =', lesson)
    return {}        // 返回空对象，避免报错
  }
  return data
}

export default getLessonDataByLesson
