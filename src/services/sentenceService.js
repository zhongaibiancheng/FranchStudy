// WordService.js
import sentenceData_01 from '@/data/lesson_01/lesson1_gold_sentence.json'
import sentenceData_03 from '@/data/lesson_03/lesson3_gold_sentence.json'

const wordDatas = {
  1: sentenceData_01,
  3: sentenceData_03,

}

// 小工具函数：根据课号拿到对应的 sentence
function getSentenceDataByLesson(lesson) {
  const data = wordDatas[lesson]
  if (!data) {
    console.warn('[WordService] 未找到该课号的数据，lesson =', lesson)
    return {}        // 返回空对象，避免报错
  }
  return data
}

export default getSentenceDataByLesson
