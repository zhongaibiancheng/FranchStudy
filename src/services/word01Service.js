// WordService.js
import wordData_01 from '@/data/lesson_01/words_01_01.json'
import wordData_02 from '@/data/lesson_02/words_01.json'
import wordData_03 from '@/data/lesson_03/words_01_01.json'
import wordData_04 from '@/data/lesson_04/words_01.json'
import wordData_05 from '@/data/lesson_05/words_01.json'
import wordData_06 from '@/data/lesson_06/words_01.json'

import book_01_wordData_01 from '@/data/book_01/words_01_04.json'
import book_01_wordData_02 from '@/data/book_01/words_05_08.json'
import book_01_wordData_09 from '@/data/book_01/words_09.json'
import book_01_wordData_10 from '@/data/book_01/words_10.json'
import book_01_wordData_11 from '@/data/book_01/words_11.json'
import book_01_wordData_12 from '@/data/book_01/words_12.json'
import book_01_wordData_13 from '@/data/book_01/words_13.json'
import book_01_wordData_14 from '@/data/book_01/words_14.json'
import book_01_wordData_15 from '@/data/book_01/words_15.json'
import book_01_wordData_16 from '@/data/book_01/words_16.json'
import book_01_wordData_17 from '@/data/book_01/words_17.json'
import book_01_wordData_18 from '@/data/book_01/words_18.json'

const wordDatas = {
  1: wordData_01,
  2: wordData_02,
  3: wordData_03,
  4: wordData_04,
  5: wordData_05,
  6: wordData_06
}
const wordDatasBook1 = {
  1: book_01_wordData_01,
  2: book_01_wordData_02,
  // 3: book_01_wordData_03,
  9: book_01_wordData_09,
  10: book_01_wordData_10,
  11: book_01_wordData_11,
  12: book_01_wordData_12,
  13: book_01_wordData_13,
  14: book_01_wordData_14,
  15: book_01_wordData_15,
  16: book_01_wordData_16,
  17: book_01_wordData_17,
  18: book_01_wordData_18
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
