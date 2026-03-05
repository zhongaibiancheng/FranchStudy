<script setup>
import { computed, ref, watch } from "vue"
import ReciteDictation from "@/components/ReciteDictation.vue"

import book_01_lesson_11 from '@/data/book_01/lesson_text_11.json'
import book_01_lesson_10 from '@/data/book_01/lesson_text_10.json'
import book_01_lesson_09 from '@/data/book_01/lesson_text_09.json'
import book_01_lesson_08 from '@/data/book_01/lesson_text_08.json'
const booksData = ref([
  {
    bookId: "bfsy-french-1",
    bookName: "北外法语（示例）",
    volumes: [
      {
        volumeId: "v1",
        volumeName: "第 1 册",
        lessons: [
          {
            lessonId: "11",
            lessonName: "第 11 课：La première classes",
            content: book_01_lesson_11
          },
          {
            lessonId: "10",
            lessonName: "第 10 课：Au téléphone / Prendre un rendez-vous",
            content: book_01_lesson_10
          },
          {
            lessonId: "09",
            lessonName: "第 09 课",
            content: book_01_lesson_09
          },
          {
            lessonId: "08",
            lessonName: "第 08 课：Faire du rangement",
            content: book_01_lesson_08
          }
        ]
      }
    ]
  }
])

// 选择状态
const selectedBookId = ref(booksData.value[0]?.bookId ?? "")
const selectedVolumeId = ref(booksData.value[0]?.volumes?.[0]?.volumeId ?? "")
const selectedLessonId = ref(booksData.value[0]?.volumes?.[0]?.lessons?.[0]?.lessonId ?? "")

const currentBook = computed(() => booksData.value.find(b => b.bookId === selectedBookId.value))
const volumeOptions = computed(() => currentBook.value?.volumes ?? [])
const currentVolume = computed(() => volumeOptions.value.find(v => v.volumeId === selectedVolumeId.value))
const lessonOptions = computed(() => currentVolume.value?.lessons ?? [])
const currentLesson = computed(() => lessonOptions.value.find(l => l.lessonId === selectedLessonId.value))
const lessonContent = computed(() => currentLesson.value?.content ?? [])

// ✅ 段落选择：-1=全部
const selectedDialogueIndex = ref(-1)
const dialogueOptions = computed(() =>
  (lessonContent.value ?? []).map((d, idx) => ({
    idx,
    label: `${d?.title?.chinese ?? "段落"}（${d?.title?.french_full ?? ""}）`,
  }))
)
const filteredLessonContent = computed(() => {
  if (!lessonContent.value?.length) return []
  if (selectedDialogueIndex.value === -1) return lessonContent.value
  const one = lessonContent.value[selectedDialogueIndex.value]
  return one ? [one] : []
})

// ✅ 抽取模式：all / 1 / 5 / 10
const pickMode = ref("all") // "all" | "1" | "5" | "10"
const pickSeed = ref(0) // 用于触发重新抽取

function resample() {
  pickSeed.value++
}

function sampleWithoutReplacement(arr, k) {
  const a = arr.slice()
  // Fisher-Yates shuffle（只需前 k 个）
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
      ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a.slice(0, Math.min(k, a.length))
}

// ✅ 真正传给 ReciteDictation 的内容
const finalLessonData = computed(() => {
  // 触发重新计算（重新抽取）
  void pickSeed.value

  const base = filteredLessonContent.value
  if (!base.length) return []

  if (pickMode.value === "all") return base

  const k = Number(pickMode.value)
  // 把所有对话的句子打平，随机抽 k 句
  const pool = []
  base.forEach((dlg, dIdx) => {
    dlg.text.forEach((line, lIdx) => {
      pool.push({
        dIdx,
        lIdx,
        line,
        from: dlg?.title?.chinese || dlg?.title?.french_full || `段落${dIdx + 1}`,
      })
    })
  })

  const picked = sampleWithoutReplacement(pool, k)

  // 组装为一个“随机抽取”段落，方便默写
  return [
    {
      title: {
        chinese: `随机抽取 ${picked.length} 句`,
        french_full: `Random pick (${picked.length})`,
      },
      text: picked.map(p => ({
        french_full: p.line.french_full,
        chinese: p.line.chinese,
        _from: p.from, // 你要显示来源可用
      })),
    },
  ]
})

// 切换上级时，自动重置下级
watch(selectedBookId, () => {
  const v = currentBook.value?.volumes?.[0]
  selectedVolumeId.value = v?.volumeId ?? ""
  selectedLessonId.value = v?.lessons?.[0]?.lessonId ?? ""
})

watch(selectedVolumeId, () => {
  const l = currentVolume.value?.lessons?.[0]
  selectedLessonId.value = l?.lessonId ?? ""
})

// 切换课次：段落回到全部；抽取回到全部
watch(selectedLessonId, () => {
  selectedDialogueIndex.value = -1
  pickMode.value = "all"
  pickSeed.value = 0
})

import { useRoute, useRouter } from "vue-router";

const router = useRouter();
const route = useRoute();
function goBack() {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push("/");
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部选择栏 -->
    <div class="border-b bg-white">
      <div class="mx-auto max-w-6xl px-4 py-4 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div class="grid grid-cols-1 sm:grid-cols-5 gap-2 w-full lg:w-auto">
          <!-- 书 -->
          <div class="flex flex-col">
            <label class="text-xs text-gray-500 mb-1">选择书</label>
            <select v-model="selectedBookId"
              class="h-10 rounded-xl border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option v-for="b in booksData" :key="b.bookId" :value="b.bookId">
                {{ b.bookName }}
              </option>
            </select>
          </div>

          <!-- 册 -->
          <div class="flex flex-col">
            <label class="text-xs text-gray-500 mb-1">第几册</label>
            <select v-model="selectedVolumeId"
              class="h-10 rounded-xl border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option v-for="v in volumeOptions" :key="v.volumeId" :value="v.volumeId">
                {{ v.volumeName }}
              </option>
            </select>
          </div>

          <!-- 课 -->
          <div class="flex flex-col">
            <label class="text-xs text-gray-500 mb-1">第几课</label>
            <select v-model="selectedLessonId"
              class="h-10 rounded-xl border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option v-for="l in lessonOptions" :key="l.lessonId" :value="l.lessonId">
                {{ l.lessonName }}
              </option>
            </select>
          </div>

          <!-- 段落 -->
          <div class="flex flex-col">
            <label class="text-xs text-gray-500 mb-1">课文段落</label>
            <select v-model.number="selectedDialogueIndex"
              class="h-10 rounded-xl border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              :disabled="!lessonContent.length">
              <option :value="-1">全部段落</option>
              <option v-for="opt in dialogueOptions" :key="opt.idx" :value="opt.idx">
                {{ opt.label }}
              </option>
            </select>
          </div>

          <!-- 抽取 -->
          <div class="flex flex-col">
            <label class="text-xs text-gray-500 mb-1">抽取方式</label>
            <select v-model="pickMode"
              class="h-10 rounded-xl border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              :disabled="!filteredLessonContent.length" @change="pickSeed = 0">
              <option value="all">全部</option>
              <option value="1">随机抽 1 句</option>
              <option value="5">随机抽 5 句</option>
              <option value="10">随机抽 10 句</option>
            </select>
          </div>
          <div>
            <button type="button" @click="goBack"
              class="h-9 px-4 rounded-lg border border-gray-200 bg-white text-sm font-semibold hover:bg-gray-50">
              返回
            </button>
          </div>
        </div>

        <!-- 重新抽取按钮（仅随机模式显示） -->
        <div v-if="pickMode !== 'all' && filteredLessonContent.length" class="mx-auto max-w-6xl px-4 pb-4">
          <button class="h-9 px-4 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700"
            @click="resample">
            重新抽取
          </button>
          <span class="ml-2 text-xs text-gray-500">（抽取结果会覆盖当前练习内容）</span>
        </div>

      </div>
    </div>

    <!-- 主体 -->
    <div class="mx-auto max-w-6xl px-4 py-6 space-y-4">
      <div class="rounded-2xl border bg-white p-4">
        <div class="text-sm text-gray-900 font-semibold">当前选择</div>
        <div class="mt-1 text-xs text-gray-600 leading-5">
          <div>书：{{ currentBook?.bookName || "-" }}</div>
          <div>册：{{ currentVolume?.volumeName || "-" }}</div>
          <div>课：{{ currentLesson?.lessonName || "-" }}</div>
          <div>段落：{{selectedDialogueIndex === -1 ? "全部段落" : (dialogueOptions.find(d => d.idx ===
            selectedDialogueIndex)?.label || "-") }}</div>
          <div>抽取：{{ pickMode === "all" ? "全部" : `随机抽 ${pickMode} 句` }}</div>
        </div>
      </div>

      <ReciteDictation v-if="finalLessonData.length" :lessonData="finalLessonData" />

      <div v-else class="rounded-2xl border bg-white p-6 text-sm text-gray-600">
        当前课次没有内容，请先在 booksData 里补充该课文 JSON。
      </div>
    </div>
  </div>
</template>