<template>
  <div class="container mx-auto p-4 flex items-center justify-center gap-2">
    <v-card class="mx-auto" prepend-icon="mdi-message-text" subtitle="This is Luohao Lab!" width="100%">
      <template v-slot:title>
        <span class="font-weight-black">欢迎使用Chat BI</span>
      </template>

      <v-card-text class="bg-surface-light pt-4">
        Chat BI 是一个强大的商业智能工具，帮助您轻松分析数据，生成报告，并提供深刻的业务洞察。通过简单的自然语言输入，您可以快速获取所需的信息，提升决策效率。
      </v-card-text>
    </v-card>
    <div class="w-full max-w-md">
      <v-textarea :model-value="inputValue" label="请输入问题" clearable outlined dense class="flex-1" :loading="isLoading"
        :rules="rules" counter @update:model-value="updateInputValue">
        <template v-slot:append-inner>
          <v-btn rounded="lg" @click="sendRequest" :disabled="isLoading">
            <v-icon>mdi-send</v-icon>
          </v-btn>
        </template>
      </v-textarea>
      <v-skeleton-loader v-if="isLoading" type="card" class="w-full h-96 mt-4"></v-skeleton-loader>
      <div v-else>
        <EChart v-if="hasData" :options="chartOptions" :loading="isLoading" v-model="chartType"
          class="chart-container w-full h-96 mt-4" />
        <!-- 流式洞察分析 -->
        <v-card v-if="isAnalysisLoading || streamingAnalysis || insightAnalysis" class="mt-2">
          <v-card-title class="d-flex align-center">
            <span>洞察分析</span>
            <v-spacer></v-spacer>
            <v-progress-circular 
              v-if="isAnalysisLoading && !isAnalysisComplete" 
              indeterminate 
              size="20" 
              width="2"
              color="primary"
            ></v-progress-circular>
          </v-card-title>
          <v-card-text class="pa-0">
            <transition-group name="analysis" tag="div" mode="out-in">
              <!-- 流式分析内容 -->
              <div v-if="streamingAnalysis" key="streaming" class="streaming-analysis">
                <MarkdownRenderer 
                  :content="streamingAnalysis" 
                  :streaming="isAnalysisLoading && !isAnalysisComplete" 
                />
              </div>
              <!-- 最终分析结果 -->
              <div v-else-if="insightAnalysis" key="final" class="final-analysis">
                <MarkdownRenderer :content="insightAnalysis" />
              </div>
              <!-- 加载状态 -->
              <div v-else-if="isAnalysisLoading" key="loading" class="text-center py-8">
                <v-progress-circular indeterminate color="primary" size="40"></v-progress-circular>
                <p class="mt-4 text-body-1 text-grey-600">🤖 AI正在分析数据...</p>
                <p class="text-body-2 text-grey-500">请稍候，精彩洞察即将呈现</p>
              </div>
            </transition-group>
          </v-card-text>
        </v-card>
        <v-card v-if="responseTime" class="text-center mt-2">
          <v-card-title>
            请求总时间: {{ responseTime }} 毫秒
          </v-card-title>
        </v-card>
        <v-skeleton-loader v-else type="card" class="w-full h-96 mt-4">
          <template v-slot:default>
            <v-card class="mx-auto" width="100%">
              <v-card-text class="bg-surface-light pt-4">
                暂无数据
              </v-card-text>
            </v-card>
          </template>
        </v-skeleton-loader>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import '@mdi/font/css/materialdesignicons.css'
import { VSkeletonLoader } from 'vuetify/components'
import EChart from './EChart.vue'

const inputValue = ref('')
const hasData = ref(false)
const isLoading = ref(false)
const chartOptions = ref({})
const chartType = ref<'bar' | 'line' | 'pie' | 'doughnut'>('bar')
const responseTime = ref<number | null>(null)
const insightAnalysis = ref<string | null>(null)
const streamingAnalysis = ref<string>('')
const isAnalysisLoading = ref(false)
const isAnalysisComplete = ref(false)
const rules = [(v: string) => v.length <= 25 || 'Max 25 characters']

interface RefinedData {
  x_axis: string
  y_axes: string[]
  scale: string
  unit: string
}

const updateInputValue = (value: string) => {
  inputValue.value = value
}

const sendRequest = async () => {
  if (!inputValue.value) {
    alert('请输入问题')
    return
  }

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

      const seriesData = refinedData.y_axes.map((yAxis: string) => {
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
          data: refinedData.y_axes
        },
        tooltip: {
          trigger: 'axis'
        }
      }
      chartType.value = chart_type // 设置图表类型
      console.log('Chart Options:', chartOptions.value)
      console.log('Chart Type:', chartType.value)

      // 开始流式洞察分析
      fetchStreamingInsightAnalysis()
    } else {
      hasData.value = false
      // 显示友好的无数据消息
      console.warn('未获取到图表数据')
    }
  } catch (error: any) {
    console.error('请求失败', error)
    hasData.value = false
    
    // 显示错误信息给用户
    const errorMessage = error.response?.data?.message || error.message || '请求失败，请稍后重试'
    alert(`生成图表失败: ${errorMessage}`)
    
  } finally {
    const endTime = performance.now()
    responseTime.value = endTime - startTime
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
  
  // 重置状态
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
              // 回退到传统方式
              setTimeout(fetchInsightAnalysis, 1000)
              break
            }
          } catch (e) {
            // 忽略JSON解析错误，继续处理下一行
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
    
    // 回退到传统方式
    fetchInsightAnalysis()
  }
}


</script>

<style scoped>
.container {
  max-width: 1200px;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.streaming-content {
  position: relative;
}

.cursor {
  display: inline-block;
  background-color: #1976d2;
  color: white;
  padding: 0 2px;
  margin-left: 2px;
  animation: blink 1s infinite;
  font-family: monospace;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.text-body-2 {
  color: rgba(0, 0, 0, 0.6);
}

.streaming-analysis {
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
  border-radius: 8px;
  min-height: 100px;
}

.final-analysis {
  padding: 1rem;
  background: #ffffff;
  border-radius: 8px;
}

/* 洞察分析卡片样式 */
.v-card:has(.streaming-analysis),
.v-card:has(.final-analysis) {
  border: 1px solid #e3f2fd;
  box-shadow: 0 2px 12px rgba(25, 118, 210, 0.08);
  transition: all 0.3s ease;
}

.v-card:has(.streaming-analysis):hover,
.v-card:has(.final-analysis):hover {
  box-shadow: 0 4px 20px rgba(25, 118, 210, 0.12);
  transform: translateY(-2px);
}

/* 流式分析特效 */
.streaming-analysis {
  position: relative;
  overflow: hidden;
}

.streaming-analysis::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #1976d2, transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

/* 过渡动画 */
.analysis-enter-active,
.analysis-leave-active {
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.analysis-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.analysis-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(1.02);
}

.analysis-enter-to,
.analysis-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

/* 响应式优化 */
@media (max-width: 768px) {
  .streaming-analysis,
  .final-analysis {
    padding: 0.75rem;
    margin: 0.5rem;
  }
  
  .v-card-title {
    font-size: 1.1rem;
    padding: 0.75rem 1rem;
  }
}
</style>