<template>
  <div class="page">
    <!-- ===== Toolbar ===== -->
    <header class="toolbar">
      <div class="title">
        <div class="badge">French</div>
        <h1>{{ data.source_title }}</h1>
      </div>

      <div class="controls">
        <!-- Level filter -->
        <label class="control">
          <span>层级</span>
          <select v-model="selectedLevel">
            <option value="all">全部</option>
            <option v-for="lv in levelKeys" :key="lv" :value="lv">
              {{ lv }} 层
            </option>
          </select>
        </label>

        <!-- Grammar point filter -->
        <label class="control">
          <span>语法点</span>
          <select v-model="selectedGpId">
            <option value="all">全部</option>
            <option
              v-for="gp in allGrammarPoints"
              :key="gp.id"
              :value="gp.id"
            >
              {{ gp.level }}｜{{ gp.name_zh }} / {{ gp.name_fr }}
            </option>
          </select>
        </label>

        <!-- Display mode -->
        <label class="control">
          <span>金句显示</span>
          <div class="seg">
            <button
              type="button"
              :class="{ active: displayMode === 'both' }"
              @click="displayMode = 'both'"
            >
              中法
            </button>
            <button
              type="button"
              :class="{ active: displayMode === 'zh' }"
              @click="displayMode = 'zh'"
            >
              中文
            </button>
            <button
              type="button"
              :class="{ active: displayMode === 'fr' }"
              @click="displayMode = 'fr'"
            >
              法语
            </button>
          </div>
        </label>

        <!-- Search -->
        <label class="control">
          <span>搜索</span>
          <input
            v-model.trim="keyword"
            type="text"
            placeholder="输入中文/法语/规则关键词"
          />
        </label>

        <!-- Lines per quote -->
        <label class="control">
          <span>空行数量（每条金句）</span>
          <div class="seg">
            <button
              type="button"
              :class="{ active: linesPerQuote === 2 }"
              @click="linesPerQuote = 2"
            >
              2 行
            </button>
            <button
              type="button"
              :class="{ active: linesPerQuote === 3 }"
              @click="linesPerQuote = 3"
            >
              3 行
            </button>
          </div>
        </label>
      </div>
    </header>

    <!-- ===== Content ===== -->
    <main class="content">
      <section class="examples">
        <div class="mini-actions">
          <button type="button" @click="selectAll">
            全选
          </button>
          <button type="button" @click="selectNone">
            全不选
          </button>
          <button type="button" @click="invertSelection">
            反选
          </button>

          <button
            type="button"
            :disabled="selectedCount === 0"
            @click="downloadPrintHtml"
            title="生成并下载可打印 HTML"
          >
            印刷已选（{{ selectedCount }}）
          </button>
          <button type="button" @click="goBack">
            返回
          </button>
        </div>

        <div class="section-head">
          <h2>第三课 Notes 金句库（A/B/C）</h2>
          <div class="meta">
            当前筛选 {{ filteredQuotes.length }} 条｜
            已选 {{ selectedCount }} 条
          </div>
        </div>

        <div class="example-list">
          <div
            v-for="q in filteredQuotes"
            :key="q.uid"
            class="example-card"
            :class="{ checked: isChecked(q.uid) }"
            @click="toggleByCard(q.uid)"
            role="button"
            tabindex="0"
          >
            <div class="checkbox-wrap" @click.stop>
              <input
                type="checkbox"
                :checked="isChecked(q.uid)"
                @change="toggle(q.uid)"
              />
            </div>

            <div class="card-main">
              <div class="card-top">
                <span class="tag level">{{ q.level }}</span>
                <span class="tag">{{ q.gpNameZh }}</span>
                <span class="tag subtle">{{ q.gpNameFr }}</span>
              </div>

              <div class="mini-rule" v-if="q.miniRule">
                {{ q.miniRule }}
              </div>

              <div class="card-body">
                <template v-if="displayMode === 'both'">
                  <div class="fr">{{ q.fr }}</div>
                  <div class="zh">{{ q.zh }}</div>
                </template>
                <template v-else-if="displayMode === 'zh'">
                  <div class="zh only">{{ q.zh }}</div>
                </template>
                <template v-else>
                  <div class="fr only">{{ q.fr }}</div>
                </template>
              </div>
            </div>
          </div>
        </div>

        <div class="foot-hint">
          提示：点击卡片可快速勾选/取消；也可只点 checkbox。<br />
          “印刷已选”会下载一个 HTML，打开后直接 Ctrl+P 即可打印。<br />
          当前印刷格式：每条金句上方 {{ linesPerQuote }} 行空行 + 中文提示（适合默写法语）。
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute,useRouter } from "vue-router";
import getNotesDataByLesson from "@/services/notesService";
import type { RootData, LevelKey, GrammarPoint } from "@/data/lesson_03/notes";

const route = useRoute();
const router = useRouter();

const lessonNo = computed(() => Number(route.query.lesson || 3));

const data = computed<RootData>(() => getNotesDataByLesson(lessonNo.value));

const levelKeys = computed<LevelKey[]>(() => ["A", "B", "C"]);

/** 汇总语法点用于下拉 */
const allGrammarPoints = computed(() => {
  const out: Array<GrammarPoint & { level: LevelKey }> = [];
  levelKeys.value.forEach((lv) => {
    const arr = data.value.levels?.[lv] || [];
    arr.forEach((gp) => out.push({ ...gp, level: lv }));
  });
  return out;
});

/** 扁平化金句 */
type FlatQuote = {
  uid: string;
  level: LevelKey;
  gpId: string;
  gpNameZh: string;
  gpNameFr: string;
  miniRule: string;
  fr: string;
  zh: string;
};

const allQuotes = computed<FlatQuote[]>(() => {
  const list: FlatQuote[] = [];
  levelKeys.value.forEach((lv) => {
    const gps = data.value.levels?.[lv] || [];
    gps.forEach((gp) => {
      const quotes = Array.isArray(gp.must_memorize) ? gp.must_memorize : [];
      quotes.forEach((q, idx) => {
        if (!q?.fr || !q?.zh) return;
        list.push({
          uid: `${lv}-${gp.id}-${idx}`,
          level: lv,
          gpId: gp.id,
          gpNameZh: gp.name_zh,
          gpNameFr: gp.name_fr,
          miniRule: gp.mini_rule || "",
          fr: q.fr,
          zh: q.zh
        });
      });
    });
  });
  return list;
});

// ===== UI state =====
const displayMode = ref<"both" | "zh" | "fr">("both");
const selectedLevel = ref<"all" | LevelKey>("all");
const selectedGpId = ref<string>("all");
const keyword = ref<string>("");
const linesPerQuote = ref<2 | 3>(2);

// ===== selection =====
const selectedUids = ref<Set<string>>(new Set());

/** 初次加载默认全选 */
watch(
  allQuotes,
  (quotes) => {
    if (quotes.length > 0 && selectedUids.value.size === 0) {
      selectedUids.value = new Set(quotes.map((q) => q.uid));
    }
  },
  { immediate: true }
);

function isChecked(uid: string) {
  return selectedUids.value.has(uid);
}

function toggle(uid: string) {
  const s = new Set(selectedUids.value);
  if (s.has(uid)) s.delete(uid);
  else s.add(uid);
  selectedUids.value = s;
}

function toggleByCard(uid: string) {
  toggle(uid);
}

function selectAll() {
  selectedUids.value = new Set(allQuotes.value.map((q) => q.uid));
}
function selectNone() {
  selectedUids.value = new Set();
}
function invertSelection() {
  const s = new Set<string>();
  for (const q of allQuotes.value) {
    if (!selectedUids.value.has(q.uid)) s.add(q.uid);
  }
  selectedUids.value = s;
}

// ===== filter =====
const filteredQuotes = computed(() => {
  const k = keyword.value.trim().toLowerCase();

  return allQuotes.value.filter((q) => {
    const okLevel = selectedLevel.value === "all" || q.level === selectedLevel.value;
    const okGp = selectedGpId.value === "all" || q.gpId === selectedGpId.value;

    const okKeyword =
      !k ||
      q.zh.toLowerCase().includes(k) ||
      q.fr.toLowerCase().includes(k) ||
      q.gpNameZh.toLowerCase().includes(k) ||
      q.gpNameFr.toLowerCase().includes(k) ||
      (q.miniRule || "").toLowerCase().includes(k);

    return okLevel && okGp && okKeyword;
  });
});

const selectedCount = computed(() => selectedUids.value.size);

const selectedQuotes = computed(() =>
  allQuotes.value.filter((q) => selectedUids.value.has(q.uid))
);

/** 生成可打印 HTML（每条：空行 + 中文 + 页眉页脚 + 页码） */
function buildPrintableHtml(quotes: FlatQuote[], lines: 2 | 3) {
  const escapeHtml = (s: string) =>
    String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");

  const blocks = quotes
    .map((q) => {
      const linesHtml = Array.from({ length: lines })
        .map(() => `<div class="line"></div>`)
        .join("");

      return `
      <div class="quote">
        <div class="meta">
          <span class="lv">${escapeHtml(q.level)}</span>
          <span class="gp">${escapeHtml(q.gpNameZh)}</span>
        </div>
        <div class="lines">${linesHtml}</div>
        <div class="zh">${escapeHtml(q.zh)}</div>
      </div>
    `;
    })
    .join("");

  const today = new Date();
  const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(
    2,
    "0"
  )}-${String(today.getDate()).padStart(2, "0")}`;

  return `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>金句印刷</title>
<style>
  * { box-sizing: border-box; }

  /* ====== Print page config (best-effort) ====== */
  @page {
    /* 给页眉页脚预留空间 */
    margin: 18mm 12mm 20mm 12mm;
  }

  body {
    margin: 0;
    padding: 28px 26px 40px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 Roboto, "Noto Sans SC", "PingFang SC",
                 "Microsoft YaHei", Arial, sans-serif;
    color: #000;
    background: #fff;
  }

  /* ====== Screen header ====== */
  .header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 18px;
    padding-bottom: 10px;
    border-bottom: 1px solid #e5e7eb;
  }
  .header h1 {
    font-size: 18px;
    margin: 0;
  }
  .header .sub {
    font-size: 11px;
    color: #6b7280;
  }

  /* ====== Quote blocks ====== */
  .quote {
    padding: 10px 2px 18px;
    margin-bottom: 16px;
    border-bottom: 1px dashed #d1d5db;
    page-break-inside: avoid;
  }

  .meta {
    font-size: 10px;
    color: #6b7280;
    margin-bottom: 6px;
    display: flex;
    gap: 6px;
  }
  .meta .lv {
    padding: 1px 6px;
    border: 1px solid #d1d5db;
    border-radius: 999px;
  }
  .meta .gp {
    font-weight: 600;
  }

  .lines { margin-bottom: 10px; }
  .line {
    height: 24px;
    border-bottom: 1.3px solid #111;
    margin-bottom: 8px;
  }

  .zh {
    font-size: 18px;
    font-weight: 600;
    line-height: 1.55;
    margin-bottom: 6px;
  }
  .fr-hint {
    font-size: 12px;
    color: #6b7280;
  }

  /* ====== Print header/footer (repeat on each page) ====== */
  .print-header,
  .print-footer {
    display: none;
  }

  @media print {
    body {
      /* 让正文不要压住固定页眉页脚 */
      padding: 0;
    }

    /* 让内容有“视觉上的”上下留白 */
    .content-wrap {
      padding-top: 12mm;
      padding-bottom: 12mm;
    }

    .header {
      display: none; /* 屏幕头隐藏 */
    }

    .quote {
      border-bottom: none;
    }

    .print-header {
      display: flex;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 12mm;
      padding: 0 12mm;
      align-items: center;
      justify-content: space-between;
      font-size: 10px;
      color: #6b7280;
      border-bottom: 1px solid #e5e7eb;
      background: #fff;
    }

    .print-footer {
      display: flex;
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 12mm;
      padding: 0 12mm;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      color: #6b7280;
      border-top: 1px solid #e5e7eb;
      background: #fff;
    }

    /* CSS page counters (best-effort; some browsers may partially ignore) */
    .print-footer::after {
      content: "第 " counter(page) " / " counter(pages) " 页";
    }
  }
</style>
</head>
<body>

  <!-- 尝试自带页眉页脚 -->
  <div class="print-header">
    <div>第三课 Notes 金句默写</div>
    <div>${dateStr}</div>
  </div>
  <div class="print-footer"></div>

  <!-- 屏幕显示头 -->
  <div class="header">
    <h1>第三课 Notes 金句印刷</h1>
    <div class="sub">
      共 ${quotes.length} 条｜空行 ${lines} 行/条
    </div>
  </div>

  <div class="content-wrap">
    ${blocks}
  </div>

</body>
</html>`;
}


function downloadPrintHtml() {
  const list = selectedQuotes.value;
  if (!list.length) return;

  const html = buildPrintableHtml(list, linesPerQuote.value);
  const blob = new Blob([html], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);

  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const filename = `第三课_Notes_金句印刷_${yyyy}${mm}${dd}.html`;

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();

  URL.revokeObjectURL(url);
}

function goBack(){
  router.push('/')
}
</script>

<style scoped>
/* ===== Page base ===== */
.page {
  min-height: 100vh;
  background: #0f172a;
  color: #e5e7eb;
}

/* ===== Toolbar ===== */
.toolbar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: linear-gradient(180deg, rgba(15,23,42,0.98), rgba(15,23,42,0.9));
  border-bottom: 1px solid rgba(255,255,255,0.08);
  padding: 18px 22px 14px;
  backdrop-filter: blur(10px);
}

.title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.badge {
  font-size: 12px;
  letter-spacing: 0.06em;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
}

.title h1 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

/* ===== Controls ===== */
.controls {
  display: grid;
  grid-template-columns: 0.7fr 1.4fr 1fr 1fr 1fr;
  gap: 12px;
  align-items: end;
}

.control {
  display: grid;
  gap: 6px;
}

.control > span {
  font-size: 12px;
  color: rgba(229,231,235,0.75);
}

select,
input {
  height: 36px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  color: #e5e7eb;
  padding: 0 10px;
  outline: none;
}

select:focus,
input:focus {
  border-color: rgba(255,255,255,0.28);
  box-shadow: 0 0 0 2px rgba(255,255,255,0.08);
}

/* segmented buttons */
.seg {
  display: inline-flex;
  gap: 6px;
  background: rgba(255,255,255,0.06);
  padding: 4px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
}

.seg button {
  height: 28px;
  padding: 0 10px;
  border-radius: 8px;
  border: 1px solid transparent;
  background: transparent;
  color: rgba(229,231,235,0.85);
  cursor: pointer;
  font-size: 12px;
}

.seg button.active {
  background: rgba(255,255,255,0.12);
  border-color: rgba(255,255,255,0.18);
  color: #fff;
}

/* mini actions */
.mini-actions {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
}

.mini-actions button {
  height: 28px;
  padding: 0 10px;
  border-radius: 9px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  color: #e5e7eb;
  cursor: pointer;
  font-size: 11px;
}

.mini-actions .primary {
  height: 36px;
  padding: 0 12px;
  border-radius: 10px;
  border: 1px solid rgba(59,130,246,0.35);
  background: rgba(59,130,246,0.18);
  color: #fff;
  cursor: pointer;
  font-size: 12px;
}

.mini-actions .primary:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* ===== Content ===== */
.content {
  padding: 18px 22px 36px;
}

.examples {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 16px;
}

/* header */
.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 10px;
}

.section-head h2 {
  font-size: 16px;
  margin: 0;
}

.meta {
  font-size: 11px;
  color: rgba(229,231,235,0.7);
}

/* list */
.example-list {
  display: grid;
  gap: 10px;
  max-height: calc(100vh - 240px);
  overflow: auto;
  padding-right: 6px;
}

/* card with checkbox */
.example-card {
  display: grid;
  grid-template-columns: 34px 1fr;
  gap: 8px;
  align-items: start;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.04);
  padding: 10px 12px 10px 8px;
  cursor: pointer;
  transition: 0.18s ease;
}

.example-card:hover {
  border-color: rgba(255,255,255,0.18);
  background: rgba(255,255,255,0.07);
}

.example-card.checked {
  border-color: rgba(59,130,246,0.55);
  background: rgba(59,130,246,0.12);
}

.checkbox-wrap {
  display: grid;
  place-items: center;
  padding-top: 6px;
}

.checkbox-wrap input {
  width: 16px;
  height: 16px;
  accent-color: #60a5fa;
  cursor: pointer;
}

/* card inner */
.card-top {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  color: rgba(229,231,235,0.9);
}

.tag.level {
  background: rgba(59,130,246,0.18);
  border-color: rgba(59,130,246,0.35);
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.tag.subtle {
  color: rgba(229,231,235,0.7);
}

.mini-rule {
  font-size: 11px;
  color: rgba(229,231,235,0.7);
  margin-bottom: 8px;
}

.fr {
  font-size: 14px;
  line-height: 1.35;
  color: #f8fafc;
}

.zh {
  font-size: 13px;
  line-height: 1.45;
  color: rgba(229,231,235,0.9);
  margin-top: 4px;
}

.only {
  margin-top: 0;
}

.foot-hint {
  margin-top: 12px;
  font-size: 11px;
  color: rgba(229,231,235,0.65);
}

/* ===== Responsive ===== */
@media (max-width: 1200px) {
  .controls {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 720px) {
  .mini-actions {
    flex-wrap: wrap;
  }
  .example-list {
    max-height: 60vh;
  }
}
</style>
