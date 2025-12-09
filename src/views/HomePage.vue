<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

// 课程列表数据
const lessons = [
  { id: 1, title: 'Leçon 1 – Rester ou partir ?','notes':true },
  { id: 2, title: "Leçon 2 – S'orienter" },
  { id: 3, title: "Leçon 3 – Interview d'un personnage",'notes':true },
  { id: 4, title: "Leçon 4 – Trois visages de l'aventure",'notes':false }
]

const goLessonReader = (lesson_id)=>{
  router.push({
    path:'/lessonReader',
    query: {
        lesson: lesson_id
      }
  })
}
const goGrammarQuotes = (lesson_id)=>{
  router.push({
    path:'/grammarQuotes',
    query: {
        lesson: lesson_id
      }
  })
}

const goWordList = (lesson_id)=>{
  router.push({
    path:'/wordList',
    query: {
        lesson: lesson_id
      }
  })
}
const goNotes =(lesson_id)=>{
  router.push({
    path:'/notes',
    query: {
        lesson: lesson_id
      }
  })
}
</script>

<template>
  <div class="home-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <h1>法语学习系统</h1>
      <p>北外法语修订版 第二册</p>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
      <div class="book-card">
        <div class="book-cover">
          <h2>第二册</h2>
          <div class="book-decoration">📚</div>
        </div>
        
        <div class="lessons-section">
          <h3>课程列表</h3>
          <div class="lessons-list">
            <div 
              v-for="(lesson,index) in lessons" 
              :key="lesson.id"
              class="lesson-item"
            >
              <span class="lesson-number">第 {{ lesson.id }} 课</span>
              <span class="lesson-title">{{ lesson.title }}</span>
              <span class="lesson-arrow">→</span>
              <div>
                <button @click="goLessonReader(index+1)">看课文</button>
                <button @click="goGrammarQuotes(index+1)">背例句</button>
                <button @click="goWordList(index+1)">背单词</button>
                <button @click="goNotes(index+1)" v-if="lesson.notes">课文备注</button>
              </div>

            </div>
          
        </div>
        </div>
      </div>

      <!-- 学习统计 -->
      <div class="stats-section">
        <h3>学习进度</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">0/12</div>
            <div class="stat-label">已学课程</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">0%</div>
            <div class="stat-label">总体进度</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">0</div>
            <div class="stat-label">掌握单词</div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.page-header {
  text-align: center;
  color: white;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 2.5em;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.page-header p {
  font-size: 1.2em;
  opacity: 0.9;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.book-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  display: flex;
  gap: 30px;
}

.book-cover {
  flex: 0 0 200px;
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  border-radius: 15px;
  padding: 30px;
  color: white;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.book-cover h2 {
  font-size: 2em;
  margin-bottom: 20px;
}

.book-decoration {
  font-size: 4em;
}

.lessons-section {
  flex: 1;
}

.lessons-section h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.5em;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

.lessons-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.lesson-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  margin-bottom: 10px;
  background: #f8f9fa;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid #3498db;
}

.lesson-item:hover {
  background: #e3f2fd;
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.lesson-number {
  font-weight: bold;
  color: #2c3e50;
  min-width: 80px;
}

.lesson-title {
  flex: 1;
  color: #34495e;
  font-size: 1.1em;
}

.lesson-arrow {
  color: #7f8c8d;
  font-size: 1.2em;
  transition: transform 0.3s ease;
}

.lesson-item:hover .lesson-arrow {
  transform: translateX(5px);
  color: #3498db;
}

.stats-section {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.stats-section h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  text-align: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 10px;
  transition: transform 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-5px);
}

.stat-number {
  font-size: 2em;
  font-weight: bold;
  color: #3498db;
  margin-bottom: 5px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9em;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .book-card {
    flex-direction: column;
  }
  
  .book-cover {
    flex: none;
    margin-bottom: 20px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .lesson-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .lesson-number {
    min-width: auto;
  }
}
</style>