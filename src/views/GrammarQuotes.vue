<template>
  <div class="page">
    <!-- ===== Toolbar ===== -->
    <header class="toolbar">
      <div class="title">
        <div class="badge">French</div>
        <h1>{{ data.source_title }}</h1>
      </div>

      <div class="controls">
        <label class="control">
          <span>语法点</span>
          <select v-model="selectedGrammarId">
            <option value="all">全部</option>
            <option
              v-for="gp in data.grammar_points"
              :key="gp.id"
              :value="gp.id"
            >
              {{ gp.name_zh }} / {{ gp.name_fr }}
            </option>
          </select>
        </label>

        <label class="control">
          <span>例句显示</span>
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

        <label class="control">
          <span>搜索</span>
          <input
            v-model.trim="keyword"
            type="text"
            placeholder="输入中文/法语关键词"
          />
        </label>

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
        <label class="control">
            <div class="seg">
                <button
                type="button"
                @click="goBack"
                >
                返回
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
            class="primary"
            :disabled="selectedCount === 0"
            @click="downloadPrintHtml"
            title="生成并下载可打印 HTML"
          >
            印刷已选（{{ selectedCount }}）
          </button>
          </div>
        <div class="section-head">
          <h2>金句 / 例句库</h2>
          <div class="meta">
            当前筛选 {{ filteredExamples.length }} 条｜
            已选 {{ selectedCount }} 条
          </div>
        </div>

        <div class="example-list">
          <div
            v-for="ex in filteredExamples"
            :key="ex.uid"
            class="example-card"
            :class="{ checked: isChecked(ex.uid) }"
            @click="toggleByCard(ex.uid)"
            role="button"
            tabindex="0"
          >
            <div class="checkbox-wrap" @click.stop>
              <input
                type="checkbox"
                :checked="isChecked(ex.uid)"
                @change="toggle(ex.uid)"
              />
            </div>

            <div class="card-main">
              <div class="card-top">
                <span class="tag">{{ ex.gpNameZh }}</span>
                <span class="pattern" v-if="ex.pattern">
                  {{ ex.pattern }}
                </span>
              </div>

              <div class="card-body">
                <template v-if="displayMode === 'both'">
                  <div class="fr">{{ ex.fr }}</div>
                  <div class="zh">{{ ex.zh }}</div>
                </template>
                <template v-else-if="displayMode === 'zh'">
                  <div class="zh only">{{ ex.zh }}</div>
                </template>
                <template v-else>
                  <div class="fr only">{{ ex.fr }}</div>
                </template>
              </div>
            </div>
          </div>
        </div>

        <div class="foot-hint">
          提示：点击卡片可快速勾选/取消；也可只点 checkbox。
          “印刷已选”会下载一个 HTML，打开后直接 Ctrl+P 即可打印。
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
const router = useRouter();
/**
 * 你之前那份 JSON 的“例句相关核心内容”内嵌版
 * （保持可读性 + 方便你后续替换为外部 JSON 文件）
 */
const data = {
  source_title: "初二法语语法学习清单（si 假设句 / tout / futur simple）",
  grammar_points: [
    {
      id: "si_present_real",
      name_zh: "si 引导的现实假设句（真实可能发生）",
      name_fr: "Si + présent (condition réelle)",
      examples: [
        {
          fr: "Si vous lui pardonnez, vous êtes généreux.",
          zh: "您如果能原谅他，您就是很宽宏大量的人。",
          pattern: "Si + présent, présent"
        },
        {
          fr: "S’il fait beau demain, nous irons à la Grande Muraille.",
          zh: "如果明天天气好，我们就去长城。",
          pattern: "Si + présent, futur"
        },
        {
          fr: "Si elle continue ainsi, elle réussira tôt ou tard.",
          zh: "她要是一直这样下去，迟早会成功。",
          pattern: "Si + présent, futur"
        },
        {
          fr: "Si tu passes par le magasin, achète-moi du pain.",
          zh: "如果你路过商店，给我买个面包。",
          pattern: "Si + présent, impératif"
        },
        {
          fr: "On va au cinéma si tu es libre ce soir.",
          zh: "要是你今晚有空，我们就去看电影。",
          pattern: "主句 + si + présent"
        },
        {
          fr: "Si vous êtes d’accord, on commencera tout de suite.",
          zh: "如果您同意，我们马上开始。",
          pattern: "Si + présent, futur"
        },
        {
          fr: "Si j’ai le temps, je ferai mes devoirs.",
          zh: "如果我有时间，我会做我的作业。",
          pattern: "Si + présent, futur"
        },
        {
          fr: "Si je finis mes devoirs, je jouerai aux jeux vidéo.",
          zh: "如果我完成我的作业，我会玩电子游戏。",
          pattern: "Si + présent, futur"
        },
        {
          fr: "Si tu es malade, tu restes à la maison.",
          zh: "如果你生病了，你就待在家里。",
          pattern: "Si + présent, présent"
        },
        {
          fr: "Nous irons à la montagne si tu as de bonnes notes.",
          zh: "如果你成绩好，我们就去山里/去山上。",
          pattern: "主句 (futur) + si + présent"
        },
        {
          fr: "Si tu es libre ce soir, on va au cinéma.",
          zh: "如果你今晚有空，我们就去看电影。",
          pattern: "顺序互换示例"
        }
      ]
    },
    {
      id: "tout_forms",
      name_zh: "TOUT 一词的四种形式与三大用法",
      name_fr: "tout / toute / tous / toutes",
      examples: [
        { fr: "Il a dormi toute la journée.", zh: "他睡了一整天。" },
        { fr: "On y va tous les ans.", zh: "我们每年都去那儿。" },
        { fr: "Tout va bien.", zh: "一切都好。" },
        { fr: "Je comprends tout.", zh: "我全都懂。" },
        { fr: "Ils sont tous là.", zh: "他们都在这儿。" },
        { fr: "Il est tout content.", zh: "他很高兴。（男的）" },
        { fr: "Elle est toute contente.", zh: "她很高兴。（女的）" },
        { fr: "Tout le monde n’est pas d’accord.", zh: "不是所有人都同意。（不是每个人都同意）" },
        { fr: "tout le monde", zh: "所有人" },
        { fr: "pas du tout", zh: "一点也不" },
        { fr: "tout de suite", zh: "马上" }
      ]
    },
    {
      id: "futur_simple",
      name_zh: "简单将来时",
      name_fr: "le futur simple",
      examples: [
        { fr: "Demain, nous irons au cinéma.", zh: "明天，我们将去电影院。" },
        { fr: "Je serai médecin.", zh: "我将成为医生。/我将来要当医生。" },
        { fr: "S’il fait beau demain, nous irons à la campagne.", zh: "如果明天天气好，我们就去乡下。" },
        { fr: "Si j’ai le temps, je ferai mes devoirs.", zh: "如果我有时间，我就做作业。" },
        { fr: "Demain, je ferai mes devoirs.", zh: "明天，我将做我的作业。" },
        { fr: "La semaine prochaine, nous irons au cinéma.", zh: "下周，我们将去看电影。" },
        { fr: "Plus tard, je vivrai à l’étranger.", zh: "以后，我将住在国外。" },
        { fr: "Si j’ai le temps, je jouerai au foot.", zh: "如果我有时间，我就去踢足球。" },
        { fr: "S’il fait beau demain, nous irons faire du ski.", zh: "如果明天天气好，我们就去滑雪。" },
        { fr: "Vous découvrirez la Bretagne en vélo.", zh: "你们会骑车游览布列塔尼。" },
        { fr: "Aujourd’hui, nous allons au cinéma.", zh: "今天我们去看电影。" },
        { fr: "Ce soir, je ferai mes devoirs.", zh: "今晚我将做作业。" }
      ]
    }
  ]
} as const;

type DisplayMode = "both" | "zh" | "fr";

type FlatExample = {
  uid: string;
  gpId: string;
  gpNameZh: string;
  gpNameFr: string;
  fr: string;
  zh: string;
  pattern?: string;
};

/** 扁平化例句（用常量数组，方便初始化“全选”） */
const allExamples: FlatExample[] = (() => {
  const list: FlatExample[] = [];
  data.grammar_points.forEach((gp) => {
    gp.examples.forEach((ex, idx) => {
      list.push({
        uid: `${gp.id}-${idx}`,
        gpId: gp.id,
        gpNameZh: gp.name_zh,
        gpNameFr: gp.name_fr,
        fr: ex.fr,
        zh: ex.zh,
        pattern: (ex as any).pattern
      });
    });
  });
  return list;
})();

/** UI state */
const displayMode = ref<DisplayMode>("both");
const selectedGrammarId = ref<string>("all");
const keyword = ref<string>("");
const linesPerQuote = ref<1 | 1>(1);

/** 选中集合：默认全选 */
const selectedUids = ref<Set<string>>(new Set(allExamples.map(e => e.uid)));

function isChecked(uid: string) {
  return selectedUids.value.has(uid);
}

function toggle(uid: string) {
  const s = new Set(selectedUids.value);
  if (s.has(uid)) s.delete(uid);
  else s.add(uid);
  selectedUids.value = s;
}

/** 点击卡片也能快速切换 */
function toggleByCard(uid: string) {
  toggle(uid);
}

/** 批量操作 */
function selectAll() {
  selectedUids.value = new Set(allExamples.map(e => e.uid));
}
function selectNone() {
  selectedUids.value = new Set();
}
function invertSelection() {
  const s = new Set<string>();
  for (const ex of allExamples) {
    if (!selectedUids.value.has(ex.uid)) s.add(ex.uid);
  }
  selectedUids.value = s;
}

/** 筛选 */
const filteredExamples = computed(() => {
  const k = keyword.value.toLowerCase();

  return allExamples.filter((ex) => {
    const okGrammar =
      selectedGrammarId.value === "all" || ex.gpId === selectedGrammarId.value;

    const okKeyword =
      !k ||
      ex.zh.toLowerCase().includes(k) ||
      ex.fr.toLowerCase().includes(k) ||
      ex.gpNameZh.toLowerCase().includes(k) ||
      ex.gpNameFr.toLowerCase().includes(k);

    return okGrammar && okKeyword;
  });
});

const selectedCount = computed(() => selectedUids.value.size);

/** 取已选例句（保持原始顺序） */
const selectedExamples = computed(() =>
  allExamples.filter(ex => selectedUids.value.has(ex.uid))
);

/** 生成可打印 HTML（每条：空行 + 中文） */
function buildPrintableHtml(examples: FlatExample[], lines: 2 | 3) {
  const escapeHtml = (s: string) =>
    s.replace(/&/g, "&amp;")
     .replace(/</g, "&lt;")
     .replace(/>/g, "&gt;")
     .replace(/"/g, "&quot;")
     .replace(/'/g, "&#039;");

  const quoteBlocks = examples.map((ex) => {
    const linesHtml = Array.from({ length: lines })
      .map(() => `<div class="line"></div>`)
      .join("");

    return `
      <div class="quote">
        <div class="lines">
          ${linesHtml}
        </div>
        <div class="zh">${escapeHtml(ex.zh)}</div>
      </div>
    `;
  }).join("");

  return `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>金句印刷</title>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 28px 26px 40px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 Roboto, "Noto Sans SC", "PingFang SC",
                 "Microsoft YaHei", Arial, sans-serif;
    color: #000;
    background: #fff;
  }
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
    letter-spacing: 0.04em;
  }
  .header .sub {
    font-size: 11px;
    color: #6b7280;
  }

  .quote {
    padding: 8px 2px 18px;
    margin-bottom: 16px;
    border-bottom: 1px dashed #d1d5db;
    page-break-inside: avoid;
  }

  .lines {
    margin-bottom: 10px;
  }
  .line {
    height: 24px;
    border-bottom: 1.3px solid #111;
    margin-bottom: 8px;
  }

  .zh {
    font-size: 18px;
    font-weight: 600;
    line-height: 1.55;
  }

  @media print {
    body { padding: 0; }
    .quote { border-bottom: none; }
  }
</style>
</head>
<body>
  <div class="header">
    <h1>金句印刷</h1>
    <div class="sub">
      共 ${examples.length} 条｜空行 ${lines} 行/条
    </div>
  </div>

  ${quoteBlocks}

</body>
</html>`;
}

/** 下载 HTML 文件 */
function downloadPrintHtml() {
  const list = selectedExamples.value;
  if (!list.length) return;

  const html = buildPrintableHtml(list, linesPerQuote.value);

  const blob = new Blob([html], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);

  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const filename = `金句印刷_${yyyy}${mm}${dd}.html`;

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();

  URL.revokeObjectURL(url);
}
function goBack() {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push("/"); // 默认回首页
  }
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
  grid-template-columns: 1.2fr 1fr 1fr 1fr auto;
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

/* actions */
.actions {
  display: grid;
  gap: 8px;
  justify-items: end;
}

.mini-actions {
  display: flex;
  gap: 6px;
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

.actions .primary {
  height: 36px;
  padding: 0 12px;
  border-radius: 10px;
  border: 1px solid rgba(59,130,246,0.35);
  background: rgba(59,130,246,0.18);
  color: #fff;
  cursor: pointer;
  font-size: 12px;
}

.actions .primary:disabled {
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
  max-height: calc(100vh - 230px);
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
  gap: 8px;
  align-items: center;
  margin-bottom: 6px;
}

.tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  color: rgba(229,231,235,0.9);
}

.pattern {
  font-size: 10px;
  color: rgba(229,231,235,0.65);
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
  .actions {
    justify-items: start;
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
