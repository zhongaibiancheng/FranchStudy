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

      <button @click="downloadWordCards" class="export-btn">
        ⬇️ 下载
      </button>
      <button @click="goBack" class="export-btn">
        ⬅️ 返回
      </button>
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
import { useRouter,useRoute } from 'vue-router'

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
    
    const router = useRouter()
    const route = useRoute()
    const lesson = ref(1)

    // 单词数据
    const allWords = ref([])
    
    // 小工具：转义 HTML 特殊字符
    const escapeHtml = (str) => {
      return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
    }

    const goBack=()=>{
      router.push('/')
    }
    const downloadWordCards = () => {
      if (!filteredWords.value.length) {
        alert('当前没有单词可导出，请先取消筛选或检查搜索条件。')
        return
      }

      // 1. 生成每一行“可对折的卡片”
      const cardsHtml = filteredWords.value.map((w, idx) => {
        const lemma = escapeHtml(w.lemma)
        const pos = escapeHtml(w.pos)
        const level = escapeHtml(w.level)
        const zh = escapeHtml(w.chinese)
        const exZh = escapeHtml(w.example_zh || '（暂无中文例句）')
        const exFr = escapeHtml(w.example_fr || '（暂无法语例句）')
        const grammar = escapeHtml(w.grammar_note_zh || '（语法解释可选记忆）')

        const indexNo = idx + 1   // ✅ 序号

        return `
          <div class="card-row">
            <!-- 左半边：提示面（先看这边） -->
            <div class="card-half card-left">
              <div class="card-header">
                <span class="word-index">${indexNo}.</span>
                <span class="lemma">${lemma}</span>
                <span class="pos">${pos}</span>
                <span class="level-badge level-${level.toLowerCase()}">${level}</span>
              </div>
              <div class="section">
                <div class="label">释义</div>
                <div class="text">${zh}</div>
              </div>
              <div class="section">
                <div class="label">例句</div>
                <div class="text">${exZh}</div>
              </div>
            </div>

            <!-- 右半边：答案面（对折后藏在里面） -->
            <div class="card-half card-right">
              <div class="section">
                <div class="label">例句</div>
                <div class="text fr">${exFr}</div>
              </div>
              <div class="section">
                <div class="label">语法要点</div>
                <div class="text grammar">${grammar}</div>
              </div>
            </div>
          </div>
        `
      }).join('\n')

      // 2. 整个 HTML 文档（A4 横向，两栏，对折）
      const html = `
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="utf-8" />
      <title>第 ${lesson.value} 课法语单词</title>
      <style>
        @page {
          size: A4 landscape;   /* A4 横向 */
          margin: 10mm;
        }
        body {
          font-family: "Microsoft YaHei", Arial, sans-serif;
          font-size: 12px;
          line-height: 1.4;
          counter-reset: page;
        }
        .page-footer {
          position: fixed;
          bottom: 4mm;
          right: 10mm;
          font-size: 10px;
          color: #888;
        }

        h1 {
          text-align: center;
          margin: 0 0 4mm 0;
        }
        p.tip {
          text-align: center;
          margin: 0 0 8mm 0;
          color: #555;
          font-size: 11px;
        }
        .card-row {
          display: flex;
          border: 1px solid #333;
          margin-bottom: 6mm;
          page-break-inside: avoid;
        }
        .card-half {
          flex: 1;
          padding: 8px 10px;
          box-sizing: border-box;
        }
        .card-left {
          border-right: 1px dashed #999; /* 中间虚线，折叠线 */
          background: #ffffff;
        }
        .card-right {
          background: #f8f9fa;
        }
        .card-header {
          display: flex;
          align-items: baseline;
          gap: 6px;
          margin-bottom: 4px;
        }
        .lemma {
          font-size: 18px;
          font-weight: bold;
          color: #2c3e50;
        }
        .pos {
          font-size: 12px;
          color: #7f8c8d;
        }
        .level-badge {
          font-size: 11px;
          padding: 1px 6px;
          border-radius: 10px;
          border: 1px solid #999;
        }
        .level-p0 { background: #fdecea; }
        .level-p1 { background: #fff4e5; }
        .level-p2 { background: #e6f4ea; }

        .section {
          margin-top: 4px;
        }
        .label {
          font-weight: bold;
          margin-bottom: 2px;
          color: #2c3e50;
          font-size: 11px;
        }
        .text {
          white-space: pre-wrap;
          word-wrap: break-word;
        }
        .text.fr {
          font-style: italic;
          color: #34495e;
        }
        .text.grammar {
          font-size: 11px;
          color: #555;
        }

        .card-row:nth-child(odd) .card-left {
          background: #fafafa;
        }
      </style>
    </head>
    <body>
    <h1>第 ${lesson.value} 课 法语单词</h1>
      <p class="tip">
        打印时请选择“A4 横向”。打印出来后沿中间虚线对折：
        先看左边（单词 + 中文 + 中文例句），不会再翻开右边的法语例句和语法解释。
      </p>
      ${cardsHtml}
    </body>
    </html>
      `

      // 3. 生成 Blob，触发浏览器下载 .html 文件
      const blob = new Blob([html], {
        type: 'text/html;charset=utf-8;'
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      const dateStr = new Date().toISOString().split('T')[0]

      a.href = url
      a.download = `lecon1_cards_fold_${dateStr}.html`  // 文件名
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }


    // 初始化数据
    const initializeData = async () => {
      try {
        loading.value = true
        console.log(route.query)
        lesson.value = route.query.lesson

        allWords.value = WordService.getAllWords(lesson.value)
      } catch (error) {
        console.error('加载单词数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 计算属性
    const levels = computed(() => WordService.getLevels(lesson.value))
    
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
      router,
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
      goBack,
      setActiveLevel,
      flipCard,
      toggleShowChinese,
      toggleRandomOrder,
      handleSearch,
      resetCards,
      nextPage,
      prevPage,
      downloadWordCards
    }
  }
}
</script>

<style scoped>
/* 样式保持不变，与之前相同 */
.flashcard-app {
  max-width: 1400px;
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
.export-controls {
  background: white;
  padding: 25px;
  border-radius: 10px;
  margin-bottom: 25px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border-left: 4px solid #3498db;
}

.export-controls h3 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 18px;
}

.export-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.export-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  /* color: white; */
}

.export-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.html-btn { background: #e74c3c; }
.json-btn { background: #f39c12; }
.text-btn { background: #27ae60; }
.csv-btn { background: #3498db; }
.md-btn { background: #9b59b6; }

.export-options {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 15px;
}

.option-group {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.option-group label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  font-size: 14px;
}

.option-group select {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.export-info {
  text-align: center;
  color: #666;
  font-size: 14px;
  padding: 10px;
  background: #ecf0f1;
  border-radius: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .export-buttons {
    flex-direction: column;
  }
  
  .export-btn {
    width: 100%;
  }
  
  .option-group {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>