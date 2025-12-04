<template>
  <div class="lesson-page">
    <h1 class="lesson-title">{{ lesson.title }}</h1>

    <div class="layout">
      <!-- 左侧：句子列表 -->
      <div class="sentences">
        <div
          v-for="item in lesson.text"
          :key="item.id"
          class="sentence-card"
          :class="{ active: selected && selected.id === item.id }"
          @click="selectSentence(item)"
        >
          <div class="sentence-header">
            <span class="sentence-id">{{ item.id }}</span>
            <span class="sentence-level">等级: {{ item.level }}</span>
          </div>

          <div class="sentence-french">
            {{ item.french_full }}
          </div>
          <div class="sentence-chinese-hint">
            {{ item.chinese }}
          </div>

          <div class="sentence-meta">
            <span class="tag" v-for="tag in item.tags" :key="tag">{{ tag }}</span>
          </div>

          <div class="sentence-actions">
            <button
              class="small-btn"
              type="button"
            >
              查看讲义
            </button>
            <button
              class="small-btn ai-btn"
              type="button"
              @click.stop="askAI(item)"
              :disabled="loading && selected && selected.id === item.id"
            >
              {{ loading && selected && selected.id === item.id ? "AI 正在讲解..." : "让 AI 再讲一遍" }}
            </button>
          </div>
        </div>
      </div>

      <!-- 右侧：详细讲解区 -->
      <div class="explain-panel" v-if="selected">
        <!-- 原句 -->
        <section class="block">
          <h2>当前句子：{{ selected.id }}</h2>
          <p class="explain-french">{{ selected.french_full }}</p>
          <p class="explain-chinese">{{ selected.chinese }}</p>
          <p class="explain-meta">
            <strong>标签：</strong>
            <span v-for="tag in selected.tags" :key="tag" class="tag">{{ tag }}</span>
            <span class="tag level-tag">等级: {{ selected.level }}</span>
          </p>
        </section>

        <!-- 基础讲义（来自 JSON 的 explain） -->
        <section class="block" v-if="selected.explain">
          <h3>一、基础讲义（事先整理好的讲解）</h3>

          <div class="sub-block">
            <h4>1. 句子大意</h4>
            <p>{{ selected.explain.meaning }}</p>
          </div>

          <div
            class="sub-block"
            v-if="selected.explain.vocab && selected.explain.vocab.length"
          >
            <h4>2. 重点词汇 / 短语</h4>
            <ul class="vocab-list">
              <li v-for="(v, idx) in selected.explain.vocab" :key="idx">
                <strong>{{ v.item }}</strong> ：{{ v.note }}
              </li>
            </ul>
          </div>

          <div class="sub-block" v-if="selected.explain.grammar">
            <h4>3. 语法&动词变位</h4>
            <p>{{ selected.explain.grammar }}</p>
          </div>

          <div class="sub-block" v-if="selected.explain.usage">
            <h4>4. 使用场景 / 说话语气</h4>
            <p>{{ selected.explain.usage }}</p>
          </div>

          <p class="hint">
            建议孩子先把这里的讲解读一遍，有不懂的再点击左侧的「让 AI 再讲一遍」。
          </p>
        </section>

        <!-- AI 补充讲解 -->
        <section class="block">
          <h3>二、AI 补充讲解</h3>

          <div v-if="error" class="error">
            {{ error }}
          </div>

          <div v-if="loading && (!aiData || selected.id !== lastAnsweredId)">
            正在请 AI 老师讲解这句话……
          </div>

          <div v-if="!loading && !aiData">
            <p class="hint">
              还没有请求 AI。可以在左侧点击「让 AI 再讲一遍」，让模型用另一种方式再解释一次，或者举更多例句。
            </p>
          </div>

          <div v-if="aiData && selected.id === lastAnsweredId" class="ai-block">
            <!-- 如果模型按约定返回 JSON -->
            <div v-if="aiData.meaning || aiData.raw">
              <h4>1. AI 版本的大意</h4>
              <p>{{ aiData.meaning || aiData.raw }}</p>
            </div>

            <div
              class="sub-block"
              v-if="aiData.vocab && aiData.vocab.length"
            >
              <h4>2. AI 补充的词汇说明</h4>
              <ul class="vocab-list">
                <li v-for="(v, idx) in aiData.vocab" :key="idx">
                  <strong>{{ v.word }}</strong> ：{{ v.explain }}
                </li>
              </ul>
            </div>

            <div class="sub-block" v-if="aiData.grammar">
              <h4>3. AI 补充的语法说明</h4>
              <p>{{ aiData.grammar }}</p>
            </div>

            <div
              class="sub-block"
              v-if="aiData.examples && aiData.examples.length"
            >
              <h4>4. AI 举的类似例句</h4>
              <ul class="examples-list">
                <li v-for="(ex, idx) in aiData.examples" :key="idx">
                  <span class="example-fr">{{ ex.french }}</span>
                  <span class="example-zh"> — {{ ex.chinese }}</span>
                </li>
              </ul>
            </div>

            <div class="sub-block" v-if="aiData.tips">
              <h4>5. 学习小贴士</h4>
              <p>{{ aiData.tips }}</p>
            </div>
          </div>
        </section>
      </div>

      <div v-else class="empty-panel">
        <p>左边点一条句子，就可以看到这一句的“讲义 + AI 讲解”。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import lesson from "@/data/lecon1_rester_ou_partir.json";

const selected = ref(null);
const aiData = ref(null);
const loading = ref(false);
const error = ref("");
const lastAnsweredId = ref(null);

// 后端地址按你的实际情况修改
const API_BASE = "http://localhost:5000";

const selectSentence = (item) => {
  selected.value = item;
  error.value = "";
  // 切换句子时，不清空 aiData，让上一句的结果保留在内存也行
  // 如果你希望每换一句就清空 AI 结果，可以取消注释下一行：
  // aiData.value = null;
};

const askAI = async (item) => {
  selected.value = item;
  error.value = "";
  loading.value = true;

  try {
    const res = await fetch(`${API_BASE}/api/explain`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        lesson_title: lesson.title,
        sentence_id: item.id,
        french_text: item.french_full,
        chinese_hint: item.chinese,
        question:
          "请用适合初二学生的中文，再讲解一下这句话，包括大意、重点词汇、语法和再举一两个类似例句。"
      })
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const json = await res.json();
    if (!json.ok) {
      throw new Error(json.error || "后端返回错误");
    }

    aiData.value = json.data;
    lastAnsweredId.value = item.id;
  } catch (e) {
    console.error(e);
    error.value = "请求 AI 讲解失败，请稍后重试。";
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.lesson-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.lesson-title {
  font-size: 24px;
  margin-bottom: 16px;
}

.layout {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

/* 左侧句子列表 */
.sentences {
  flex: 1;
  max-height: 80vh;
  overflow-y: auto;
  padding-right: 8px;
}

.sentence-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 8px 10px;
  margin-bottom: 8px;
  background: #fff;
  cursor: pointer;
  transition: box-shadow 0.15s ease, border-color 0.15s ease, background-color 0.15s ease;
}

.sentence-card:hover {
  border-color: #409eff;
  background: #f7fbff;
}

.sentence-card.active {
  border-color: #409eff;
  box-shadow: 0 0 0 1px rgba(64, 158, 255, 0.25);
  background: #f0f7ff;
}

.sentence-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #777;
}

.sentence-id {
  font-weight: 600;
}

.sentence-level {
  font-size: 11px;
}

.sentence-french {
  margin-top: 4px;
  font-weight: 600;
  font-size: 14px;
}

.sentence-chinese-hint {
  margin-top: 4px;
  font-size: 13px;
  color: #555;
}

.sentence-meta {
  margin-top: 4px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.sentence-actions {
  margin-top: 4px;
  display: flex;
  gap: 6px;
}

.small-btn {
  padding: 2px 8px;
  font-size: 12px;
  border-radius: 10px;
  border: 1px solid #ccc;
  background: #fafafa;
  cursor: pointer;
}

.small-btn:hover {
  background: #f0f0f0;
}

.small-btn.ai-btn {
  border-color: #409eff;
  color: #409eff;
}

.small-btn.ai-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 右侧讲解区 */
.explain-panel {
  flex: 1;
  border-left: 1px solid #eee;
  padding-left: 16px;
  max-height: 80vh;
  overflow-y: auto;
}

.empty-panel {
  flex: 1;
  border-left: 1px solid #eee;
  padding-left: 16px;
  color: #888;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.block {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #eee;
}

.explain-french {
  font-weight: 600;
  margin: 4px 0;
}

.explain-chinese {
  margin: 2px 0 4px;
  color: #444;
}

.explain-meta {
  font-size: 12px;
  color: #666;
}

.tag {
  display: inline-block;
  font-size: 11px;
  background: #f0f0f0;
  border-radius: 999px;
  padding: 2px 6px;
  margin-right: 4px;
  margin-top: 2px;
}

.level-tag {
  background: #eaf3ff;
  color: #2c73d6;
}

.sub-block {
  margin-top: 6px;
}

.sub-block h4 {
  margin-bottom: 2px;
  font-size: 14px;
}

.vocab-list,
.examples-list {
  padding-left: 16px;
  margin: 4px 0;
}

.example-fr {
  font-weight: 600;
}

.example-zh {
  margin-left: 4px;
  color: #555;
}

.hint {
  font-size: 12px;
  color: #777;
  margin-top: 4px;
}

.error {
  color: #d9534f;
  font-size: 13px;
}

/* AI 区块 */
.ai-block {
  background: #fafbff;
  border-radius: 8px;
  padding: 8px 10px;
}
</style>
