<template>
    <div ref="chart" class="chart-container"></div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
  import * as echarts from 'echarts'
  
  const props = defineProps<{
    options: echarts.EChartsOption
    loading: boolean
  }>()
  
  const chart = ref<HTMLElement | null>(null)
  let myChart: echarts.ECharts | null = null
  
  const initChart = async () => {
    if (chart.value) {
      await nextTick()
      myChart = echarts.init(chart.value)
      myChart.setOption(props.options)
    }
  }
  
  onMounted(() => {
    initChart()
    window.addEventListener('resize', () => {
      if (myChart) {
        myChart.resize()
      }
    })
  })
  
  onBeforeUnmount(() => {
    if (myChart) {
      myChart.dispose()
    }
    window.removeEventListener('resize', () => {
      if (myChart) {
        myChart.resize()
      }
    })
  })
  
  watch(
    () => props.options,
    (newOptions) => {
      if (myChart) {
        myChart.setOption(newOptions)
      }
    },
    { deep: true }
  )
  
  watch(
    () => props.loading,
    (newLoading) => {
      if (myChart) {
        if (newLoading) {
          myChart.showLoading()
        } else {
          myChart.hideLoading()
        }
      }
    }
  )
  </script>
  
  <style scoped>
  .chart-container {
    width: 100%;
    height: 100%;
  }
  </style>