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
          <v-textarea :model-value="inputValue" label="请输入问题" clearable outlined dense class="flex-1"
              :loading="isLoading" :rules="rules" counter @update:model-value="updateInputValue">
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
const chartOptions = ref<echarts.EChartsOption>({})
const chartType = ref<'bar' | 'line' | 'pie' | 'doughnut'>('bar')
const responseTime = ref<number | null>(null)
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

  isLoading.value = true
  responseTime.value = null
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
      } else {
          hasData.value = false
      }
  } catch (error) {
      console.error('请求失败', error)
  } finally {
      const endTime = performance.now()
      responseTime.value = endTime - startTime
      isLoading.value = false
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
</style>