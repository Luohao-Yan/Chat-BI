<template>
  <div class="home-container">
    <!-- 初始状态 - 欢迎页面居中 -->
    <div v-if="!hasData && !isLoading && !hasStartedChat" class="initial-view">
      <div class="initial-content">
        <!-- 欢迎卡片 -->
        <v-card title="欢迎使用Chat BI" subtitle="This is Luohao Lab!"
          text="Chat BI 是一个强大的商业智能工具，帮助您轻松分析数据，生成报告，并提供深刻的业务洞察。通过简单的自然语言输入，您可以快速获取所需的信息，提升决策效率。">
          <template v-slot:prepend>
            <v-icon color="primary" size="large">mdi-message-text</v-icon>
          </template>
        </v-card>

        <!-- 初始输入框 - 居中显示 -->
        <ChatInput v-model="inputValue" :disabled="isLoading" :rows="1" @send="sendRequest" />
      </div>
    </div>

    <!-- 对话状态 - 内容区域可滚动 + 输入框固定底部 -->
    <template v-else>
      <!-- 内容区域 - 可滚动 -->
      <div class="content-area" ref="contentArea">
        <div class="content-wrapper">
          <v-skeleton-loader v-if="isLoading" type="card" class="my-8"></v-skeleton-loader>
          <div v-else class="messages-list">
            <!-- 用户消息气泡 -->
            <div class="message-item user-message">
              <div class="user-bubble">
                <p class="text-sm">{{ inputValue }}</p>
              </div>
            </div>

            <!-- AI 响应区域 -->
            <div class="message-item ai-message">
              <!-- 响应时间 -->
              <div v-if="responseTime" class="response-time">
                <v-icon size="16">mdi-clock-outline</v-icon>
                <span>{{ (responseTime / 1000).toFixed(1) }}s</span>
              </div>

              <!-- 图表展示 -->
              <v-card v-if="hasData" class="mb-4">
                <v-card-text>
                  <EChart :options="chartOptions" :loading="isLoading" v-model="chartType" class="chart" />
                </v-card-text>
              </v-card>

              <!-- 洞察分析 -->
              <v-card v-if="streamingAnalysis || insightAnalysis" class="mb-4">
                <v-card-text>
                  <div class="prose dark:prose-invert max-w-none">
                    <MarkdownRenderer v-if="streamingAnalysis" :content="streamingAnalysis" />
                    <MarkdownRenderer v-else-if="insightAnalysis" :content="insightAnalysis" />
                  </div>
                </v-card-text>
              </v-card>

              <!-- 加载状态 -->
              <div v-if="isAnalysisLoading && !streamingAnalysis" class="loading-state">
                <v-progress-circular indeterminate color="primary" size="40"></v-progress-circular>
                <p class="mt-4 text-body-2 text-medium-emphasis">AI正在分析数据...</p>
              </div>

              <!-- 操作按钮 -->
              <div class="action-bar">
                <v-btn icon size="small" variant="text">
                  <v-icon size="18">mdi-refresh</v-icon>
                </v-btn>
                <v-btn icon size="small" variant="text">
                  <v-icon size="18">mdi-content-copy</v-icon>
                </v-btn>
                <v-btn icon size="small" variant="text">
                  <v-icon size="18">mdi-thumb-up-outline</v-icon>
                </v-btn>
                <v-btn icon size="small" variant="text">
                  <v-icon size="18">mdi-thumb-down-outline</v-icon>
                </v-btn>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 - 固定在底部 -->
      <div class="input-bar">
        <div class="input-wrapper">
          <ChatInput v-model="inputValue" :disabled="isLoading" :rows="2" @send="sendRequest" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import EChart from './EChart.vue'
import MarkdownRenderer from './MarkdownRenderer.vue'
import ChatInput from './ChatInput.vue'

const inputValue = ref('')
const hasData = ref(false)
const isLoading = ref(false)
const hasStartedChat = ref(false)
const chartOptions = ref({})
const chartType = ref<'bar' | 'line' | 'pie' | 'doughnut'>('bar')
const responseTime = ref<number | null>(null)
const insightAnalysis = ref<string | null>(null)
const streamingAnalysis = ref<string>('')
const isAnalysisLoading = ref(false)
const isAnalysisComplete = ref(false)

interface RefinedData {
  x_axis: string
  y_axes: string[]
  scale: string
  unit: string
}

const sendRequest = async () => {
  if (!inputValue.value) {
    alert('请输入问题')
    return
  }

  // 标记对话已开始
  hasStartedChat.value = true

  // 重置所有状态
  isLoading.value = true
  hasData.value = false
  responseTime.value = null
  insightAnalysis.value = null
  streamingAnalysis.value = ''
  isAnalysisLoading.value = false
  isAnalysisComplete.value = false

  const startTime = performance.now()

  try {
    const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/generate_chart`, {
      user_input: inputValue.value,
    })
    console.log('Response:', response.data)

    const { data, refined_data, chart_type } = response.data

    if (data && data.length > 0) {
      hasData.value = true

      const refinedData = refined_data as RefinedData
      console.log('Refined Data:', refinedData)

      const xAxisData = data.map((item: any) => item[refinedData.x_axis])
      console.log('xAxisData:', xAxisData)

      const seriesData = refined_data.y_axes.map((yAxis: string) => {
        return {
          name: yAxis,
          type: chart_type,
          data: data.map((item: any) => item[yAxis]),
          stack: chart_type === 'bar' ? 'x' : undefined,
          areaStyle: chart_type === 'line' ? {} : undefined
        }
      })
      console.log('Series Data:', seriesData)

      chartOptions.value = {
        xAxis: {
          type: 'category',
          data: xAxisData,
        },
        yAxis: {
          type: 'value',
        },
        series: seriesData,
        legend: {
          data: refined_data.y_axes
        },
        tooltip: {
          trigger: 'axis'
        }
      }
      chartType.value = chart_type
      console.log('Chart Options:', chartOptions.value)
      console.log('Chart Type:', chartType.value)

      // 开始流式洞察分析
      fetchStreamingInsightAnalysis()
    } else {
      hasData.value = false
      console.warn('未获取到图表数据')
    }
  } catch (error: any) {
    console.error('请求失败', error)
    hasData.value = false

    const errorMessage = error.response?.data?.message || error.message || '请求失败，请稍后重试'
    alert(`生成图表失败: ${errorMessage}`)

  } finally {
    const endTime = performance.now()
    responseTime.value = Math.round(endTime - startTime)
    isLoading.value = false
  }
}

const fetchInsightAnalysis = async () => {
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/insight_analysis`, {
      params: { user_input: inputValue.value }
    })
    insightAnalysis.value = response.data.insight_analysis
  } catch (error) {
    console.error('获取洞察分析失败', error)
  }
}

const fetchStreamingInsightAnalysis = async () => {
  if (!inputValue.value) return

  streamingAnalysis.value = ''
  insightAnalysis.value = null
  isAnalysisLoading.value = true
  isAnalysisComplete.value = false

  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/insight_analysis_stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_input: inputValue.value,
        data: JSON.stringify({
          chartData: chartOptions.value,
          userQuestion: inputValue.value,
          timestamp: new Date().toISOString()
        })
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    if (!response.body) {
      throw new Error('Response body is null')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        isAnalysisComplete.value = true
        isAnalysisLoading.value = false
        break
      }

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            if (data.content) {
              streamingAnalysis.value += data.content
            } else if (data.done) {
              isAnalysisComplete.value = true
              isAnalysisLoading.value = false
            } else if (data.error) {
              console.error('流式分析错误:', data.error)
              isAnalysisComplete.value = true
              isAnalysisLoading.value = false
              streamingAnalysis.value += '\n\n出现错误，正在尝试获取缓存的分析结果...'
              setTimeout(fetchInsightAnalysis, 1000)
              break
            }
          } catch (e) {
            console.debug('解析流数据出错:', e)
          }
        }
      }
    }

  } catch (error) {
    console.error('流式洞察分析失败:', error)
    isAnalysisComplete.value = true
    isAnalysisLoading.value = false
    streamingAnalysis.value = ''
    fetchInsightAnalysis()
  }
}
</script>

<style scoped>
/* 主容器 - 占满父元素 */
.home-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 初始状态视图 - 垂直水平居中 */
.initial-view {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  overflow-y: auto;
}

.initial-content {
  width: 100%;
  max-width: 48rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 对话视图 - 内容区 + 输入框 */
.content-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.content-wrapper {
  width: 100%;
  max-width: 64rem;
  margin: 0 auto;
  padding: 2rem 1rem;
  padding-top: 5rem; /* 增加顶部 padding 避开 app-bar (64px 高度 + 额外空间) */
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.message-item {
  width: 100%;
}

/* 用户消息 - 右对齐 */
.user-message {
  display: flex;
  justify-content: flex-end;
}

.user-bubble {
  max-width: 80%;
  padding: 0.75rem 1.25rem;
  background-color: rgb(var(--v-theme-primary));
  color: rgb(var(--v-theme-on-primary));
  border-radius: 1rem;
  border-top-right-radius: 0.125rem;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  box-sizing: border-box;
}

.user-bubble p {
  margin: 0;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
}

/* AI消息 - 左对齐 */
.ai-message {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.response-time {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  opacity: 0.6;
}

.chart {
  width: 100%;
  height: 24rem;
}

.loading-state {
  text-align: center;
  padding: 2rem 0;
}

.action-bar {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* 输入框区域 - 固定底部 */
.input-bar {
  flex-shrink: 0;
  background-color: rgb(var(--v-theme-background));
  padding: 1rem;
}

.input-wrapper {
  width: 100%;
  max-width: 64rem;
  margin: 0 auto;
}

/* 响应式 */
@media (min-width: 640px) {
  .initial-view {
    padding: 3rem 2rem;
  }

  .content-wrapper {
    padding: 2rem 2rem;
    padding-top: 5rem; /* 保持顶部 padding */
  }
}
</style>
