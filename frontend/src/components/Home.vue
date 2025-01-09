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
        <v-text-field v-model="inputValue" label="请输入问题" outlined dense class="flex-1" :loading="isLoading">
          <template v-slot:append-inner>
            <v-btn rounded="lg" @click="sendRequest" :disabled="isLoading">
              <v-icon>mdi-send</v-icon>
            </v-btn>
          </template>
        </v-text-field>
        <v-skeleton-loader v-if="isLoading" type="card" class="w-full h-96 mt-4"></v-skeleton-loader>
        <div v-else>
          <EChart v-if="hasData" :options="chartOptions" :loading="isLoading" class="chart-container w-full h-96 mt-4" />
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
  
    isLoading.value = true
  
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/generate_chart`, {
        user_input: inputValue.value,
      })
      console.log('Response:', response.data) // 添加日志，查看后端返回的数据
  
      const { data, refined_data, chart_type } = response.data
  
      if (data && data.length > 0) {
        hasData.value = true
  
        const refinedData = refined_data as RefinedData
        console.log('Refined Data:', refinedData) // 添加日志，查看 refined_data
  
        const xAxisData = data.map((item: any) => item[refinedData.x_axis])
        console.log('xAxisData:', xAxisData) // 添加日志，查看 xAxisData
  
        const seriesData = refinedData.y_axes.map((yAxis: string) => {
          return {
            name: yAxis,
            type: chart_type,
            data: data.map((item: any) => item[yAxis]),
            stack: chart_type === 'bar' ? 'x' : undefined, // 确保堆叠仅在柱状图时使用
            areaStyle: chart_type === 'line' ? {} : undefined // 确保区域样式仅在折线图时使用
          }
        })
        console.log('Series Data:', seriesData) // 添加日志，查看 seriesData
  
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
      } else {
        hasData.value = false
      }
    } catch (error) {
      console.error('请求失败', error)
    } finally {
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
    height: 400px;
  }
  </style>