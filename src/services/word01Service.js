// WordService.js
import wordData_01 from '@/data/lesson_01/words_01_01.json'
import wordData_02 from '@/data/lesson_02/words_01.json'
import wordData_03 from '@/data/lesson_03/words_01_01.json'
import wordData_04 from '@/data/lesson_04/words_01.json'
import wordData_05 from '@/data/lesson_05/words_01.json'

import book_01_wordData_01 from '@/data/book_01/words_01_04.json'
import book_01_wordData_02 from '@/data/book_01/words_05_08.json'
import book_01_wordData_03 from '@/data/book_01/words_09_10.json'
import book_01_wordData_04 from '@/data/book_01/words_11_12.json'
import book_01_wordData_05 from '@/data/book_01/words_13_14.json'

const wordDatas = {
  1: wordData_01,
  2: wordData_02,
  3: wordData_03,
  4: wordData_04,
  5: wordData_05,
}
const wordDatasBook1 = {
  1: book_01_wordData_01,
  2: book_01_wordData_02,
  3: book_01_wordData_03,
  4: book_01_wordData_04,
  5: book_01_wordData_05
}
// 小工具函数：根据课号拿到对应的 wordData
function getWordDataByLesson(lesson,book) {
  let data
  //第一册
  if(book==1){
    data = wordDatasBook1[lesson]
  }else{
    data = wordDatas[lesson]
  }
  
  if (!data) {
    console.warn('[WordService] 未找到该课号的数据，lesson =', lesson)
    return {}        // 返回空对象，避免报错
  }
  return data
}

export class WordService {
  // 获取某一课所有单词（打平成数组）
  static getAllWords(lesson,book) {
    const words = []
    const wordData = getWordDataByLesson(lesson,book)

    return wordData
  }
}

export default WordService
