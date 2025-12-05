<template>
  <div class="french-lesson">
    <!-- 顶部标题 -->
    <header class="lesson-header">
      <h1>{{ lessonTitle }}</h1>
      <div class="progress-info">
        <span>完成度: {{ completionRate }}%</span>
        <button @click="resetProgress" class="reset-btn">重置进度</button>
      </div>
    </header>

    <!-- 导航菜单 -->
    <nav class="lesson-nav">
      <button 
        v-for="section in sections" 
        :key="section.id"
        :class="{ active: activeSection === section.id }"
        @click="activeSection = section.id"
        class="nav-btn"
      >
        {{ section.title }}
      </button>
    </nav>

    <!-- 内容区域 -->
    <div class="lesson-content">
      <!-- ① 本课概览 -->
      <section v-if="activeSection === 'overview'" class="content-section">
        <h2>① 本课概览</h2>
        
        <div class="theme-keywords">
          <h3>主题关键词：</h3>
          <div class="keywords-grid">
            <span v-for="keyword in keywords" :key="keyword" class="keyword-tag">
              {{ keyword }}
            </span>
          </div>
        </div>

        <div class="story-summary">
          <h3>故事大意（让孩子用中文复述）：</h3>
          <ul>
            <li v-for="(point, index) in storyPoints" :key="index">
              {{ point }}
            </li>
          </ul>
        </div>
      </section>

      <!-- ② 本课语法 -->
      <section v-if="activeSection === 'grammar'" class="content-section">
        <h2>② 本课语法（Grammaire）</h2>
        
        <div class="grammar-point" v-for="point in grammarPoints" :key="point.title">
          <h3>{{ point.title }}</h3>
          <p><strong>用法：</strong>{{ point.usage }}</p>
          <p><strong>结构：</strong>{{ point.structure }}</p>
          
          <div class="examples">
            <h4>例句：</h4>
            <div v-for="(example, index) in point.examples" :key="index" class="example">
              <p class="french">{{ example.french }}</p>
              <p class="chinese">{{ example.chinese }}</p>
            </div>
          </div>
        </div>

        <!-- 小任务 -->
        <div class="exercise">
          <h3>小任务：</h3>
          <p>{{ exercise.description }}</p>
          <div class="exercise-inputs">
            <div v-for="n in 2" :key="n" class="input-group">
              <label>句子 {{ n }}：</label>
              <input 
                v-model="exercise.answers[n-1]"
                :placeholder="exercise.placeholders[n-1]"
                @blur="saveExerciseProgress"
              >
            </div>
          </div>
          <button @click="checkExercise" class="check-btn">检查答案</button>
        </div>
      </section>

      <!-- ③ 必背单词 -->
      <section v-if="activeSection === 'vocabulary'" class="content-section">
        <h2>③ 必背单词（A 档）</h2>
        <p class="vocab-instruction">建议：这些词要 <strong>会读 + 会写 + 会用在句子里</strong></p>
        
        <!-- 动词 -->
        <div class="vocab-category">
          <h3>重要动词 Verbes importants</h3>
          <div class="vocab-grid">
            <div v-for="verb in verbs" :key="verb.french" class="vocab-item">
              <div class="vocab-header">
                <strong>{{ verb.french }}</strong> —— {{ verb.chinese }}
              </div>
              <div class="checkboxes">
                <label v-for="skill in skills" :key="skill">
                  <input 
                    type="checkbox" 
                    v-model="verb.progress[skill]"
                    @change="updateProgress"
                  >
                  {{ skill }}
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- 名词 -->
        <div class="vocab-category">
          <h3>名词和短语 Noms & expressions</h3>
          <div class="vocab-grid">
            <div v-for="noun in nouns" :key="noun.french" class="vocab-item">
              <div class="vocab-header">
                <strong>{{ noun.french }}</strong> —— {{ noun.chinese }}
              </div>
              <div class="checkboxes">
                <label v-for="skill in ['会读', '会写']" :key="skill">
                  <input 
                    type="checkbox" 
                    v-model="noun.progress[skill]"
                    @change="updateProgress"
                  >
                  {{ skill }}
                </label>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ④ 本课金句 -->
      <section v-if="activeSection === 'sentences'" class="content-section">
        <h2>④ 本课金句（Phrases clés）</h2>
        <p class="sentences-instruction">
          目标：这些句子要 <strong>会读 → 会说 → 尽量会写</strong>
        </p>
        
        <div class="sentences-list">
          <div v-for="(sentence, index) in keySentences" :key="index" class="sentence-item">
            <div class="sentence-content">
              <p class="french">{{ sentence.french }}</p>
              <p class="chinese">{{ sentence.chinese }}</p>
            </div>
            <div class="sentence-checkboxes">
              <label v-for="skill in sentenceSkills" :key="skill">
                <input 
                  type="checkbox" 
                  v-model="sentence.progress[skill]"
                  @change="updateProgress"
                >
                {{ skill }}
              </label>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'FrenchLesson',
  setup() {
    // 响应式数据
    const activeSection = ref('overview')
    const lessonData = ref({
      verbs: [],
      nouns: [],
      keySentences: []
    })

    // 课程基本信息
    const lessonTitle = 'Leçon 1 – Rester ou partir ?'
    const keywords = ['vacances（假期）', 'sport（运动）', 'cinéma（电影院）', 'aventure（冒险）']
    const storyPoints = [
      '周五晚上，一家人在餐桌上聊天。',
      '爸爸想在家看 2006 年世界杯决赛。',
      '妈妈吐槽他是"沙发上的运动员"。',
      '孩子们想出去、想去滑雪。',
      '最后决定：今晚全家去电影院；明天一早全家去乡下的房子，在花园里野餐、散步。'
    ]

    // 语法点
    const grammarPoints = [
      {
        title: '1. 最近将来时：aller + 动词原形',
        usage: '表示"马上要 / 打算做某事"（类似英语 be going to do）。',
        structure: '主语 + aller（现在时变位）+ 动词不定式。',
        examples: [
          { french: 'Je vais regarder le match.', chinese: '我要看比赛。' },
          { french: 'On va au cinéma ce soir.', chinese: '我们今晚要去看电影。' }
        ]
      },
      {
        title: '2. 简单将来时：futur simple（本课先盯 nous / vous）',
        usage: '将来某一天会做什么。',
        structure: '词尾重点：nous：-ons，vous：-ez',
        examples: [
          { french: 'Nous irons à la campagne demain.', chinese: '明天我们会去乡下。' },
          { french: 'Vous découvrirez la Bretagne en vélo.', chinese: '你们将骑车游览布列塔尼。' }
        ]
      },
      {
        title: '3. 代词 y / en（先有印象）',
        usage: 'y：表示"在那里 / 到那里"；en：表示"其中一些 / 这件事"',
        structure: 'y 代替「à + 地点」；en 代替「de + 名词」',
        examples: [
          { french: 'On va au cinéma ? – Oui, on y va.', chinese: '我们去电影院吗？——是的，我们去那儿。' },
          { french: 'Tu fais du ski ? – Oui, j\'en fais.', chinese: '你滑雪吗？——对，我滑。' }
        ]
      }
    ]

    // 小任务
    const exercise = ref({
      description: '写两句以 Je vais … 开头的句子（我要去做什么）。写两句以 Nous irons … 开头的句子（我们将会做什么）。',
      placeholders: ['Je vais...（我要去...）', 'Nous irons...（我们将会...）'],
      answers: ['', '']
    })

    // 技能类型
    const skills = ['会读', '会写', '会用句子']
    const sentenceSkills = ['会读', '会说', '会写']

    // 导航菜单
    const sections = [
      { id: 'overview', title: '① 本课概览' },
      { id: 'grammar', title: '② 本课语法' },
      { id: 'vocabulary', title: '③ 必背单词' },
      { id: 'sentences', title: '④ 本课金句' }
    ]

    // 初始化数据
    const initializeData = () => {
      // 动词数据
      const verbsData = [
        { french: 'sortir', chinese: '出去' },
        { french: 'regarder', chinese: '看（电视 / 比赛）' },
        { french: 'aimer', chinese: '喜欢' },
        { french: 'faire (du ski …)', chinese: '做；进行某项运动' },
        { french: 'aller', chinese: '去' },
        { french: 'partir', chinese: '出发，离开' },
        { french: 'manger', chinese: '吃' },
        { french: 'préparer', chinese: '准备' },
        { french: 'pique-niquer', chinese: '野餐（动词）' },
        { french: 'découvrir', chinese: '发现，游览' },
        { french: 'traverser', chinese: '穿越，横穿' },
        { french: 'visiter', chinese: '参观' },
        { french: 'faire de l\'alpinisme', chinese: '登山' },
        { french: 'grimper', chinese: '攀登' },
        { french: 'dominer', chinese: '俯视，俯临' },
        { french: 'vivre', chinese: '生活，度过' },
        { french: 'rater', chinese: '错过，没赶上' }
      ]

      // 名词数据
      const nounsData = [
        { french: 'les vacances', chinese: '假期' },
        { french: 'les vacances de Noël', chinese: '圣诞假期' },
        { french: 'le match / la finale', chinese: '比赛 / 决赛' },
        { french: 'la Coupe du Monde', chinese: '世界杯' },
        { french: 'le foot / le rugby / le tennis / le volley-ball', chinese: '足球 / 橄榄球 / 网球 / 排球' },
        { french: 'le ski', chinese: '滑雪' },
        { french: 'le golf', chinese: '高尔夫球' },
        { french: 'la télé', chinese: '电视' },
        { french: 'le cinéma', chinese: '电影院' },
        { french: 'la campagne', chinese: '乡下' },
        { french: 'le jardin', chinese: '花园' },
        { french: 'un pique-nique', chinese: '野餐（名词）' },
        { french: 'un sandwich', chinese: '三明治' },
        { french: 'une promenade (à pied)', chinese: '散步' },
        { french: 'un livre', chinese: '书' },
        { french: 'une aventure', chinese: '冒险' }
      ]

      // 关键句子数据
      const sentencesData = [
        { french: 'Ce soir, je vais regarder le match de foot à la télé.', chinese: '今晚我要在电视上看足球比赛。' },
        { french: 'Qu\'est-ce que nous ferons pendant les vacances de Noël ?', chinese: '我们圣诞假期要做什么？' },
        { french: 'Nous irons peut-être faire du ski à Grenoble.', chinese: '我们也许会去格勒诺布尔滑雪。' },
        { french: 'Les vacances peuvent aussi être une aventure.', chinese: '假期也可以是一场冒险。' },
        { french: 'Vous découvrirez la Bretagne en vélo.', chinese: '你们将骑车游览布列塔尼。' },
        { french: 'Vous ferez de l\'alpinisme dans les Alpes ou dans les Pyrénées.', chinese: '你们会在阿尔卑斯或比利牛斯山登山。' }
      ]

      // 从本地存储加载数据或初始化
      const savedData = localStorage.getItem('frenchLesson1')
      if (savedData) {
        const parsed = JSON.parse(savedData)
        lessonData.value = parsed
      } else {
        // 初始化进度数据
        lessonData.value.verbs = verbsData.map(verb => ({
          ...verb,
          progress: { '会读': false, '会写': false, '会用句子': false }
        }))
        lessonData.value.nouns = nounsData.map(noun => ({
          ...noun,
          progress: { '会读': false, '会写': false }
        }))
        lessonData.value.keySentences = sentencesData.map(sentence => ({
          ...sentence,
          progress: { '会读': false, '会说': false, '会写': false }
        }))
      }

      // 加载练习答案
      const savedExercise = localStorage.getItem('frenchLesson1Exercise')
      if (savedExercise) {
        exercise.value.answers = JSON.parse(savedExercise)
      }
    }

    // 计算完成度
    const completionRate = computed(() => {
      let totalItems = 0
      let completedItems = 0

      // 计算动词完成度
      lessonData.value.verbs.forEach(verb => {
        Object.values(verb.progress).forEach(isCompleted => {
          totalItems++
          if (isCompleted) completedItems++
        })
      })

      // 计算名词完成度
      lessonData.value.nouns.forEach(noun => {
        Object.values(noun.progress).forEach(isCompleted => {
          totalItems++
          if (isCompleted) completedItems++
        })
      })

      // 计算句子完成度
      lessonData.value.keySentences.forEach(sentence => {
        Object.values(sentence.progress).forEach(isCompleted => {
          totalItems++
          if (isCompleted) completedItems++
        })
      })

      return totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0
    })

    // 更新进度并保存
    const updateProgress = () => {
      localStorage.setItem('frenchLesson1', JSON.stringify(lessonData.value))
    }

    // 保存练习进度
    const saveExerciseProgress = () => {
      localStorage.setItem('frenchLesson1Exercise', JSON.stringify(exercise.value.answers))
    }

    // 检查练习答案
    const checkExercise = () => {
      alert('答案已保存！继续加油！💪')
      saveExerciseProgress()
    }

    // 重置进度
    const resetProgress = () => {
      if (confirm('确定要重置所有学习进度吗？')) {
        localStorage.removeItem('frenchLesson1')
        localStorage.removeItem('frenchLesson1Exercise')
        initializeData()
      }
    }

    // 组件挂载时初始化数据
    onMounted(() => {
      initializeData()
    })

    return {
      lessonTitle,
      activeSection,
      sections,
      keywords,
      storyPoints,
      grammarPoints,
      exercise,
      skills,
      sentenceSkills,
      completionRate,
      checkExercise,
      resetProgress,
      saveExerciseProgress,
      // 返回响应式数据
      verbs: computed(() => lessonData.value.verbs),
      nouns: computed(() => lessonData.value.nouns),
      keySentences: computed(() => lessonData.value.keySentences)
    }
  }
}
</script>

<style scoped>
.french-lesson {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Microsoft YaHei', sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.lesson-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.lesson-header h1 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.8em;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.progress-info span {
  font-weight: bold;
  color: #27ae60;
}

.reset-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.reset-btn:hover {
  background: #c0392b;
}

.lesson-nav {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.nav-btn {
  flex: 1;
  min-width: 120px;
  background: white;
  border: 2px solid #3498db;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: bold;
}

.nav-btn.active {
  background: #3498db;
  color: white;
}

.nav-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.content-section {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.content-section h2 {
  color: #2c3e50;
  border-bottom: 3px solid #3498db;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.theme-keywords h3,
.story-summary h3 {
  color: #34495e;
}

.keywords-grid {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 15px 0;
}

.keyword-tag {
  background: #e3f2fd;
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid #bbdefb;
  font-weight: 500;
}

.story-summary ul {
  padding-left: 20px;
}

.story-summary li {
  margin-bottom: 8px;
  line-height: 1.6;
}

.grammar-point {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 25px;
  border-left: 4px solid #3498db;
}

.grammar-point h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.examples {
  margin-top: 15px;
}

.example {
  margin: 10px 0;
  padding: 10px;
  background: white;
  border-radius: 5px;
}

.french {
  font-style: italic;
  color: #2c3e50;
  margin-bottom: 5px;
}

.chinese {
  color: #7f8c8d;
}

.exercise {
  background: #e8f5e8;
  padding: 20px;
  border-radius: 8px;
  margin-top: 30px;
}

.exercise-inputs {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin: 20px 0;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.input-group label {
  font-weight: bold;
  color: #27ae60;
}

.input-group input {
  padding: 10px;
  border: 2px solid #bdc3c7;
  border-radius: 5px;
  font-size: 16px;
}

.input-group input:focus {
  border-color: #3498db;
  outline: none;
}

.check-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

.check-btn:hover {
  background: #219a52;
}

.vocab-instruction,
.sentences-instruction {
  background: #fff3cd;
  padding: 15px;
  border-radius: 5px;
  border-left: 4px solid #ffc107;
  margin-bottom: 20px;
}

.vocab-category {
  margin-bottom: 30px;
}

.vocab-category h3 {
  color: #34495e;
  border-bottom: 2px solid #95a5a6;
  padding-bottom: 5px;
  margin-bottom: 15px;
}

.vocab-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.vocab-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.vocab-header {
  margin-bottom: 10px;
  font-size: 1.1em;
}

.checkboxes {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.checkboxes label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.sentences-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sentence-item {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #9b59b6;
}

.sentence-content {
  margin-bottom: 15px;
}

.sentence-checkboxes {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.sentence-checkboxes label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .french-lesson {
    padding: 10px;
  }
  
  .lesson-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .lesson-nav {
    flex-direction: column;
  }
  
  .vocab-grid {
    grid-template-columns: 1fr;
  }
  
  .checkboxes,
  .sentence-checkboxes {
    flex-direction: column;
    gap: 10px;
  }
}
</style>