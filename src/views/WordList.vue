<template>
  <div class="flashcard-app">
    <!-- 顶部控制栏 -->
    <div class="controls">
      <div class="filter-section">
        <label>优先级筛选：</label>
        <button 
          v-for="level in levels" 
          :key="level"
          :class="{ active: activeLevel === level }"
          @click="setActiveLevel(level)"
          class="level-btn"
        >
          {{ level }}
        </button>
        <button 
          @click="setActiveLevel('all')"
          :class="{ active: activeLevel === 'all' }"
          class="level-btn"
        >
          全部
        </button>
      </div>

      <div class="search-section">
        <input 
          v-model="searchQuery"
          placeholder="搜索单词或中文..."
          class="search-input"
          @input="handleSearch"
        >
        <span class="word-count">共 {{ filteredWords.length }} 个单词</span>
      </div>

      <div class="display-controls">
        <button @click="toggleShowChinese" class="control-btn">
          {{ showChinese ? '隐藏中文' : '显示中文' }}
        </button>
        <button @click="toggleRandomOrder" class="control-btn">
          {{ randomOrder ? '顺序显示' : '随机显示' }}
        </button>
        <button @click="resetCards" class="control-btn">重置</button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载单词数据中...</p>
    </div>

    <!-- 单词卡片网格 -->
    <div v-else class="flashcard-grid">
      <div 
        v-for="(word, index) in paginatedWords" 
        :key="word.id"
        class="flashcard"
        :class="{
          'flipped': word.flipped,
          'p0': word.level === 'P0',
          'p1': word.level === 'P1',
          'p2': word.level === 'P2'
        }"
        @click="flipCard(word)"
      >
        <div class="card-inner">
          <!-- 正面：单词信息 -->
          <div class="card-front">
            <div class="word-header">
              <span class="word-lemma">{{ word.lemma }}</span>
              <span class="word-pos">{{ word.pos }}</span>
              <span class="level-badge" :class="word.level.toLowerCase()">{{ word.level }}</span>
            </div>
            
            <div class="word-content">
              <div v-if="showChinese" class="chinese-meaning">
                {{ word.chinese }}
              </div>
              <div v-else class="placeholder">
                👆 点击显示释义
              </div>
            </div>

            <div class="word-tags">
              <span 
                v-for="tag in word.tags" 
                :key="tag"
                class="tag"
              >
                {{ tag }}
              </span>
            </div>
          </div>

          <!-- 背面：详细解释 -->
          <div class="card-back">
            <div class="back-content">
              <div class="meaning-section">
                <h4>中文释义</h4>
                <p>{{ word.chinese }}</p>
              </div>

              <div v-if="word.example_fr" class="example-section">
                <h4>例句</h4>
                <div class="example">
                  <p class="french-example">{{ word.example_fr }}</p>
                  <p class="chinese-example">{{ word.example_zh }}</p>
                </div>
              </div>

              <div v-if="word.grammar_note_zh" class="grammar-section">
                <h4>语法要点</h4>
                <p>{{ word.grammar_note_zh }}</p>
              </div>

              <div class="meta-info">
                <span class="present-tag" :class="{ present: word.present_in_text }">
                  {{ word.present_in_text ? '课文中出现' : '扩展词汇' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无数据提示 -->
    <div v-if="!loading && filteredWords.length === 0" class="no-data">
      <p>没有找到匹配的单词</p>
      <button @click="resetCards" class="control-btn">显示所有单词</button>
    </div>

    <!-- 底部导航 -->
    <div v-if="!loading && totalPages > 1" class="navigation">
      <button @click="prevPage" :disabled="currentPage === 1" class="nav-btn">
        ◀ 上一页
      </button>
      <span class="page-info">第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="nav-btn">
        下一页 ▶
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import WordService from '@/services/wordService'

export default {
  name: 'FlashcardApp',
  setup() {
    // 响应式数据
    const activeLevel = ref('all')
    const searchQuery = ref('')
    const showChinese = ref(false)
    const randomOrder = ref(false)
    const currentPage = ref(1)
    const loading = ref(true)
    const cardsPerPage = 12
    
    // 单词数据
    const allWords = ref([])
    
    // 初始化数据
    const initializeData = async () => {
      try {
        loading.value = true
        allWords.value = WordService.getAllWords()
      } catch (error) {
        console.error('加载单词数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 计算属性
    const levels = computed(() => WordService.getLevels())
    
    const filteredWords = computed(() => {
      let words = allWords.value.filter(word => {
        const matchesLevel = activeLevel.value === 'all' || word.level === activeLevel.value
        const matchesSearch = searchQuery.value === '' || 
          word.lemma.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          word.chinese.includes(searchQuery.value)
        return matchesLevel && matchesSearch
      })
      
      if (randomOrder.value) {
        words = [...words].sort(() => Math.random() - 0.5)
      }
      
      return words
    })
    
    const paginatedWords = computed(() => {
      const start = (currentPage.value - 1) * cardsPerPage
      const end = start + cardsPerPage
      return filteredWords.value.slice(start, end)
    })
    
    const totalPages = computed(() => {
      return Math.ceil(filteredWords.value.length / cardsPerPage)
    })
    
    // 方法
    const setActiveLevel = (level) => {
      activeLevel.value = level
      currentPage.value = 1
    }
    
    const flipCard = (word) => {
      word.flipped = !word.flipped
    }
    
    const toggleShowChinese = () => {
      showChinese.value = !showChinese.value
    }
    
    const toggleRandomOrder = () => {
      randomOrder.value = !randomOrder.value
      currentPage.value = 1
    }
    
    const handleSearch = () => {
      currentPage.value = 1
    }
    
    const resetCards = () => {
      allWords.value.forEach(word => {
        word.flipped = false
      })
      showChinese.value = false
      randomOrder.value = false
      searchQuery.value = ''
      activeLevel.value = 'all'
      currentPage.value = 1
    }
    
    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }
    
    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }
    
    // 生命周期
    onMounted(() => {
      initializeData()
    })
    
    return {
      activeLevel,
      searchQuery,
      showChinese,
      randomOrder,
      currentPage,
      loading,
      levels,
      filteredWords,
      paginatedWords,
      totalPages,
      setActiveLevel,
      flipCard,
      toggleShowChinese,
      toggleRandomOrder,
      handleSearch,
      resetCards,
      nextPage,
      prevPage
    }
  }
}
</script>

<style scoped>
/* 样式保持不变，与之前相同 */
.flashcard-app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.controls {
  background: white;
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
}

.filter-section, .search-section, .display-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.level-btn {
  padding: 8px 16px;
  border: 2px solid #e9ecef;
  border-radius: 20px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.level-btn.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.search-input {
  padding: 8px 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  width: 200px;
}

.word-count {
  font-size: 0.9em;
  color: #666;
}

.control-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.3s ease;
}

.control-btn:hover {
  background: #e9ecef;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: white;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 2s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-data {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 15px;
  color: #666;
}

.flashcard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.flashcard {
  height: 200px;
  perspective: 1000px;
  cursor: pointer;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flashcard.flipped .card-inner {
  transform: rotateY(180deg);
}

.card-front, .card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.card-front {
  background: white;
}

.card-back {
  background: #f8f9fa;
  transform: rotateY(180deg);
  overflow-y: auto;
}

/* 优先级颜色标识 */
.p0 .card-front { border-left: 6px solid #e74c3c; }
.p1 .card-front { border-left: 6px solid #f39c12; }
.p2 .card-front { border-left: 6px solid #27ae60; }

.word-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.word-lemma {
  font-size: 1.4em;
  font-weight: bold;
  color: #2c3e50;
}

.word-pos {
  color: #7f8c8d;
  font-size: 0.9em;
}

.level-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  color: white;
  font-weight: bold;
}

.level-badge.p0 { background: #e74c3c; }
.level-badge.p1 { background: #f39c12; }
.level-badge.p2 { background: #27ae60; }

.word-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chinese-meaning {
  font-size: 1.2em;
  color: #34495e;
  text-align: center;
}

.placeholder {
  color: #bdc3c7;
  font-style: italic;
}

.word-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tag {
  background: #ecf0f1;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  color: #7f8c8d;
}

.back-content h4 {
  margin: 10px 0 5px 0;
  color: #2c3e50;
  font-size: 1em;
}

.back-content p {
  margin: 0;
  color: #34495e;
  line-height: 1.4;
}

.example {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 8px;
  margin: 5px 0;
}

.french-example {
  font-style: italic;
  color: #2c3e50;
}

.chinese-example {
  color: #7f8c8d;
  font-size: 0.9em;
}

.present-tag {
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 0.8em;
  font-weight: bold;
}

.present-tag.present {
  background: #d4edda;
  color: #155724;
}

.present-tag:not(.present) {
  background: #fff3cd;
  color: #856404;
}

.navigation {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  background: white;
  padding: 15px;
  border-radius: 15px;
}

.nav-btn {
  padding: 10px 20px;
  border: 2px solid #3498db;
  background: white;
  color: #3498db;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-btn:not(:disabled):hover {
  background: #3498db;
  color: white;
}

.page-info {
  font-weight: bold;
  color: #2c3e50;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .flashcard-grid {
    grid-template-columns: 1fr;
  }
  
  .controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-section, .search-section, .display-controls {
    justify-content: center;
  }
  
  .search-input {
    width: 100%;
  }
}
</style>