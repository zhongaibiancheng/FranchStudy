<template>
  <div class="sentence-card">
    <div class="card-header">
      <div class="left">
        <span class="id">{{ item.id }}</span>
        <span class="badge source">{{ item.source }}</span>
        <span class="badge level">Level {{ item.level }}</span>

        <span
          v-for="t in (item.tags || [])"
          :key="t"
          class="badge tag"
        >
          {{ t }}
        </span>
      </div>

      <div class="right">
        <!-- ✅ 单句切换原文/挖空 -->
        <button
          class="mini-btn"
          :disabled="forceGap"
          @click.stop="toggleGap"
          :title="forceGap ? '已开启全局挖空模式' : ''"
        >
          <span v-if="forceGap">全局挖空中</span>
          <span v-else>{{ localShowGap ? '切回原文' : '查看挖空版' }}</span>
        </button>
      </div>
    </div>

    <!-- ✅ 法语 -->
    <div class="french">
      <div class="label">法语</div>
      <div class="text">
        {{ displayedFrench }}
      </div>
    </div>

    <!-- ✅ 中文（受全局 showChinese 控制） -->
    <div v-if="showChinese" class="chinese">
      <div class="label">中文</div>
      <div class="text">
        {{ item.chinese || '（暂无中文）' }}
      </div>
    </div>

    <!-- 可选：讲解 -->
    <details class="detail">
      <summary>查看讲解</summary>
      <div class="explain">
        <div v-if="item.explain?.meaning" class="block">
          <div class="label">句意</div>
          <div class="text">{{ item.explain.meaning }}</div>
        </div>

        <div v-if="item.explain?.vocab?.length" class="block">
          <div class="label">词汇提示</div>
          <ul class="vocab-list">
            <li v-for="(v, i) in item.explain.vocab" :key="i">
              <strong>{{ v.item }}</strong>：{{ v.note }}
            </li>
          </ul>
        </div>

        <div v-if="item.explain?.grammar" class="block">
          <div class="label">语法</div>
          <div class="text">{{ item.explain.grammar }}</div>
        </div>

        <div v-if="item.explain?.usage" class="block">
          <div class="label">使用场景</div>
          <div class="text">{{ item.explain.usage }}</div>
        </div>
      </div>
    </details>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
  showChinese: { type: Boolean, default: false },
  // ✅ 全局挖空模式开关
  forceGap: { type: Boolean, default: false }
})

const localShowGap = ref(false)

const toggleGap = () => {
  if (props.forceGap) return
  localShowGap.value = !localShowGap.value
}

// ✅ 有全局挖空时，全句强制挖空
const effectiveShowGap = computed(() => {
  return props.forceGap || localShowGap.value
})

// ✅ 显示的法语
const displayedFrench = computed(() => {
  const full = props.item.french_full
  const gap = props.item.french_gap

  if (effectiveShowGap.value) {
    return gap || full || ''
  }
  return full || gap || ''
})
</script>

<style scoped>
.sentence-card{
  background: #fff;
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,.06);
  border: 1px solid #eee;
}

.card-header{
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.left{
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.right{ display: flex; gap: 6px; }

.id{
  font-weight: 700;
  color: #2c3e50;
  background: #f5f7fb;
  padding: 2px 8px;
  border-radius: 8px;
}

.badge{
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #f2f2f2;
  color: #555;
}
.badge.source{ background: #eef6ff; color: #1b4d8f; }
.badge.level{ background: #fff3e6; color: #8a4b00; }
.badge.tag{ background: #f4f4ff; color: #3b3b8f; }

.mini-btn{
  border: 1px solid #ddd;
  background: #fafafa;
  padding: 4px 8px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
}
.mini-btn:hover{ background: #f0f0f0; }
.mini-btn:disabled{
  opacity: 0.6;
  cursor: not-allowed;
}

.label{
  font-size: 11px;
  color: #888;
  margin-bottom: 4px;
}
.text{
  font-size: 14px;
  color: #222;
  line-height: 1.5;
  white-space: pre-wrap;
}

.french{ margin-bottom: 10px; }
.chinese{
  background: #fbfbfb;
  border: 1px dashed #e5e5e5;
  padding: 8px 10px;
  border-radius: 8px;
  margin-bottom: 8px;
}

.detail summary{
  cursor: pointer;
  font-size: 12px;
  color: #666;
}
.explain{
  margin-top: 8px;
  display: grid;
  gap: 8px;
}
.block{
  background: #fafafa;
  border: 1px solid #eee;
  padding: 8px 10px;
  border-radius: 8px;
}
.vocab-list{
  margin: 0;
  padding-left: 16px;
}
</style>
