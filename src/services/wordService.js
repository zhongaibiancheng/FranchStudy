import wordData from '@/data/frenchWords.json'

export class WordService {
  static getAllWords() {
    const words = []
    Object.keys(wordData).forEach(level => {
      wordData[level].forEach(word => {
        words.push({
          ...word,
          flipped: false,
          id: `${word.lemma}-${level}-${Date.now()}-${Math.random()}`
        })
      })
    })
    return words
  }

  static getWordsByLevel(level) {
    if (level === 'all') {
      return this.getAllWords()
    }
    return wordData[level] || []
  }

  static getLevels() {
    return Object.keys(wordData)
  }
}

export default WordService