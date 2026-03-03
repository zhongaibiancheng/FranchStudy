<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="border-b bg-white">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
        <div>
          <h1 class="text-lg font-semibold text-gray-900">法语听写</h1>
          <p class="text-xs text-gray-500 mt-0.5">
            选择册数与课次，随机抽词进行听写（支持逐题判分 / 整组判分）
          </p>
        </div>

        <div class="flex items-center gap-2">
          <button type="button" @click="goBack" class="h-9 px-4 rounded-lg border border-gray-200 bg-white text-sm font-semibold hover:bg-gray-50">
            返回
          </button>
          <button class="h-9 px-4 rounded-lg border border-gray-200 bg-white text-sm font-semibold hover:bg-gray-50"
            @click="resetAll">
            重置
          </button>
        </div>
      </div>
    </div>

    <!-- Body -->
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- ========================= -->
      <!-- Stage: setup              -->
      <!-- ========================= -->
      <div v-if="stage === 'setup'" class="bg-white border rounded-xl p-6">
        <h2 class="text-sm font-semibold text-gray-900">选择范围</h2>

        <!-- 来源选择：二选一 -->
        <div class="mt-4">
          <label class="text-sm font-semibold text-gray-700">抽词来源</label>
          <div class="mt-2 flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6 text-sm">
            <label class="inline-flex items-center gap-2">
              <input type="radio" value="lesson" v-model="setup.source" />
              <span class="font-semibold text-gray-800">从课文抽取</span>
              <span class="text-xs text-gray-500">（按册数 + 课次）</span>
            </label>
            <label class="inline-flex items-center gap-2">
              <input type="radio" value="wrongbook" v-model="setup.source" />
              <span class="font-semibold text-gray-800">从错题本抽取</span>
              <span class="text-xs text-gray-500">（只抽你做错过的词）</span>
            </label>
          </div>
        </div>

        <!-- 课文抽取：book/lesson 仅在 source=lesson 时可用 -->
        <div class="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <!-- 册数 -->
          <div>
            <label class="text-sm font-semibold text-gray-700">册数</label>
            <select v-model="setup.book"
              class="mt-2 w-full h-10 rounded-lg border border-gray-200 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:bg-gray-50 disabled:text-gray-400"
              :disabled="setup.source !== 'lesson'">
              <option value="">请选择册数</option>
              <option v-for="b in books" :key="b.value" :value="b.value">
                {{ b.label }}
              </option>
            </select>
          </div>

          <!-- 课次 -->
          <div>
            <label class="text-sm font-semibold text-gray-700">课次</label>
            <select v-model="setup.lesson"
              class="mt-2 w-full h-10 rounded-lg border border-gray-200 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:bg-gray-50 disabled:text-gray-400"
              :disabled="setup.source !== 'lesson' || !setup.book">
              <option value="">请选择课次</option>
              <option v-for="l in lessonOptions" :key="l.value" :value="l.value">
                {{ l.label }}
              </option>
            </select>
          </div>

          <!-- 抽取数量：两种来源都需要 -->
          <div>
            <label class="text-sm font-semibold text-gray-700">抽取数量</label>
            <div class="mt-2 relative">
              <input v-model.number="setup.count" type="number" min="1" max="50"
                class="w-full h-10 rounded-lg border border-gray-200 px-3 pr-16 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                placeholder="例如 10" />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">个</span>
            </div>

            <p v-if="setup.source === 'lesson'" class="text-xs text-gray-500 mt-1">从本课随机抽取</p>
            <p v-else class="text-xs text-gray-500 mt-1">从错题本随机抽取（不足时可考虑回退策略）</p>
          </div>
        </div>

        <!-- 模式选择（原样保留） -->
        <div class="mt-5">
          <label class="text-sm font-semibold text-gray-700">判分模式</label>
          <div class="mt-2 flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6 text-sm">
            <label class="inline-flex items-center gap-2">
              <input type="radio" value="immediate" v-model="setup.mode" />
              <span class="font-semibold text-gray-800">逐题判分</span>
              <span class="text-xs text-gray-500">（写完一个就核对一个）</span>
            </label>
            <label class="inline-flex items-center gap-2">
              <input type="radio" value="batch" v-model="setup.mode" />
              <span class="font-semibold text-gray-800">整组判分</span>
              <span class="text-xs text-gray-500">（全部写完再统一核对）</span>
            </label>
          </div>
        </div>

        <div class="mt-6 flex justify-end">
          <button
            class="h-10 px-6 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!canStart || loading" @click="startSession">
            {{ loading ? "抽取中..." : "开始听写" }}
          </button>
        </div>
      </div>

      <!-- ========================= -->
      <!-- Stage: doing              -->
      <!-- ========================= -->
      <div v-else-if="stage === 'doing'" class="space-y-4">
        <!-- 进度条 -->
        <div class="bg-white border rounded-xl p-4">
          <div class="flex items-center justify-between">
            来源：{{ setup.source === "lesson" ? "课文" : "错题本" }}｜
            <div class="text-sm font-semibold text-gray-900">
              进度：第 {{ currentIndex + 1 }} / {{ session.words.length }} 个
            </div>
            <div class="text-xs text-gray-500">
              册数：{{ setup.book }} ｜课次：{{ setup.lesson }} ｜模式：{{ setup.mode === "immediate" ? "逐题判分" : "整组判分" }}
            </div>
          </div>

          <div class="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
            <div class="h-2 bg-blue-600" :style="{ width: progressPercent + '%' }"></div>
          </div>
        </div>

        <!-- 听写卡片 -->
        <div class="bg-white border rounded-xl p-6">
          <div class="flex items-center justify-between">
            <h2 class="text-sm font-semibold text-gray-900">听写题</h2>

            <div class="flex items-center gap-2">
              <button class="h-9 px-4 rounded-lg border border-gray-200 bg-white text-sm font-semibold hover:bg-gray-50"
                @click="playCurrent">
                🔊 播放
              </button>

              <!-- 逐题判分：显示答案 -->
              <button v-if="setup.mode === 'immediate'"
                class="h-9 px-4 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition disabled:opacity-50"
                :disabled="reveal" @click="reveal = true">
                显示答案
              </button>

              <!-- 整组判分：下一题 -->
              <button v-if="setup.mode === 'batch'"
                class="h-9 px-4 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition"
                @click="nextBatchStep">
                {{ currentIndex < session.words.length - 1 ? "下一题" : "我写完了 → 去核对" }} </button>
            </div>
          </div>

          <!-- 提示文案 -->
          <p class="mt-3 text-sm text-gray-600">
            <template v-if="setup.mode === 'immediate'">
              请先听发音，在纸上写下：<span class="font-semibold">法语拼写 / 中文意思 / 词性</span>，然后点击“显示答案”核对并标记对错。
            </template>
            <template v-else>
              整组判分模式：请只听发音并在纸上依次写下对应答案。系统<strong>不会显示答案</strong>，直到你点击“我写完了 → 去核对”。
            </template>
          </p>

          <!-- 逐题判分：答案区 -->
          <div v-if="setup.mode === 'immediate'">
            <div v-if="reveal" class="mt-5 rounded-xl border border-gray-200 bg-gray-50 p-4">
              <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                <div>
                  <p class="text-xs text-gray-500">法语</p>
                  <p class="text-lg font-semibold text-gray-900">{{ currentWord.french }}</p>

                  <p class="text-xs text-gray-500 mt-3">中文</p>
                  <p class="text-sm text-gray-900">{{ currentWord.chinese || "—" }}</p>

                  <p class="text-xs text-gray-500 mt-3">词性</p>
                  <div class="text-sm text-gray-900">
                    <div>
                      <span class="font-semibold">{{ currentWord.part_of_speech || "—" }}</span>
                      <span class="text-gray-500">
                        （{{ currentWord.part_of_speech_full_chinese || "—" }}）
                      </span>
                    </div>

                    <!-- 语法标签：阴阳性/单复数/动词信息 -->
                    <div v-if="gramLabel" class="mt-1 text-xs text-gray-500">
                      {{ gramLabel }}
                    </div>

                    <!-- 你后端返回的中文展示串（例如：阴性｜复数｜命令式 vous 等） -->
                    <div v-if="currentWord.display_label_cn" class="mt-1 text-xs text-gray-500">
                      {{ currentWord.display_label_cn }}
                    </div>
                  </div>
                </div>

                <div class="text-xs text-gray-500 sm:text-right">
                  <p>提示：可再点击“播放”复听核对</p>
                </div>
              </div>

              <div class="mt-4 flex items-center justify-end gap-2">
                <button
                  class="h-9 px-4 rounded-lg border border-gray-200 bg-white text-sm font-semibold hover:bg-gray-50"
                  @click="markImmediate(currentWord.exercise_id,currentWord.word_id, 0)">
                  我写错了
                </button>
                <button class="h-9 px-4 rounded-lg bg-green-600 text-white text-sm font-semibold hover:bg-green-700"
                  @click="markImmediate(currentWord.exercise_id,currentWord.word_id, 1)">
                  我写对了
                </button>
              </div>
            </div>

            <div v-else class="mt-5 rounded-xl border border-dashed border-gray-200 p-4 text-sm text-gray-500">
              答案已隐藏。点击“播放”可重复听发音；准备好后点击“显示答案”。
            </div>
          </div>

          <!-- 整组判分：只显示当前编号提示（不显示答案） -->
          <div v-else class="mt-5 rounded-xl border border-dashed border-gray-200 p-4 text-sm text-gray-500">
            当前是第 <span class="font-semibold text-gray-900">{{ currentIndex + 1 }}</span> 个词。请在纸上按顺序记录。
            <div class="mt-2 text-xs text-gray-400">
              （你也可以在核对页看到所有答案并逐条判对/错）
            </div>
          </div>
        </div>
      </div>

      <!-- ========================= -->
      <!-- Stage: review (batch)     -->
      <!-- ========================= -->
      <div v-else-if="stage === 'review'" class="space-y-4">
        <div class="bg-white border rounded-xl p-4">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm font-semibold text-gray-900">整组核对</div>
              <div class="text-xs text-gray-500 mt-0.5">
                已标注 {{ reviewedCount }} / {{ session.words.length }} 个
              </div>
            </div>
            <button class="h-9 px-4 rounded-lg border border-gray-200 bg-white text-sm font-semibold hover:bg-gray-50"
              @click="stage = 'doing'">
              返回继续听写
            </button>
          </div>
        </div>

        <div class="bg-white border rounded-xl overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full text-sm">
              <thead class="bg-gray-50 text-gray-600">
                <tr>
                  <th class="text-left font-semibold px-4 py-3 whitespace-nowrap">No</th>
                  <th class="text-left font-semibold px-4 py-3 whitespace-nowrap">法语</th>
                  <th class="text-left font-semibold px-4 py-3 whitespace-nowrap">中文</th>
                  <th class="text-left font-semibold px-4 py-3 whitespace-nowrap">词性</th>
                  <th class="text-right font-semibold px-4 py-3 whitespace-nowrap">操作</th>
                </tr>
              </thead>

              <tbody class="divide-y divide-gray-100">
                <tr v-for="(w, idx) in session.words" :key="w.exercise_id" class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-gray-500 whitespace-nowrap">{{ idx + 1 }}</td>

                  <td class="px-4 py-3 whitespace-nowrap">
                    <div class="flex items-center gap-2">
                      <span class="font-semibold text-gray-900">{{ w.french }}</span>
                      <button class="text-blue-600 hover:text-blue-800 text-xs font-semibold" @click="speak(w.french)">
                        🔊
                      </button>
                    </div>
                  </td>

                  <td class="px-4 py-3 whitespace-nowrap text-gray-700">
                    {{ w.chinese || "—" }}
                  </td>

                  <td class="px-4 py-3 whitespace-nowrap text-gray-700">
                    <!-- {{ w.part_of_speech || "—" }}
                    <span class="text-gray-400">（{{ w.part_of_speech_full_chinese || "—" }}）</span> -->
                    <span class="text-gray-400">{{ formatPos(w) }}</span>

                  </td>

                  <td class="px-4 py-3 whitespace-nowrap text-right">
                    <div class="inline-flex items-center gap-2">
                      <button class="h-8 px-3 rounded-lg border text-sm font-semibold" :class="batchResult(w.word_id) === 'wrong'
                        ? 'border-red-200 bg-red-100 text-red-700'
                        : 'border-gray-200 bg-green-100 text-gray-700 hover:bg-gray-50'"
                        @click="markBatch(w.exercise_id,w.word_id, 0)">
                        错
                      </button>
                      <button class="h-8 px-3 rounded-lg border text-sm font-semibold" :class="batchResult(w.word_id) === 'correct'
                        ? 'border-green-200 bg-green-50 text-green-700'
                        : 'border-gray-200 bg-white text-gray-700 hover:bg-gray-50'"
                        @click="markBatch(w.exercise_id,w.word_id, 1)">
                        对
                      </button>
                    </div>
                  </td>
                </tr>

                <tr v-if="session.words.length === 0">
                  <td colspan="5" class="px-4 py-10 text-center text-gray-500">
                    无数据
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="flex justify-end gap-2">
          <button class="h-10 px-4 rounded-lg border border-gray-200 bg-white text-sm font-semibold hover:bg-gray-50"
            @click="resetAll">
            返回选择
          </button>

          <button
            class="h-10 px-4 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 disabled:opacity-50"
            :disabled="reviewedCount !== session.words.length" @click="finishBatchReview">
            完成本组
          </button>
        </div>

        <p class="text-xs text-gray-500">
          提示：需要把每一条都标记“对/错”后才能完成本组。
        </p>
      </div>

      <!-- ========================= -->
      <!-- Stage: done               -->
      <!-- ========================= -->
      <div v-else class="bg-white border rounded-xl p-6">
        <h2 class="text-sm font-semibold text-gray-900">本组完成</h2>

        <div class="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="rounded-xl border bg-gray-50 p-4">
            <p class="text-xs text-gray-500">总数</p>
            <p class="text-xl font-semibold text-gray-900">{{ session.words.length }}</p>
          </div>
          <div class="rounded-xl border bg-green-50 border-green-100 p-4">
            <p class="text-xs text-green-700">写对</p>
            <p class="text-xl font-semibold text-green-800">{{ correctCount }}</p>
          </div>
          <div class="rounded-xl border bg-red-50 border-red-100 p-4">
            <p class="text-xs text-red-700">写错</p>
            <p class="text-xl font-semibold text-red-800">{{ wrongCount }}</p>
          </div>
        </div>

        <div class="mt-5">
          <p class="text-sm font-semibold text-gray-900">错词列表</p>

          <div v-if="wrongWords.length === 0" class="mt-2 text-sm text-gray-500">
            没有错词，太强了。
          </div>

          <ul v-else class="mt-2 divide-y divide-gray-100 border rounded-xl overflow-hidden">
            <li v-for="w in wrongWords" :key="w.id" class="px-4 py-3 bg-white">
              <div class="flex items-center justify-between gap-3">
                <div class="min-w-0">
                  <p class="text-sm font-semibold text-gray-900 truncate">{{ w.french }}</p>
                  <p class="text-xs text-gray-500 truncate">
                    {{ w.part_of_speech || "—" }}（{{ w.part_of_speech_full_chinese || "—" }}） · {{ w.chinese || "—" }}
                  </p>
                </div>
                <button class="text-blue-600 hover:text-blue-800 text-sm font-semibold" @click="speak(w.french)">
                  🔊 再听
                </button>
              </div>
            </li>
          </ul>
        </div>

        <div class="mt-6 flex justify-end gap-2">
          <button class="h-10 px-4 rounded-lg border border-gray-200 bg-white text-sm font-semibold hover:bg-gray-50"
            @click="resetAll">
            返回选择
          </button>

          <button class="h-10 px-4 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700"
            @click="restartSameSetup">
            再来一组
          </button>

          <button
            class="h-10 px-4 rounded-lg bg-gray-900 text-white text-sm font-semibold hover:bg-black disabled:opacity-50"
            :disabled="wrongWords.length === 0" @click="restartWrongOnly">
            只复习错词
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import api from '../utils/api'
import { useRoute, useRouter } from "vue-router";

const router = useRouter();
const route = useRoute();
/**
 * 你的单词结构：
 * { id, french, chinese, part_of_speech, part_of_speech_full_chinese }
 */

/** --------- Setup options --------- */
const books = [
  { value: "1", label: "第 1 册" },
  { value: "2", label: "第 2 册" },
];

const lessonsByBook = {
  // "1": Array.from({ length: 12 }, (_, i) => ({ value: String(i + 1), label: `第 ${i + 1} 课` })),
  // "2": Array.from({ length: 12 }, (_, i) => ({ value: String(i + 1), label: `第 ${i + 1} 课` })),
  "1":
    Array.from({ length: 18 }, (_, i) => ({
  value: String(i + 1),
  label: `第 ${i + 1} 课`
})),
  "2":[
    { value: String(1), label: `第 ${1} 课` },
    { value: String(2), label: `第 ${2} 课` },
    { value: String(3), label: `第 ${3} 课` },
    { value: String(4), label: `第 ${4} 课` },
    { value: String(5), label: `第 ${5} 课` }
  ]
};

const setup = ref({
  source: "lesson", // lesson | wrongbook
  book: "",
  lesson: "",
  count: 10,
  mode: "immediate", // immediate | batch
});

function formatPos(w) {
  if (!w) return "—"

  const base = w.part_of_speech || "—"
  const baseCN = w.part_of_speech_full_chinese || ""

  const partsCN = []

  // ===== 名词 =====
  if (base.startsWith("n")) {
    if (w.gram_gender === "m") partsCN.push("阳性")
    if (w.gram_gender === "f") partsCN.push("阴性")
    if (w.gram_number === "pl") partsCN.push("复数")
  }

  // ===== 形容词 =====
  if (base.startsWith("a")) {
    if (w.gram_gender === "m") partsCN.push("阳性")
    if (w.gram_gender === "f") partsCN.push("阴性")
  }

  // ===== 动词 =====
  if (base.startsWith("v")) {
    if (w.gram_mood === "imp") partsCN.push("命令式")

    const personMap = {
      "1s": "je",
      "2s": "tu",
      "3s": "il/elle",
      "1p": "nous",
      "2p": "vous",
      "3p": "ils/elles"
    }

    if (w.gram_person && personMap[w.gram_person]) {
      partsCN.push(personMap[w.gram_person])
    }

    if (w.gram_tense === "pres") partsCN.push("现在时")
  }

  // ===== 拼接 =====
  const extra = partsCN.length > 0 ? `｜${partsCN.join("｜")}` : ""

  if (baseCN) {
    return `${base}（${baseCN}${extra}）`
  }

  return `${base}${extra ? `（${partsCN.join("｜")}）` : ""}`
}

const lessonOptions = computed(() => (setup.value.book ? lessonsByBook[setup.value.book] : []));

watch(
  () => setup.value.source,
  (src) => {
    if (src === "lesson") {
      // 选择课文抽词：错题本不需要额外字段（这里只是保证 UI 状态）
      // 不动
    } else {
      // 选择错题本：清空 book/lesson，避免误用
      setup.value.book = "";
      setup.value.lesson = "";
    }
  },
  { immediate: true }
);

/** --------- Stage --------- */
const stage = ref("setup"); // setup | doing | review | done
const loading = ref(false);

/** --------- Session --------- */
const session = ref({
  id: "",
  words: /** @type {Array<{id:number,french:string,chinese?:string,part_of_speech?:string,part_of_speech_full_chinese?:string}>} */ ([]),
  results: /** @type {Record<number, 'correct'|'wrong'>} */ ({}),
});

const currentIndex = ref(0);
const reveal = ref(false);

const currentWord = computed(() => session.value.words[currentIndex.value] || {});

const canStart = computed(() => {
  const n = Number(setup.value.count);
  if (!n || n <= 0) return false;

  if (setup.value.source === "lesson") {
    return !!(setup.value.book && setup.value.lesson);
  }
  if (setup.value.source === "wrongbook") {
    return true; // 只要有 count 就能抽
  }
  return false;
});
const progressPercent = computed(() => {
  if (!session.value.words.length) return 0;
  return Math.round(((currentIndex.value + 1) / session.value.words.length) * 100);
});
const gramLabel = computed(() => {
  const w = currentWord.value || currentWord; // 兼容 ref / 普通对象
  if (!w) return "";

  const parts = [];

  // 性
  if (w.gram_gender === "m") parts.push("阳性");
  else if (w.gram_gender === "f") parts.push("阴性");

  // 数
  if (w.gram_number === "sg") parts.push("单数");
  else if (w.gram_number === "pl") parts.push("复数");

  // 语气
  if (w.gram_mood === "imp") parts.push("命令式");

  // 人称（你后端用 1s/2s/3s/1p/2p/3p）
  const personMap = {
    "1s": "je",
    "2s": "tu",
    "3s": "il/elle",
    "1p": "nous",
    "2p": "vous",
    "3p": "ils/elles",
  };
  if (w.gram_person && personMap[w.gram_person]) {
    parts.push(personMap[w.gram_person]);
  }

  // 时态（如果你以后填）
  const tenseMap = {
    pres: "现在时",
    past: "过去时",
    fut: "将来时",
  };
  if (w.gram_tense && tenseMap[w.gram_tense]) {
    parts.push(tenseMap[w.gram_tense]);
  }

  return parts.join("｜");
});
/***
 * 根据 book/lesson 从后端获取单词列表
 * 
 */
async function fetchWords(book, lesson, count){
   try {
        const response = await api.post('/spellingbee/exercise', {
            "book":book,
            "lesson":lesson,
            "mode":setup.value.source,
            "count": count
        })
        
        if (response.data && response.data.words) {
          return response.data.words
        } else {
          console.log('响应中缺少用户数据')
          errors.value.general = '获取单词列表失败'
        }
      } catch (error) {
        console.error('获取单词列表失败:', error)
        // 处理后端返回的错误信息
        if (error.response && error.response.data && error.response.data.error) {
        } else {
          errors.value.general = '获取单词列表失败，请稍后重试'
        }
      } finally {
        // loading.value = false
      }
};

async function apiStartSessionFromWrongbook({ book, lesson, count }) {
  const wrongPool = await fetchWords(book, lesson, count)
  const shuffled = [...wrongPool].sort(() => Math.random() - 0.5);
  return {
    session_id: `sess_wrong_${Date.now()}`,
    items: shuffled.slice(0, Math.min(count, shuffled.length)),
  };
}

/** --------- Mock API（后续替换成 Flask 接口） --------- */
async function apiStartSession({ book, lesson, count }) {
  const pool = await fetchWords(book, lesson, count);

  // 真实项目：按 book/lesson 过滤 pool
  const shuffled = [...pool].sort(() => Math.random() - 0.5);
  return {
    session_id: `sess_${Date.now()}`,
    items: shuffled.slice(0, Math.min(count, shuffled.length)),
  };
}

async function startSession() {
  if (!canStart.value) return;
  loading.value = true;

  try {
    let resp;

    if (setup.value.source === "lesson") {
      resp = await apiStartSession({
        book: setup.value.book,
        lesson: setup.value.lesson,
        count: Number(setup.value.count),
      });
    } else {
      resp = await apiStartSessionFromWrongbook({
        book: setup.value.book,
        lesson: setup.value.lesson,
        count: Number(setup.value.count),
      });
    }

    session.value.id = resp.session_id;
    session.value.words = resp.items;
    session.value.results = {};
    currentIndex.value = 0;
    reveal.value = false;
    stage.value = "doing";
    playCurrent();
  } finally {
    loading.value = false;
  }
}

function playCurrent() {
  const text = currentWord.value?.french;

  if (!text) return;
  speak(text);
}

/** ----- immediate mode mark ----- */
async function markImmediate(exercise_id, word_id, result) {
  try {
      const response = await api.put('/spellingbee/exercise/'+exercise_id, {
          "word_id":word_id,
          "result":result
      })

      const w = currentWord.value;
      if (!w?.word_id) return;
      session.value.results[w.word_id] = result == 0? "wrong" : "correct";

      if (currentIndex.value < session.value.words.length - 1) {
        currentIndex.value += 1;
        reveal.value = false;
        playCurrent();
      } else {
        stage.value = "done";
      }
    } catch (error) {
      console.error('更新听写结果失败:', error)
      // 处理后端返回的错误信息
      if (error.response && error.response.data && error.response.data.error) {
      } else {
        errors.value.general = '更新听写结果失败，请稍后重试'
      }
    } finally {
      // loading.value = false
    }

}

/** ----- batch mode step ----- */
function nextBatchStep() {
  if (currentIndex.value < session.value.words.length - 1) {
    currentIndex.value += 1;
    playCurrent();
  } else {
    // 最后一题写完，进入核对页
    stage.value = "review";
  }
}

/** ----- batch review ----- */
function batchResult(id) {
  return session.value.results[id] || "";
}

async function markBatch(exercise_id, word_id, result) {
  session.value.results[word_id] = result == 0? "wrong" : "correct";
  try {
        const response = await api.put('/spellingbee/exercise/'+exercise_id, {
            "word_id":word_id,
            "result":result
        })
      } catch (error) {
        console.error('更新听写结果失败:', error)
        // 处理后端返回的错误信息
        if (error.response && error.response.data && error.response.data.error) {
        } else {
          errors.value.general = '更新听写结果失败，请稍后重试'
        }
      } finally {
        // loading.value = false
      }
}

const reviewedCount = computed(() => Object.keys(session.value.results).length);

function finishBatchReview() {
  // 必须全部都标注
  if (reviewedCount.value !== session.value.words.length) return;
  stage.value = "done";
}

/** --------- Summary --------- */
const correctCount = computed(() => Object.values(session.value.results).filter((v) => v === "correct").length);
const wrongCount = computed(() => Object.values(session.value.results).filter((v) => v === "wrong").length);

const wrongWords = computed(() => {
  const wrongIds = new Set(
    Object.entries(session.value.results)
      .filter(([, v]) => v === "wrong")
      .map(([id]) => Number(id))
  );
  return session.value.words.filter((w) => wrongIds.has(w.id));
});

/** --------- Restart --------- */
function restartSameSetup() {
  stage.value = "setup";
  startSession();
}

function restartWrongOnly() {
  session.value.words = wrongWords.value;
  session.value.results = {};
  currentIndex.value = 0;
  reveal.value = false;

  // 复习错词时：直接用逐题判分体验更好（也可以保持原模式）
  setup.value.mode = "immediate";
  stage.value = "doing";
  playCurrent();
}

function resetAll() {
  stage.value = "setup";
  session.value = { id: "", words: [], results: {} };
  currentIndex.value = 0;
  reveal.value = false;
  loading.value = false;
}

/** --------- TTS: Web Speech API --------- */
// function speak(text) {
//   if (!window.speechSynthesis) {
//     alert("当前浏览器不支持 Web Speech API");
//     return;
//   }
//   window.speechSynthesis.cancel();
//   const u = new SpeechSynthesisUtterance(text);
//   u.lang = "fr-FR";
//   u.rate = 0.9;
//   u.pitch = 1;
//   window.speechSynthesis.speak(u);
// }
let FR_VOICE = null;

function pickFrenchVoice() {
  const voices = window.speechSynthesis.getVoices() || [];

  // 优先：明确 fr-FR
  const fr = voices.filter(v => (v.lang || "").toLowerCase().startsWith("fr"));

  // 经验排序：更像高质量引擎的名字优先（可按你机器实际调整）
  const prefer = ["google", "microsoft", "amelie", "thomas", "français", "french"];
  fr.sort((a, b) => {
    const an = (a.name || "").toLowerCase();
    const bn = (b.name || "").toLowerCase();
    const as = prefer.findIndex(k => an.includes(k));
    const bs = prefer.findIndex(k => bn.includes(k));
    return (as === -1 ? 999 : as) - (bs === -1 ? 999 : bs);
  });

  return fr[0] || null;
}

// 把教材写法简单清洗成更适合 TTS 的文本
function normalizeForTTS(text) {
  if (!text) return "";

  return String(text)
    .trim()
    // 去掉括号内容：beau (bel, belle) -> beau
    .replace(/\s*\([^)]*\)\s*/g, " ")
    // 把逗号变体：désolé, e -> désolé
    .replace(/\s*,\s*[a-z]\b/gi, "")
    // 把斜杠：un/une -> un une（或你直接传拆分后的词更好）
    .replace(/\s*\/\s*/g, " ")
    // 多余空格
    .replace(/\s+/g, " ")
    .trim();
}

// 等 voices 加载
function initTTS() {
  if (!window.speechSynthesis) return;
  const trySet = () => { FR_VOICE = pickFrenchVoice(); };
  trySet();
  window.speechSynthesis.onvoiceschanged = () => {
    trySet();
  };
}
initTTS();

function speak(text) {
  if (!window.speechSynthesis) {
    alert("当前浏览器不支持 Web Speech API");
    return;
  }

  window.speechSynthesis.cancel();

  const u = new SpeechSynthesisUtterance(normalizeForTTS(text));
  u.lang = "fr-FR";
  if (FR_VOICE) u.voice = FR_VOICE;

  u.rate = 1.0;   // 先用 1.0 更稳
  u.pitch = 1.0;

  window.speechSynthesis.speak(u);
}
function goBack() {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push("/");
  }
}
</script>