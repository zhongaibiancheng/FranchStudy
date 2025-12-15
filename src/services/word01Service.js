// WordService.js
import wordData_01 from '@/data/lesson_01/words_01_01.json'
import wordData_02 from '@/data/lesson_02/words_01.json'
// import wordData_03 from '@/data/lesson_03/words_01.json'
import wordData_04 from '@/data/lesson_04/words_01.json'

const wordDatas = {
  1: wordData_01,
  2: wordData_02,
  // 3: wordData_03,
  4: wordData_04,

}

// 小工具函数：根据课号拿到对应的 wordData
function getWordDataByLesson(lesson) {
  const data = wordDatas[lesson]

  if (!data) {
    console.warn('[WordService] 未找到该课号的数据，lesson =', lesson)
    return {}        // 返回空对象，避免报错
  }
  return data
}

export class WordService {
  // 获取某一课所有单词（打平成数组）
  static getAllWords(lesson) {
    const words = []
    const wordData = getWordDataByLesson(lesson)

    return wordData
  }
}

export default WordService
