<template>
  <div class="lesson-reader">
    <!-- ✅ 工具栏 -->
    <div class="toolbar">
      <div class="title">
        <h2>{{ lessonData.title }}</h2>
        <select v-model="part" class="select">
          <option disabled value="">请选择...</option>
          <option v-for="opt in options" :key="opt.value" :value="opt.id">
            {{ opt.label }}
          </option>
        </select>
        <span class="count">
          当前显示 {{ filteredSentences.length }} / 共 {{ lessonData.text.length }} 句
          · 已选 {{ selectedCountInFiltered }} 句
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

        <!-- ✅ 选择快捷操作（仅作用于当前筛选列表） -->
        <div class="segmented">
          <button class="seg-btn" @click="selectAllFiltered">
            全选当前
          </button>
          <button class="seg-btn" @click="selectNoneFiltered">
            全不选当前
          </button>
          <button class="seg-btn" @click="invertFiltered">
            反选当前
          </button>
        </div>

        <!-- ✅ 打印乱序开关 -->
        <label class="print-toggle">
          <input type="checkbox" v-model="printShuffle" />
          <span>打印乱序</span>
        </label>

        <!-- ✅ 打印填空练习 -->
        <button class="action-btn print" @click="printGapExercise">
          🖨️ 打印填空练习
        </button>

        <!-- ✅ 一键重置 -->
        <button class="action-btn ghost" @click="resetAll">
          重置视图
        </button>

        <button @click="goBack" class="action-btn">
          ⬅️ 返回
        </button>
      </div>
    </div>

    <!-- ✅ 卡片区（带选择框） -->
    <div class="cards">
      <div
        v-for="item in filteredSentences"
        :key="item.id"
        class="sentence-row"
        :class="{ checked: isSelected(item.id) }"
      >
        <label class="sentence-check" @click.stop>
          <input
            type="checkbox"
            :checked="isSelected(item.id)"
            @change="toggleSelect(item.id)"
          />
        </label>

        <div class="sentence-card-wrap">
          <SentenceCard
            :item="item"
            :showChinese="showChinese"
            :forceGap="globalGapMode"
            :playing="playingId === item.id"
            :onPlay="handlePlaySentence"
          />
        </div>
      </div>
    </div>

    <!-- ✅ 空提示 -->
    <div v-if="!filteredSentences.length" class="empty">
      当前筛选条件下没有句子
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SentenceCard from '@/components/SentenceCard.vue'
import getLessonDataByLesson from '@/services/lessonService'
import { useSegmentAudio } from '@/composables/useSegmentAudio'

const route = useRoute()
const router = useRouter()

const lessonNo = computed(() => Number(route.query.lesson || 1))

const lessonData = computed(() => {
  return getLessonDataByLesson(lessonNo.value,part.value)
})

const goBack = () => {
  router.push('/')
}
const options= [
  {
  id:1,
  value:'对话',
  label:'对话'
},
  {
  id:2,
  value:'文章1',
  label:'文章1'
}
]

const part = ref(1)

const showChinese = ref(true)
const globalGapMode = ref(false)
const filterSource = ref('all') // all | dialogue | texte

// ✅ 新增：打印顺序控制
const printShuffle = ref(false)

// ✅ 新增：选择状态（Set 更适合）
const selectedIds = ref(new Set())

// ✅ 整课音频 src getter
const getLessonSrc = () => lessonData.value?.audio?.src

// ✅ 片段播放控制
const { playingId, playSegment } = useSegmentAudio(getLessonSrc)

const filteredSentences = computed(() => {
  const list = lessonData.value?.text || []
  if (filterSource.value === 'all') return list
  return list.filter(x => x.source === filterSource.value)
})

/**
 * ✅ 默认全选：当课次变化/数据变化时，重新把整课句子加入选中
 *   如果你希望“默认不选”，把这里改成：selectedIds.value = new Set()
 */
watch(
  () => lessonData.value?.text,
  (text) => {
    if (!text) return
    selectedIds.value = new Set(text.map(x => x.id))
  },
  { immediate: true }
)

// ✅ 选择相关工具函数
const isSelected = (id) => selectedIds.value.has(id)

const toggleSelect = (id) => {
  const s = new Set(selectedIds.value)
  if (s.has(id)) s.delete(id)
  else s.add(id)
  selectedIds.value = s
}

// ✅ 仅对“当前筛选列表”做全选/全不选/反选
const selectAllFiltered = () => {
  const s = new Set(selectedIds.value)
  for (const it of filteredSentences.value) s.add(it.id)
  selectedIds.value = s
}

const selectNoneFiltered = () => {
  const s = new Set(selectedIds.value)
  for (const it of filteredSentences.value) s.delete(it.id)
  selectedIds.value = s
}

const invertFiltered = () => {
  const s = new Set(selectedIds.value)
  for (const it of filteredSentences.value) {
    if (s.has(it.id)) s.delete(it.id)
    else s.add(it.id)
  }
  selectedIds.value = s
}

const selectedCountInFiltered = computed(() => {
  const list = filteredSentences.value || []
  let c = 0
  for (const it of list) {
    if (selectedIds.value.has(it.id)) c++
  }
  return c
})

const toggleChinese = () => {
  showChinese.value = !showChinese.value
}

const toggleGlobalGap = () => {
  globalGapMode.value = !globalGapMode.value
}

// ✅ 给卡片用的播放方法
const handlePlaySentence = (item) => {
  playSegment(item, lessonData.value?.audio?.src)
}

const resetAll = () => {
  showChinese.value = true
  globalGapMode.value = false
  filterSource.value = 'all'
  printShuffle.value = false

  // ✅ 重置选择：恢复整课全选
  const text = lessonData.value?.text || []
  selectedIds.value = new Set(text.map(x => x.id))
}

/** ✅ 小工具：数组乱序（不改原数组） */
const shuffleArray = (arr) => {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

/** ✅ 打印填空练习（只打印选中的句子） */
const printGapExercise = () => {
  const base = filteredSentences.value || []

  // ✅ 关键改动：只取“当前筛选范围内 + 被选中”
  const selectedBase = base.filter(x => selectedIds.value.has(x.id))

  if (!selectedBase.length) {
    alert('请先勾选要打印的句子。')
    return
  }

  const list = printShuffle.value ? shuffleArray(selectedBase) : selectedBase

  // 做一份只用于打印的“填空练习数据”
  const printable = list.map((x) => ({
    index: x.id, // 你原来就是用 id
    source: x.source,
    french_gap: x.french_gap || x.french_full || '',
    chinese: x.chinese || ''
  }))

  const title = lessonData.value?.title || `Leçon ${lessonNo.value}`
  const dateStr = new Date().toLocaleDateString()

  const html = buildGapPrintHtml({
    title,
    dateStr,
    filterSource: filterSource.value,
    isShuffled: printShuffle.value,
    items: printable
  })

  // ✅ 新窗口打印（更干净、不污染当前页面）
  const w = window.open('', '_blank')
  if (!w) {
    alert('浏览器拦截了弹窗。请允许弹窗后重试打印。')
    return
  }

  w.document.open()
  w.document.write(html)
  w.document.close()
}

/** ✅ 生成打印 HTML（A4，含序号、中文提示） */
const buildGapPrintHtml = ({ title, dateStr, filterSource, isShuffled, items }) => {
  const sourceLabel =
    filterSource === 'all' ? '全部' :
    filterSource === 'dialogue' ? 'Dialogue' : 'Texte'

  const headerNote = `
    <div class="meta">
      <span>来源：${sourceLabel}</span>
      <span>顺序：${isShuffled ? '乱序' : '按课文顺序'}</span>
      <span>日期：${dateStr}</span>
      <span>数量：${items.length} 句</span>
    </div>
  `

  const body = items.map(it => `
    <div class="item">
      <div class="idx">${it.index}</div>
      <div class="content">
        <div class="fr">${escapeHtml(it.french_gap)}</div>
        <div class="zh">${escapeHtml(it.chinese)}</div>
      </div>
    </div>
  `).join('')

  return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>${escapeHtml(title)} - 填空练习</title>
  <style>
    @page {
      size: A4;
      margin: 14mm 12mm 16mm 12mm;
    }

    body {
      font-family: "Microsoft YaHei", Arial, sans-serif;
      color: #111;
      font-size: 12.5px;
      line-height: 1.45;
    }

    h1 {
      font-size: 18px;
      margin: 0 0 6px 0;
      text-align: center;
      letter-spacing: .5px;
    }

    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      justify-content: center;
      font-size: 11px;
      color: #666;
      margin-bottom: 10px;
    }

    .hint {
      text-align: center;
      font-size: 11px;
      color: #666;
      margin-bottom: 12px;
    }

    .list {
      display: grid;
      gap: 10px;
    }

    .item {
      display: flex;
      gap: 10px;
      border: 1px solid #e6e6e6;
      border-radius: 10px;
      padding: 10px 12px;
      page-break-inside: avoid;
    }

    .idx {
      width: 26px;
      height: 26px;
      border-radius: 999px;
      border: 1px solid #ddd;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 12px;
      color: #333;
      flex-shrink: 0;
      margin-top: 2px;
    }

    .content {
      flex: 1;
      min-width: 0;
    }

    .fr {
      font-size: 13.5px;
      font-weight: 500;
      margin-bottom: 4px;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .zh {
      font-size: 12px;
      color: #666;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .page-number {
      position: fixed;
      bottom: 6mm;
      right: 10mm;
      font-size: 10px;
      color: #888;
    }
  </style>
</head>
<body>
  <h1>${escapeHtml(title)} · 填空练习</h1>
  ${headerNote}
  <div class="hint">
    说明：请根据中文提示填写法语空格。建议先不翻课本，再对照原文检查。
  </div>

  <div class="list">
    ${body}
  </div>

  <div class="page-number">
    （如需页码可在浏览器打印设置中开启“页眉页脚”）
  </div>

  <script>
    window.onload = function () {
      window.print();
    }
  <\/script>
</body>
</html>`
}

/** ✅ 打印 HTML 安全转义 */
const escapeHtml = (str) => {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
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

/* ✅ 打印按钮稍微突出一点 */
.action-btn.print{
  background: #111;
  color: #fff;
  border-color: #111;
}
.action-btn.print:hover{
  background: #222;
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

/* ✅ 打印乱序开关 */
.print-toggle{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  border: 1px dashed #ddd;
  border-radius: 10px;
  font-size: 12px;
  color: #444;
  background: #fafafa;
}
.print-toggle input{
  transform: translateY(1px);
  cursor: pointer;
}

/* ✅ 句子列表 */
.cards{
  display: grid;
  gap: 12px;
}

/* ✅ 新增：每行 = checkbox + card */
.sentence-row{
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 8px;
  align-items: start;
}

.sentence-check{
  display: grid;
  place-items: center;
  padding-top: 10px;
}

.sentence-check input{
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #111;
}

.sentence-row.checked .sentence-card-wrap{
  outline: 2px solid rgba(17,17,17,0.08);
  border-radius: 12px;
}

/* 让 SentenceCard 外部包一层，不影响它内部布局 */
.sentence-card-wrap{
  border-radius: 12px;
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
