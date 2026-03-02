<script setup>
import { computed, ref, watch } from "vue"
import ReciteDictation from "@/components/ReciteDictation.vue"

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
            lessonId: "10",
            lessonName: "第 10 课：Au téléphone / Prendre un rendez-vous",
            content: [
              {
                title: { french_full: "Dialogue 1 Au téléphone", chinese: "对话一 打电话" },
                text: [
                  { french_full: "(Le téléphone sonne chez les Dupont. Madame Dupont décroche.)", chinese: "（杜邦家电话响了。杜邦夫人接电话。）" },
                  { french_full: "Allô, bonjour.", chinese: "喂，您好。" },
                  { french_full: "Bonjour, madame. Ici, c’est André Duval.", chinese: "您好，夫人。我是安德烈·杜瓦尔。" },
                  { french_full: "Pardon, c’est de la part de qui ?", chinese: "请问您是哪位？" },
                  { french_full: "André Duval à l’appareil.", chinese: "我是安德烈·杜瓦尔。" },
                  { french_full: "Pardon ?", chinese: "您说什么？" },
                  { french_full: "André, André Duval.", chinese: "安德烈，安德烈·杜瓦尔。" },
                  { french_full: "Je suis vraiment désolée, monsieur. Vous pouvez épeler, s’il vous plaît ?", chinese: "真的很抱歉，先生。您可以拼一下吗？" },
                  { french_full: "D-U-V-A-L, de la compagnie Air France.", chinese: "D-U-V-A-L，来自法航公司。" },
                  { french_full: "Ah oui, de Roissy.", chinese: "啊，是的，来自鲁瓦西。" },
                  { french_full: "C’est ça. Je voudrais parler à votre fils, Thomas. Il est là ?", chinese: "是的。我想和您的儿子托马说话。他在吗？" },
                  { french_full: "Oui, oui, il lit des journaux dans sa chambre. Attendez, je vous passe Thomas.", chinese: "在，在，他正在房间里看报纸。请稍等，我让托马接电话。" },
                  { french_full: "Merci, madame.", chinese: "谢谢您，夫人。" }
                ]
              },
              {
                title: { french_full: "Dialogue 2 Prendre un rendez-vous", chinese: "对话二 约会（约时间）" },
                text: [
                  { french_full: "Allô, oui ?", chinese: "喂，是我。" },
                  { french_full: "Salut, Thomas. Tu es là ?", chinese: "嗨，托马。你在吗？" },
                  { french_full: "Je lis et je révise mes leçons. Il y a un examen la semaine prochaine.", chinese: "我在读书和复习功课。下周有考试。" },
                  { french_full: "Cet examen est vraiment important ?", chinese: "这个考试真的很重要吗？" },
                  { french_full: "Bien sûr. Pourquoi ?", chinese: "当然。为什么？" },
                  { french_full: "Ce soir, il y a des amis à la maison. Tu viens ?", chinese: "今晚家里有朋友来。你来吗？" },
                  { french_full: "C’est à quelle heure ?", chinese: "几点？" },
                  { french_full: "Vers neuf heures.", chinese: "大约九点。" },
                  { french_full: "O.K. D’accord, je viens.", chinese: "好的，我来。" },
                  { french_full: "Alors, c’est entendu ?", chinese: "那就这么说定了？" },
                  { french_full: "Entendu !", chinese: "说定了！" },
                  { french_full: "Et sais-tu où est Vincent ? C’est pour la cuisine.", chinese: "你知道文森特在哪儿吗？是为了厨房的事情。" },
                  { french_full: "Le samedi, il va toujours à la bibliothèque. Il a son portable.", chinese: "星期六他总是去图书馆。他带着手机。" },
                  { french_full: "Mais je n’ai pas son numéro.", chinese: "但是我没有他的电话号码。" },
                  { french_full: "C’est le 06 45 66 32 00.", chinese: "是 06 45 66 32 00。" },
                  { french_full: "Merci, c’est gentil.", chinese: "谢谢，你真好。" },
                  { french_full: "De rien.", chinese: "不客气。" },
                  { french_full: "Alors, rendez-vous ce soir et bonne journée !", chinese: "那今晚见，祝你今天愉快！" },
                  { french_full: "Toi aussi ! À ce soir !", chinese: "你也是！今晚见！" }
                ]
              }
            ]
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
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部选择栏 -->
    <div class="border-b bg-white">
      <div class="mx-auto max-w-6xl px-4 py-4 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 class="text-lg font-semibold text-gray-900">法语课文背诵与默写</h1>
          <p class="text-xs text-gray-500 mt-1">选择书/册/课/段落，并选择抽取方式开始练习</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-5 gap-2 w-full lg:w-auto">
          <!-- 书 -->
          <div class="flex flex-col">
            <label class="text-xs text-gray-500 mb-1">选择书</label>
            <select
              v-model="selectedBookId"
              class="h-10 rounded-xl border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option v-for="b in booksData" :key="b.bookId" :value="b.bookId">
                {{ b.bookName }}
              </option>
            </select>
          </div>

          <!-- 册 -->
          <div class="flex flex-col">
            <label class="text-xs text-gray-500 mb-1">第几册</label>
            <select
              v-model="selectedVolumeId"
              class="h-10 rounded-xl border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option v-for="v in volumeOptions" :key="v.volumeId" :value="v.volumeId">
                {{ v.volumeName }}
              </option>
            </select>
          </div>

          <!-- 课 -->
          <div class="flex flex-col">
            <label class="text-xs text-gray-500 mb-1">第几课</label>
            <select
              v-model="selectedLessonId"
              class="h-10 rounded-xl border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option v-for="l in lessonOptions" :key="l.lessonId" :value="l.lessonId">
                {{ l.lessonName }}
              </option>
            </select>
          </div>

          <!-- 段落 -->
          <div class="flex flex-col">
            <label class="text-xs text-gray-500 mb-1">课文段落</label>
            <select
              v-model.number="selectedDialogueIndex"
              class="h-10 rounded-xl border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              :disabled="!lessonContent.length"
            >
              <option :value="-1">全部段落</option>
              <option v-for="opt in dialogueOptions" :key="opt.idx" :value="opt.idx">
                {{ opt.label }}
              </option>
            </select>
          </div>

          <!-- 抽取 -->
          <div class="flex flex-col">
            <label class="text-xs text-gray-500 mb-1">抽取方式</label>
            <select
              v-model="pickMode"
              class="h-10 rounded-xl border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              :disabled="!filteredLessonContent.length"
              @change="pickSeed = 0"
            >
              <option value="all">全部</option>
              <option value="1">随机抽 1 句</option>
              <option value="5">随机抽 5 句</option>
              <option value="10">随机抽 10 句</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 重新抽取按钮（仅随机模式显示） -->
      <div v-if="pickMode !== 'all' && filteredLessonContent.length" class="mx-auto max-w-6xl px-4 pb-4">
        <button
          class="h-9 px-4 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700"
          @click="resample"
        >
          重新抽取
        </button>
        <span class="ml-2 text-xs text-gray-500">（抽取结果会覆盖当前练习内容）</span>
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
          <div>段落：{{ selectedDialogueIndex === -1 ? "全部段落" : (dialogueOptions.find(d => d.idx === selectedDialogueIndex)?.label || "-") }}</div>
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