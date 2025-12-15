<template>
  <div class="word-app">
    <!-- 头部 -->
    <div class="app-header">
      <h1>法语单词默写学习系统</h1>
      <!-- 印刷 / 导出功能：移动到页面头部 -->
      <div class="export-section">
        <div class="export-options">
          <button @click="toggleSelectAll" class="select-all-btn">
            {{ selectedWords.length === filteredWords.length ? '取消全选' : '全选当前单词' }}
          </button>
          <span style="margin-left: 15px; color: #e0e0e0;">
            已选择 {{ selectedWords.length }} / 共 {{ filteredWords.length }} 个单词
          </span>

          <button @click="downloadPracticeSheet" class="export-btn both-btn">
            下载练习
          </button>
          <button @click="downloadAnswerSheet" class="export-btn both-btn">
            下载答案
          </button>
          <button @click="goBack" class="export-btn both-btn">
            返回
          </button>
        </div>
      </div>
    </div>
    
    <!-- 控制区域（去掉优先级分类） -->
    <div class="controls">
      <div class="control-group">
        <input 
          v-model="searchQuery"
          placeholder="搜索单词或中文..."
          class="search-input"
          @input="handleSearch"
        >
        <span class="word-count">共 {{ filteredWords.length }} 个单词</span>
      </div>
      
      <div class="control-group">
        <button @click="toggleRandomOrder" class="action-btn">
          {{ randomOrder ? '顺序显示' : '随机显示' }}
        </button>
        <button @click="resetSelection" class="action-btn secondary">
          重置（恢复默认全选）
        </button>
      </div>
    </div>
    
    <!-- 单词列表（不分页，全部展示） -->
    <div class="word-list">
      <div 
        v-for="word in filteredWords" 
        :key="word.id"
        :class="['word-card', { selected: selectedWords.includes(word.id) }]"
        @click="toggleWordSelection(word.id)"
      >
        <div class="word-header">
          <span class="word-lemma">{{ word.lemma }}</span>
          <span class="word-pos">{{ word.pos }}</span>
        </div>
        
        <div class="word-chinese">{{ word.chinese }}</div>
        
        <div class="word-tags">
          <span v-for="tag in word.tags" :key="tag" class="word-tag">
            {{ tag }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import WordService from '@/services/word01Service'
import { useRouter, useRoute } from 'vue-router'

const searchQuery = ref('')
const randomOrder = ref(false)
const selectedWords = ref([])
const allWords = ref([])
const loading = ref(false)
const lesson = ref(1)

const router = useRouter()
const route = useRoute()
const goBack=()=>{
  router.push('/')
}
// 过滤后的单词列表（只按搜索过滤，不再按 level 分类）
const filteredWords = computed(() => {
  let words = allWords.value.filter(word => {
    const q = searchQuery.value.trim().toLowerCase()
    if (!q) return true
    return (
      word.lemma.toLowerCase().includes(q) ||
      (word.chinese && word.chinese.includes(searchQuery.value))
    )
  })

  if (randomOrder.value) {
    words = shuffleArray([...words])
  }

  return words
})

const title = computed(() => {
  // 创建一个Date对象，表示当前时刻
  const now = new Date();

  // 获取年份、月份（注意月份从0开始，需+1）、日期
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0'); // 用padStart补零
  const day = String(now.getDate()).padStart(2, '0');

  // 获取时、分、秒
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');

  // 拼接成所需格式的字符串，例如 'YYYY-MM-DD HH:mm:ss'
  const formattedString = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;

  return `第 ${lesson.value} 课单词练习 - ${formattedString}`
})
// 方法
const toggleRandomOrder = () => {
  randomOrder.value = !randomOrder.value
}

const handleSearch = () => {
  // 搜索时不改变选择状态，只更新显示
}

const toggleWordSelection = (wordId) => {
  const index = selectedWords.value.indexOf(wordId)
  if (index === -1) {
    selectedWords.value.push(wordId)
  } else {
    selectedWords.value.splice(index, 1)
  }
}

const toggleSelectAll = () => {
  if (selectedWords.value.length === filteredWords.value.length) {
    // 取消全选
    selectedWords.value = []
  } else {
    // 全部选中当前过滤结果
    selectedWords.value = filteredWords.value.map(word => word.id)
  }
}

const resetSelection = () => {
  searchQuery.value = ''
  randomOrder.value = false
  // 恢复默认：所有单词全选
  selectedWords.value = allWords.value.map(word => word.id)
}

// 打乱数组
const shuffleArray = (array) => {
  const result = [...array]
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[result[i], result[j]] = [result[j], result[i]]
  }
  return result
}


// ✅ 按“当前页面显示顺序(含乱序)”输出已选单词
const getSelectedWordDataInDisplayOrder = () => {
  const selectedSet = new Set(selectedWords.value)

  // 当前页面显示顺序（已包含随机/顺序 + 搜索过滤）
  const displayList = filteredWords.value

  // 先按显示顺序取出已选
  const inDisplay = displayList.filter(w => selectedSet.has(w.id))

  // 兼容：如果有些已选单词不在当前过滤结果里（比如你搜索过），把它们补到最后（按原始顺序）
  const displayIdSet = new Set(displayList.map(w => w.id))
  const others = allWords.value.filter(w => selectedSet.has(w.id) && !displayIdSet.has(w.id))

  return [...inDisplay, ...others]
}

// HTML 生成 & 下载
const generatePracticeSheetHTML = () => {
  const selectedWordData = getSelectedWordDataInDisplayOrder()
  
  const wordsHTML = selectedWordData.map((word, index) => `
    <div class="practice-item">
      <div class="word-info">
        <span class="word-number">${index + 1}.</span>
        <span class="word-chinese-practice">${escapeHtml(word.chinese+"("+word.part_of_speech_full_chinese+" - "+word.part_of_speech+" )")}</span>
        <span class="word-pos-practice">${escapeHtml(word.pos)}</span>
      </div>
      <div class="answer-line"></div>
    </div>
  `).join('')
  
  // 保持你原来的整体 HTML 结构，这里只写一个最简外壳示例
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>${title.value}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .practice-item { margin-top: 12px; padding:12px;background-color:#f5f5f5}
    .word-info { margin-bottom: 4px; }
    .answer-line { border-bottom: 4px double #333; height: 24px; }
  </style>
</head>
<body style="display:flex;flex-direction:column;align-items:center;">
  <h1>${title.value}</h1>
  <div style="display:flex;flex-wrap: wrap; ">
  ${wordsHTML}
  </div>
</body>
</html>`
}

const generateAnswerSheetHTML = () => {
  const selectedWordData = getSelectedWordDataInDisplayOrder()
  
  const wordsHTML = selectedWordData.map((word, index) => `
    <div class="answer-item">
      <div class="word-info">
        <span class="word-number">${index + 1}.</span>
        <span class="word-chinese-practice">${escapeHtml(word.chinese+"("+word.part_of_speech_full_chinese+" - "+word.part_of_speech+" )")}</span>
        <span class="word-pos-practice">${escapeHtml(word.pos)}</span>
      </div>
      <div class="word-answer">${escapeHtml(word.french)}</div>
    </div>
  `).join('')
  
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>${title.value} 答案</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .answer-item { margin-top: 12px; padding:12px;background-color:#f5f5f5}
    .word-info { margin-bottom: 4px; }
    .word-answer { border-bottom: 4px double #333; height: 24px;}
  </style>
</head>
<body style="display:flex;flex-direction:column;align-items:center;">
  <h1>${title.value} 答案</h1>
  <div style="display:flex;flex-wrap: wrap; ">
    ${wordsHTML}
  </div>
</body>
</html>`
}

const escapeHtml = (text) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

const downloadFile = (content, filename, contentType = 'text/html;charset=utf-8') => {
  const blob = new Blob([content], { type: contentType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const downloadPracticeSheet = () => {
  if (selectedWords.value.length === 0) {
    alert('请先选择要下载的单词')
    return
  }
  
  const htmlContent = generatePracticeSheetHTML()
  const filename = `法语单词默写练习_${new Date().toISOString().split('T')[0]}.html`
  downloadFile(htmlContent, filename)
}

const downloadAnswerSheet = () => {
  if (selectedWords.value.length === 0) {
    alert('请先选择要下载的单词')
    return
  }
  
  const htmlContent = generateAnswerSheetHTML()
  const filename = `法语单词默写答案_${new Date().toISOString().split('T')[0]}.html`
  downloadFile(htmlContent, filename)
}

// 初始化数据：加载单词并默认全选
const initializeData = async () => {
  try {
    loading.value = true
    lesson.value = route.query.lesson
    allWords.value = WordService.getAllWords(lesson.value) || []
    // 默认所有单词选中
    selectedWords.value = allWords.value.map(word => word.id)
  } catch (error) {
    console.error('加载单词数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  initializeData()
})
</script>

<style scoped>
.word-app {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.app-header {
  background: #2c3e50;
  color: white;
  padding: 25px 30px 10px;
  text-align: center;
}

.app-header h1 {
  font-size: 2.2em;
  margin-bottom: 10px;
  font-weight: 600;
}

.app-header p {
  opacity: 0.8;
  font-size: 1.1em;
}

/* 顶部导出区域样式稍微调一下，适配深色背景 */
.export-section {
  margin-top: 20px;
  padding: 15px 20px 20px;
  background: rgba(0, 0, 0, 0.15);
  border-radius: 12px;
}

.export-options {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 12px;
  justify-content: center;
  align-items: center;
}

.export-btn {
  padding: 10px 18px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95em;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.export-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25);
}

.practice-btn { background: #2ecc71; color: white; }
.answer-btn { background: #e67e22; color: white; }
.both-btn { background: #9b59b6; color: white; }

.select-all-btn {
  background: #34495e;
  color: white;
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9em;
}

/* 控制区域 */
.controls {
  padding: 25px 30px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
  justify-content: space-between;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-input {
  padding: 10px 15px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  width: 260px;
  font-size: 1em;
}

.action-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: #3498db;
  color: white;
  cursor: pointer;
  font-size: 1em;
  font-weight: 600;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: #2980b9;
  transform: translateY(-2px);
}

.action-btn.secondary {
  background: #95a5a6;
}

.action-btn.secondary:hover {
  background: #7f8c8d;
}

.word-count {
  font-size: 1em;
  color: #6c757d;
  font-weight: 500;
}

/* 单词列表 */
.word-list {
  padding: 30px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  max-height: 650px;
  overflow-y: auto;
}

.word-card {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.word-card:hover {
  border-color: #3498db;
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.word-card.selected {
  border-color: #e74c3c;
  background: #fff5f5;
}

.word-card.selected::after {
  content: "✓";
  position: absolute;
  top: 10px;
  right: 10px;
  background: #e74c3c;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.word-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.word-lemma {
  font-size: 1.5em;
  font-weight: bold;
  color: #2c3e50;
}

.word-pos {
  color: #7f8c8d;
  font-size: 0.9em;
  background: #ecf0f1;
  padding: 2px 8px;
  border-radius: 10px;
}

.word-chinese {
  font-size: 1.2em;
  color: #34495e;
  margin-bottom: 10px;
}

.word-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 10px;
}

.word-tag {
  background: #ecf0f1;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 0.8em;
  color: #7f8c8d;
}

/* 响应式 */
@media (max-width: 768px) {
  .controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .control-group {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .search-input {
    width: 100%;
  }
  
  .word-list {
    grid-template-columns: 1fr;
  }

  .export-options {
    flex-direction: column;
  }

  .export-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
