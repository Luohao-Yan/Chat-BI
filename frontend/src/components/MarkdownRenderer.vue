<template>
  <div class="markdown-content">
    <div v-html="renderedMarkdown" class="markdown-body"></div>
    <div v-if="streaming && showCursor" class="streaming-cursor">▊</div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { marked } from 'marked'

const props = defineProps<{
  content: string
  streaming?: boolean
}>()

const showCursor = ref(true)

// 配置marked选项
marked.setOptions({
  breaks: true,
  gfm: true,
})

const renderedMarkdown = computed(() => {
  if (!props.content) return ''
  
  try {
    return marked(props.content)
  } catch (error) {
    console.error('Markdown rendering error:', error)
    return `<p>${props.content}</p>`
  }
})

// 流式模式下的光标闪烁
watch(() => props.streaming, (newVal) => {
  if (newVal) {
    const interval = setInterval(() => {
      showCursor.value = !showCursor.value
    }, 500)
    
    watch(() => props.streaming, (streaming) => {
      if (!streaming) {
        clearInterval(interval)
        showCursor.value = false
      }
    })
  }
})
</script>

<style scoped>
.markdown-content {
  position: relative;
}

.markdown-body {
  line-height: 1.6;
  color: #24292f;
  font-size: 14px;
}

.streaming-cursor {
  display: inline-block;
  color: #1976d2;
  font-weight: bold;
  animation: pulse 1s infinite;
  margin-left: 2px;
}

@keyframes pulse {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* Markdown样式 */
.markdown-body :deep(h1) {
  font-size: 1.8rem;
  font-weight: 600;
  margin: 1.5rem 0 1rem 0;
  color: #1976d2;
  border-bottom: 2px solid #e3f2fd;
  padding-bottom: 0.5rem;
}

.markdown-body :deep(h2) {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 1.25rem 0 0.75rem 0;
  color: #1976d2;
  display: flex;
  align-items: center;
}

.markdown-body :deep(h3) {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 1rem 0 0.5rem 0;
  color: #424242;
}

.markdown-body :deep(p) {
  margin: 0.75rem 0;
  line-height: 1.7;
}

.markdown-body :deep(ul) {
  margin: 0.75rem 0;
  padding-left: 1.5rem;
}

.markdown-body :deep(li) {
  margin: 0.25rem 0;
  line-height: 1.6;
}

.markdown-body :deep(strong) {
  font-weight: 600;
  color: #1976d2;
}

.markdown-body :deep(blockquote) {
  margin: 1rem 0;
  padding: 0.75rem 1rem;
  background: linear-gradient(90deg, #e3f2fd 0%, #f5f5f5 100%);
  border-left: 4px solid #1976d2;
  border-radius: 4px;
  font-style: italic;
  color: #424242;
}

.markdown-body :deep(blockquote p) {
  margin: 0;
}

.markdown-body :deep(code) {
  background: #f5f5f5;
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.9em;
  color: #d32f2f;
}

.markdown-body :deep(pre) {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem;
  margin: 1rem 0;
  overflow-x: auto;
}

.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
  color: #24292f;
}

/* 序号列表样式 */
.markdown-body :deep(ol) {
  margin: 0.75rem 0;
  padding-left: 1.5rem;
  counter-reset: item;
}

.markdown-body :deep(ol li) {
  margin: 0.5rem 0;
  line-height: 1.6;
  position: relative;
}

.markdown-body :deep(ol li strong) {
  color: #1976d2;
}

/* 表格样式 */
.markdown-body :deep(table) {
  border-collapse: collapse;
  margin: 1rem 0;
  width: 100%;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #e0e0e0;
  padding: 0.75rem;
  text-align: left;
}

.markdown-body :deep(th) {
  background: #f5f5f5;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .markdown-body {
    font-size: 13px;
  }
  
  .markdown-body :deep(h1) {
    font-size: 1.5rem;
  }
  
  .markdown-body :deep(h2) {
    font-size: 1.3rem;
  }
  
  .markdown-body :deep(h3) {
    font-size: 1.1rem;
  }
}
</style>