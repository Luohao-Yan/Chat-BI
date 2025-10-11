<template>
  <div
    class="chat-input-wrapper"
    :class="{ 'focused': isFocused }"
    @focusin="isFocused = true"
    @focusout="isFocused = false">

    <!-- 输入区域 -->
    <div class="input-section">
      <textarea
        ref="textareaRef"
        v-model="localValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :rows="rows"
        class="input-area"
        @keydown.enter.exact.prevent="handleSend"
        @keydown.enter.shift.exact="handleNewLine"
        @input="autoResize"
      ></textarea>
    </div>

    <!-- 功能按钮区域 -->
    <div class="action-bar">
      <v-btn
        icon
        size="small"
        variant="plain"
        class="action-btn">
        <v-icon>mdi-paperclip</v-icon>
      </v-btn>

      <div class="spacer"></div>

      <v-icon
        v-if="localValue"
        class="clear-icon"
        @click="handleClear">
        mdi-close-circle
      </v-icon>

      <v-btn
        icon
        size="small"
        color="primary"
        :disabled="disabled || !localValue"
        class="send-btn"
        @click="handleSend">
        <v-icon>mdi-arrow-up</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'

interface Props {
  modelValue: string
  disabled?: boolean
  rows?: number
  placeholder?: string
  maxRows?: number
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'send'): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  rows: 1,
  placeholder: '请输入问题',
  maxRows: 6
})

const emit = defineEmits<Emits>()

const isFocused = ref(false)
const textareaRef = ref<HTMLTextAreaElement>()

const localValue = computed({
  get: () => props.modelValue,
  set: (value: string) => emit('update:modelValue', value)
})

const handleSend = () => {
  if (!props.disabled && localValue.value) {
    emit('send')
  }
}

const handleClear = () => {
  localValue.value = ''
  nextTick(() => {
    autoResize()
    textareaRef.value?.focus()
  })
}

const handleNewLine = () => {
  const textarea = textareaRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const value = localValue.value

  localValue.value = value.substring(0, start) + '\n' + value.substring(end)

  nextTick(() => {
    textarea.selectionStart = textarea.selectionEnd = start + 1
    autoResize()
  })
}

const autoResize = () => {
  const textarea = textareaRef.value
  if (!textarea) return

  // 重置高度以获取正确的 scrollHeight
  textarea.style.height = 'auto'

  // 计算最大高度
  const lineHeight = parseInt(getComputedStyle(textarea).lineHeight)
  const maxHeight = lineHeight * props.maxRows

  // 设置新高度
  const newHeight = Math.min(textarea.scrollHeight, maxHeight)
  textarea.style.height = `${newHeight}px`
}

watch(() => props.modelValue, () => {
  nextTick(autoResize)
})

onMounted(() => {
  autoResize()
})
</script>

<style scoped>
.chat-input-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 1px solid currentColor;
  border-radius: 1.5rem;
  opacity: 0.5;
  transition: all 0.2s;
}

.chat-input-wrapper.focused {
  opacity: 1;
}

.input-section {
  width: 100%;
}

.input-area {
  width: 100%;
  min-height: 1.5rem;
  padding: 0;
  border: none;
  outline: none;
  background: transparent;
  resize: none;
  font-family: inherit;
  font-size: 0.875rem;
  line-height: 1.5rem;
  overflow-y: auto;
}

.input-area:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-btn {
  flex-shrink: 0;
}

.spacer {
  flex: 1;
}

.clear-icon {
  flex-shrink: 0;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.clear-icon:hover {
  opacity: 1;
}

.send-btn {
  flex-shrink: 0;
}
</style>
