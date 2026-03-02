<script setup>
import { computed, reactive, ref, watch } from "vue"

const props = defineProps({
  lessonData: {
    type: Array,
    required: true,
    default: () => [],
  },
})

const mode = ref("study")
const openMap = reactive({})
const inputMap = reactive({})
const resultMap = reactive({})
const showAnswerMap = reactive({})

/* ================================
   统计总句数（新增）
================================ */
const totalLines = computed(() => {
  return props.lessonData.reduce((sum, dlg) => {
    return sum + (dlg.text?.length || 0)
  }, 0)
})

/* ================================
   单词级检查
================================ */
function normalizeForWordCheck(s) {
  return (s ?? "")
    .replace(/\u00A0/g, " ")
    .replace(/[’]/g, "'")
    .trim()
    .replace(/\s+/g, " ")
}

function tokenizeWords(s) {
  const t = normalizeForWordCheck(s)
    .replace(/([,.!?;:()])/g, " $1 ")
    .replace(/\s+/g, " ")
    .trim()
  return t ? t.split(" ") : []
}

function checkLineByWords(expected, typed) {
  const e = tokenizeWords(expected)
  const a = tokenizeWords(typed)

  const maxLen = Math.max(e.length, a.length, 1)
  let correct = 0
  const tokens = []

  for (let i = 0; i < maxLen; i++) {
    const et = e[i] ?? ""
    const at = a[i] ?? ""
    const ok = et !== "" && et === at
    if (ok) correct++
    tokens.push({ expected: et, actual: at, ok })
  }

  const score = Math.round((correct / maxLen) * 100)
  const okAll = e.length === a.length && score === 100
  return { okAll, score, tokens }
}

/* ================================
   控制逻辑
================================ */
function setMode(m) {
  mode.value = m
}

function checkAll() {
  props.lessonData.forEach((dlg, dIdx) => {
    dlg.text.forEach((line, lIdx) => {
      const key = `${dIdx}-${lIdx}`
      const typed = inputMap[key] ?? ""
      resultMap[key] = checkLineByWords(line.french_full, typed)
    })
  })
}

function checkOne(dIdx, lIdx) {
  const key = `${dIdx}-${lIdx}`
  const expected = props.lessonData[dIdx].text[lIdx].french_full
  const typed = inputMap[key] ?? ""
  resultMap[key] = checkLineByWords(expected, typed)
}

function resetAll() {
  Object.keys(inputMap).forEach((k) => delete inputMap[k])
  Object.keys(resultMap).forEach((k) => delete resultMap[k])
  Object.keys(showAnswerMap).forEach((k) => delete showAnswerMap[k])
}

watch(
  () => props.lessonData,
  () => {
    resetAll()
    Object.keys(openMap).forEach((k) => delete openMap[k])
    props.lessonData.forEach((_, idx) => (openMap[idx] = true))
    mode.value = "study"
  },
  { deep: true, immediate: true }
)
</script>

<template>
  <div class="rounded-2xl border bg-white shadow-sm overflow-hidden">

    <!-- Header -->
    <div class="border-b bg-white px-4 py-4">
      <h2 class="text-base font-semibold text-gray-900">
        课文背诵 / 默写
      </h2>

      <!-- ✅ 新增总句数显示 -->
      <div class="text-xs text-gray-500 mt-1">
        本课共 {{ totalLines }} 句
      </div>

      <div class="mt-3 flex gap-2">
        <button
          class="h-9 px-3 rounded-lg border text-sm font-semibold"
          :class="mode === 'study' ? 'bg-gray-900 text-white border-gray-900' : 'bg-white text-gray-800 border-gray-200'"
          @click="setMode('study')"
        >
          对照背诵
        </button>

        <button
          class="h-9 px-3 rounded-lg border text-sm font-semibold"
          :class="mode === 'dictation' ? 'bg-gray-900 text-white border-gray-900' : 'bg-white text-gray-800 border-gray-200'"
          @click="setMode('dictation')"
        >
          隐藏法语默写
        </button>

        <button
          class="h-9 px-3 rounded-lg border border-gray-200 bg-white text-sm font-semibold"
          @click="resetAll"
        >
          重置
        </button>

        <button
          v-if="mode === 'dictation'"
          class="h-9 px-4 rounded-lg bg-blue-600 text-white text-sm font-semibold"
          @click="checkAll"
        >
          检查全部
        </button>
      </div>
    </div>

    <!-- 主体 -->
    <div>
      <div
        v-for="(dlg, dIdx) in lessonData"
        :key="dIdx"
        class="border-t"
      >
        <div v-for="(line, lIdx) in dlg.text" :key="lIdx" class="px-4 py-4 border-b">

          <!-- ✅ 计算全局序号 -->
          <div class="flex gap-3 items-start">

            <!-- 序号 -->
            <div class="w-8 text-sm font-semibold text-gray-500">
              {{
                // 计算全局连续编号
                lessonData
                  .slice(0, dIdx)
                  .reduce((sum, d) => sum + (d.text?.length || 0), 0)
                + lIdx + 1
              }}
            </div>

            <div class="flex-1">

              <!-- 中文 -->
              <div class="text-sm text-gray-900 leading-6">
                {{ line.chinese }}
              </div>

              <!-- 对照模式 -->
              <div v-if="mode === 'study'" class="mt-2 text-sm text-gray-700">
                {{ line.french_full }}
              </div>

              <!-- 默写模式 -->
              <div v-else class="mt-3 space-y-2">

                <textarea
                  class="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm"
                  rows="2"
                  v-model="inputMap[`${dIdx}-${lIdx}`]"
                />

                <div class="flex gap-2">
                  <button
                    class="h-8 px-3 rounded-lg bg-blue-600 text-white text-xs"
                    @click="checkOne(dIdx, lIdx)"
                  >
                    检查
                  </button>

                  <button
                    class="h-8 px-3 rounded-lg border text-xs"
                    @click="showAnswerMap[`${dIdx}-${lIdx}`] = !showAnswerMap[`${dIdx}-${lIdx}`]"
                  >
                    查看答案
                  </button>
                </div>

                <div v-if="showAnswerMap[`${dIdx}-${lIdx}`]" class="text-xs text-gray-600">
                  答案：{{ line.french_full }}
                </div>

              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

  </div>
</template>