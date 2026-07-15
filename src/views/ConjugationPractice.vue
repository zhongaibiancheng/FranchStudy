<template>
  <div class="page">
    <header class="toolbar">
      <div class="title">
        <div class="badge">French</div>
        <h1>{{ currentData?.title || '动词变位默写' }}</h1>
      </div>

      <div class="controls">
        <label class="control">
          <span>练习文件</span>
          <select v-model="selectedFileId" @change="switchFile">
            <option v-for="f in availableFiles" :key="f.id" :value="f.id">
              {{ f.name }}
            </option>
          </select>
        </label>

        <label class="control">
          <span>版本</span>
          <div class="seg">
            <button
              type="button"
              :class="{ active: mode === 'practice' }"
              @click="mode = 'practice'"
            >
              默写版
            </button>
            <button
              type="button"
              :class="{ active: mode === 'answer' }"
              @click="mode = 'answer'"
            >
              答案版
            </button>
          </div>
        </label>

        <label class="control">
          <div class="seg">
            <button type="button" @click="goBack">返回</button>
          </div>
        </label>
      </div>
    </header>

    <main class="content">
      <section class="examples">
        <div class="mini-actions">
          <button type="button" @click="selectAll">全选</button>
          <button type="button" @click="selectNone">全不选</button>
          <button type="button" @click="invertSelection">反选</button>
          <button
            type="button"
            class="primary"
            :disabled="selectedCount === 0"
            @click="downloadPrintHtml"
          >
            印刷已选（{{ selectedCount }}）
          </button>
        </div>

        <div class="section-head">
          <h2>动词列表</h2>
          <div class="meta">
            共 {{ verbs.length }} 个动词 ｜ 已选 {{ selectedCount }} 个
          </div>
        </div>

        <div class="verb-list">
          <div
            v-for="(v, i) in verbs"
            :key="v.name"
            class="verb-card"
            :class="{ checked: isChecked(i) }"
            @click="toggle(i)"
            role="button"
            tabindex="0"
          >
            <div class="checkbox-wrap" @click.stop>
              <input
                type="checkbox"
                :checked="isChecked(i)"
                @change="toggle(i)"
              />
            </div>

            <div class="card-main">
              <div class="card-top">
                <span class="verb-num">{{ i + 1 }}</span>
                <span class="verb-name">{{ v.name }}</span>
                <span class="verb-meaning">{{ v.meaning }}</span>
              </div>

              <div class="mini-table-wrap">
                <table class="mini-table">
                  <thead>
                    <tr>
                      <th>主语</th>
                      <th v-for="t in currentData.tenses" :key="t">{{ t }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, ri) in displayRows(v)" :key="ri">
                      <td class="subject-cell">{{ currentData.subjects[ri] }}</td>
                      <td
                        v-for="(cell, ci) in row"
                        :key="ci"
                      >
                        {{ mode === 'answer' ? cell : '' }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import verbsA2 from '@/data/practice-sheets/verbs_a2.json'

const router = useRouter()

const availableFiles = [
  { id: 'verbs-a2', name: 'A2 动词变位默写 (31个)', data: verbsA2 }
]

const selectedFileId = ref('verbs-a2')
const mode = ref('practice')
const selectedIndexes = ref(new Set())

const currentData = computed(() => {
  const f = availableFiles.find(x => x.id === selectedFileId.value)
  return f?.data || availableFiles[0].data
})

const verbs = computed(() => currentData.value?.verbs || [])

const subjects = computed(() => currentData.value?.subjects || [])

const selectedCount = computed(() => selectedIndexes.value.size)

function isChecked(i) {
  return selectedIndexes.value.has(i)
}

function toggle(i) {
  const s = new Set(selectedIndexes.value)
  if (s.has(i)) s.delete(i)
  else s.add(i)
  selectedIndexes.value = s
}

function selectAll() {
  selectedIndexes.value = new Set(verbs.value.map((_, i) => i))
}

function selectNone() {
  selectedIndexes.value = new Set()
}

function invertSelection() {
  const s = new Set()
  for (let i = 0; i < verbs.value.length; i++) {
    if (!selectedIndexes.value.has(i)) s.add(i)
  }
  selectedIndexes.value = s
}

function switchFile() {
  selectedIndexes.value = new Set(verbs.value.map((_, i) => i))
}

function displayRows(v) {
  return mode.value === 'answer' ? v.answer : v.practice
}

function escapeHtml(s) {
  return String(s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

function buildPrintableHtml() {
  const selected = [...selectedIndexes.value].sort((a, b) => a - b)
  const isPractice = mode.value === 'practice'
  const data = currentData.value
  const tenses = data.tenses
  const allSubjects = data.subjects

  const tableHtml = (v) => {
    const rows = isPractice ? v.practice : v.answer
    if (!rows || rows.length === 0) return ''
    const subjRow = allSubjects.slice(0, rows.length)

    return `
      <table>
        <thead>
          <tr>
            <th>主语</th>
            ${tenses.map(t => `<th>${escapeHtml(t)}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${rows.map((r, ri) => `
            <tr>
              <td class="subject">${escapeHtml(subjRow[ri])}</td>
              ${r.map(c => `
                <td class="${isPractice && !c ? 'blank' : ''}">${isPractice ? '' : escapeHtml(c)}</td>
              `).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>
    `
  }

  const blocks = selected.map(i => {
    const v = verbs.value[i]
    return `
      <div class="verb-block">
        <h2>${escapeHtml(i + 1)}) ${escapeHtml(v.name)}（${escapeHtml(v.meaning)}）</h2>
        ${tableHtml(v)}
      </div>
    `
  }).join('')

  const modeLabel = isPractice ? '默写版' : '答案版'

  const d = new Date()
  const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

  return `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>${escapeHtml(data.title)} - ${modeLabel}</title>
<style>
  * { box-sizing: border-box; }
  @page { margin: 15mm 12mm 18mm 12mm; }
  body {
    margin: 0;
    padding: 24px 20px 30px;
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
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #e5e7eb;
  }
  .header h1 { font-size: 18px; margin: 0; }
  .header .sub { font-size: 11px; color: #6b7280; }
  .verb-block { page-break-inside: avoid; margin-bottom: 24px; }
  .verb-block h2 {
    font-size: 15px; margin: 0 0 8px;
    padding-bottom: 4px; border-bottom: 1px solid #e5e7eb;
  }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th, td { border: 1px solid #d1d5db; padding: 6px 8px; text-align: center; }
  th { background: #f3f4f6; font-weight: 600; font-size: 12px; }
  td.subject {
    font-weight: 600; background: #fafafa;
    width: 60px; white-space: nowrap;
  }
  td.blank {
    min-width: 60px; height: 28px;
    border-bottom: 1.5px solid #111;
    border-left: 1px solid #d1d5db;
    border-right: 1px solid #d1d5db;
    border-top: 1px solid #d1d5db;
    background: transparent;
  }
  .print-header, .print-footer { display: none; }
  @media print {
    body { padding: 0; }
    .header { display: none; }
    .print-header {
      display: flex; position: fixed; top: 0; left: 0; right: 0;
      height: 10mm; padding: 0 12mm;
      align-items: center; justify-content: space-between;
      font-size: 10px; color: #6b7280;
      border-bottom: 1px solid #e5e7eb; background: #fff;
    }
    .print-footer {
      display: flex; position: fixed; bottom: 0; left: 0; right: 0;
      height: 10mm; padding: 0 12mm;
      align-items: center; justify-content: center;
      font-size: 10px; color: #6b7280;
      border-top: 1px solid #e5e7eb; background: #fff;
    }
    .print-footer::after { content: "第 " counter(page) " / " counter(pages) " 页"; }
  }
</style>
</head>
<body>
<div class="print-header">
  <div>${escapeHtml(data.title)} - ${modeLabel}</div>
  <div>${dateStr}</div>
</div>
<div class="print-footer"></div>
<div class="header">
  <h1>${escapeHtml(data.title)} - ${modeLabel}</h1>
  <div class="sub">共 ${selected.length} 个动词 ｜ ${dateStr}</div>
</div>
${blocks}
</body>
</html>`
}

function downloadPrintHtml() {
  if (selectedCount.value === 0) return
  const html = buildPrintableHtml()
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)

  const d = new Date()
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const modeLabel = mode.value === 'practice' ? '默写版' : '答案版'

  const a = document.createElement('a')
  a.href = url
  a.download = `动词变位_${modeLabel}_${yyyy}${mm}${dd}.html`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/')
}

switchFile()
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #0f172a;
  color: #e5e7eb;
}
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
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.controls {
  display: grid;
  grid-template-columns: 1.4fr 1fr auto;
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
select, input {
  height: 36px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  color: #e5e7eb;
  padding: 0 10px;
  outline: none;
}
select:focus, input:focus {
  border-color: rgba(255,255,255,0.28);
  box-shadow: 0 0 0 2px rgba(255,255,255,0.08);
}
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
.mini-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
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
.content {
  padding: 18px 22px 36px;
}
.examples {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 16px;
}
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
.verb-list {
  display: grid;
  gap: 10px;
  max-height: calc(100vh - 230px);
  overflow: auto;
  padding-right: 6px;
}
.verb-card {
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
.verb-card:hover {
  border-color: rgba(255,255,255,0.18);
  background: rgba(255,255,255,0.07);
}
.verb-card.checked {
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
.card-top {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 6px;
}
.verb-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  font-size: 11px;
  font-weight: 600;
  color: rgba(229,231,235,0.9);
}
.verb-name {
  font-size: 15px;
  font-weight: 600;
  color: #f8fafc;
}
.verb-meaning {
  font-size: 12px;
  color: rgba(229,231,235,0.7);
}
.mini-table-wrap {
  overflow-x: auto;
}
.mini-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}
.mini-table th {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  padding: 4px 6px;
  text-align: center;
  font-weight: 600;
  color: rgba(229,231,235,0.85);
  white-space: nowrap;
}
.mini-table td {
  border: 1px solid rgba(255,255,255,0.08);
  padding: 3px 6px;
  text-align: center;
  color: rgba(229,231,235,0.7);
}
.mini-table .subject-cell {
  font-weight: 600;
  color: rgba(229,231,235,0.9);
  background: rgba(255,255,255,0.03);
  white-space: nowrap;
}
@media (max-width: 1200px) {
  .controls { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 720px) {
  .verb-list { max-height: 60vh; }
}
</style>
