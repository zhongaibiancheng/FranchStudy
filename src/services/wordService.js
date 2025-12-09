// WordService.js
import wordData_01 from '@/data/lesson_01/words_01.json'
import wordData_03 from '@/data/lesson_03/words_01.json'

const wordDatas = {
  1: wordData_01,
  3: wordData_03,
  // 2: wordData_02,
  // 3: wordData_03,
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

    Object.keys(wordData).forEach(level => {
      wordData[level].forEach(word => {
        words.push({
          ...word,
          level, // 确保 level 字段有
          flipped: false,
          id: `${word.lemma}-${level}-${Date.now()}-${Math.random()}`
        })
      })
    })
    return words
  }

  // 获取某一课某个 level 的单词
  static getWordsByLevel(lesson, level) {
    const wordData = getWordDataByLesson(lesson)
    if (level === 'all') {
      return this.getAllWords(lesson)
    }
    return wordData[level] || []
  }

  // 获取某一课有哪些 level（P0 / P1 / P2…）
  static getLevels(lesson) {
    const wordData = getWordDataByLesson(lesson)
    return Object.keys(wordData)
  }
}

export default WordService
