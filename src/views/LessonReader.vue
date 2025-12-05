<template>
  <div class="lesson-reader">
    <!-- ✅ 工具栏 -->
    <div class="toolbar">
      <div class="title">
        <h2>{{ lessonData.title }}</h2>
        <span class="count">
          当前显示 {{ filteredSentences.length }} / 共 {{ lessonData.text.length }} 句
        </span>
      </div>

      <div class="actions">
        <!-- ✅ 全局中文开关 -->
        <button class="action-btn" @click="toggleChinese">
          {{ showChinese ? '隐藏中文' : '显示中文' }}
        </button>

        <!-- ✅ 全局挖空模式 -->
        <button
          class="action-btn"
          :class="{ active: globalGapMode }"
          @click="toggleGlobalGap"
        >
          {{ globalGapMode ? '关闭全局挖空' : '开启全局挖空' }}
        </button>

        <!-- ✅ 来源快速筛选 -->
        <div class="segmented">
          <button
            class="seg-btn"
            :class="{ active: filterSource === 'all' }"
            @click="filterSource = 'all'"
          >
            全部
          </button>
          <button
            class="seg-btn"
            :class="{ active: filterSource === 'dialogue' }"
            @click="filterSource = 'dialogue'"
          >
            Dialogue
          </button>
          <button
            class="seg-btn"
            :class="{ active: filterSource === 'texte' }"
            @click="filterSource = 'texte'"
          >
            Texte
          </button>
        </div>

        <!-- ✅ 一键重置 -->
        <button class="action-btn ghost" @click="resetAll">
          重置视图
        </button>
      </div>
    </div>

    <!-- ✅ 卡片区 -->
    <div class="cards">
      <SentenceCard
        v-for="item in filteredSentences"
        :key="item.id"
        :item="item"
        :showChinese="showChinese"
        :forceGap="globalGapMode"
      />
    </div>

    <div v-if="!filteredSentences.length" class="empty">
      当前筛选条件下没有句子
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import SentenceCard from '@/components/SentenceCard.vue'
import getLessonDataByLesson from '@/services/lessonService'

const route = useRoute()


const lessonNo = computed(() => Number(route.query.lesson || 1))

const lessonData = computed(() => {
  return getLessonDataByLesson(lessonNo.value)
})

const showChinese = ref(true)
const globalGapMode = ref(false)
const filterSource = ref('all') // all | dialogue | texte

const filteredSentences = computed(() => {
  const list = lessonData.value?.text || []
  if (filterSource.value === 'all') return list
  return list.filter(x => x.source === filterSource.value)
})

const toggleChinese = () => {
  showChinese.value = !showChinese.value
}

const toggleGlobalGap = () => {
  globalGapMode.value = !globalGapMode.value
}

const resetAll = () => {
  showChinese.value = true
  globalGapMode.value = false
  filterSource.value = 'all'
}
</script>

<style scoped>
.lesson-reader{
  max-width: 980px;
  margin: 0 auto;
  padding: 18px;
}

.toolbar{
  background: #fff;
  border: 1px solid #eee;
  border-radius: 14px;
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  flex-wrap: wrap;
  box-shadow: 0 2px 10px rgba(0,0,0,.04);
}

.title{
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}
.title h2{
  margin: 0;
  font-size: 20px;
  color: #222;
}
.count{
  font-size: 12px;
  color: #888;
}

.actions{
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.action-btn{
  border: 1px solid #dcdcdc;
  background: #f8f8f8;
  padding: 8px 12px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 13px;
  transition: .2s;
}
.action-btn:hover{
  background: #f0f0f0;
}
.action-btn.active{
  background: #eaf2ff;
  border-color: #bcd2ff;
  color: #114a9b;
}
.action-btn.ghost{
  background: #fff;
}

.segmented{
  display: inline-flex;
  border: 1px solid #ddd;
  border-radius: 10px;
  overflow: hidden;
}
.seg-btn{
  border: none;
  background: #fff;
  padding: 8px 10px;
  font-size: 12px;
  cursor: pointer;
}
.seg-btn + .seg-btn{
  border-left: 1px solid #eee;
}
.seg-btn.active{
  background: #f3f6ff;
  color: #1b4d8f;
  font-weight: 600;
}

.cards{
  display: grid;
  gap: 12px;
}

.empty{
  margin-top: 14px;
  padding: 14px;
  text-align: center;
  border: 1px dashed #ddd;
  border-radius: 10px;
  background: #fafafa;
  color: #777;
}
</style>
