<template>
    <div class="chart-container relative">
        <div class="settings-bar absolute top-0 left-0 w-full flex justify-end p-2 bg-white shadow-md">
            <v-btn icon @click="setChartType('line')">
                <v-icon>mdi-chart-line</v-icon>
            </v-btn>
            <v-btn icon @click="setChartType('bar')">
                <v-icon>mdi-chart-bar</v-icon>
            </v-btn>
            <v-btn icon @click="setChartType('pie')">
                <v-icon>mdi-chart-pie</v-icon>
            </v-btn>
            <v-btn icon @click="setChartType('doughnut')">
                <v-icon>mdi-chart-donut</v-icon>
            </v-btn>
        </div>
        <div v-if="chartReady" ref="chart" class="chart-container mt-12"></div>
    </div>
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
const chartType = ref<'bar' | 'line' | 'pie' | 'doughnut'>('bar')
const chartReady = ref(false)

const initChart = async () => {
    if (chart.value) {
        console.log('Initializing chart with element:', chart.value)
        await nextTick()
        myChart = echarts.init(chart.value)
        console.log('ECharts instance created:', myChart)
        updateChartOptions()
        window.addEventListener('resize', resizeChart)
    } else {
        console.log('Chart element is not ready')
    }
}

const resizeChart = () => {
    if (myChart) {
        console.log('Resizing chart')
        myChart.resize()
    }
}

const updateChartOptions = () => {
    if (myChart) {
        console.log('Updating chart options with type:', chartType.value)
        const updatedOptions = {
            ...props.options,
            series: (props.options.series as echarts.SeriesOption[])?.map((series: any) => ({
                ...series,
                type: chartType.value === 'doughnut' ? 'pie' : chartType.value,
                ...(chartType.value === 'pie' || chartType.value === 'doughnut' ? {
                    label: {
                        show: true,
                        position: 'outside',
                        formatter: '{b} {d}%', // 显示标签和百分比
                    },
                    labelLine: {
                        show: true
                    },
                    radius: chartType.value === 'doughnut' ? ['40%', '70%'] : '50%', // 设置饼图和环形图的大小
                } : {}),
            })),
            ...(chartType.value !== 'pie' && chartType.value !== 'doughnut' ? {
                dataZoom: [
                    {
                        type: 'slider',
                        show: true,
                        xAxisIndex: [0],
                        start: 0,
                        end: 100,
                    },
                ],
                grid: {
                    left: '10%',
                    right: '10%',
                    bottom: '15%',
                    top: '15%',
                    containLabel: true,
                },
            } : {}),
            ...(chartType.value === 'pie' || chartType.value === 'doughnut' ? {
                xAxis: undefined,
                yAxis: undefined,
                grid: undefined, // 移除 grid 配置
                dataZoom: undefined, // 移除 dataZoom 配置
            } : {}),
        }
        console.log('Setting chart options:', updatedOptions)
        myChart.setOption(updatedOptions)
    } else {
        console.log('ECharts instance is not ready')
    }
}

const setChartType = (type: 'bar' | 'line' | 'pie' | 'doughnut') => {
    chartType.value = type
    updateChartOptions()
}

onMounted(() => {
    console.log('Component mounted')
    chartReady.value = true
    initChart()
})

onBeforeUnmount(() => {
    if (myChart) {
        console.log('Disposing chart')
        myChart.dispose()
    }
    window.removeEventListener('resize', resizeChart)
})

watch(
    () => props.options,
    (newOptions) => {
        console.log('Options changed:', newOptions)
        if (myChart) {
            updateChartOptions()
        }
    },
    { deep: true }
)

watch(
    () => props.loading,
    (newLoading) => {
        console.log('Loading state changed:', newLoading)
        if (myChart) {
            if (newLoading) {
                myChart.showLoading()
            } else {
                myChart.hideLoading()
            }
        }
    }
)

// 监听 chartReady 和 chart 元素的变化
watch(
    () => chartReady.value,
    (newReady) => {
        console.log('Chart ready state changed:', newReady)
        if (newReady && chart.value) {
            initChart()
        }
    }
)

watch(
    () => chart.value,
    (newChart) => {
        console.log('Chart element changed:', newChart)
        if (newChart) {
            initChart()
        }
    }
)

// 监听 chart 元素的尺寸变化
watch(
    () => chart.value?.clientWidth,
    (newWidth) => {
        console.log('Chart element width changed:', newWidth)
        if (newWidth && newWidth > 0) {
            initChart()
        }
    }
)

watch(
    () => chart.value?.clientHeight,
    (newHeight) => {
        console.log('Chart element height changed:', newHeight)
        if (newHeight && newHeight > 0) {
            initChart()
        }
    }
)
</script>

<style scoped>
.chart-container {
    width: 100%;
    height: 100%;
    position: relative;
}

.settings-bar {
    top: 0;
    left: 0;
    width: 100%;
    display: flex;
    justify-content: flex-end;
    z-index: 10;
}

.chart-container .v-btn {
    margin-left: 8px;
}

@media (min-width: 768px) {
    .chart-container .v-btn {
        margin-left: 16px;
    }

    .chart-container {
        height: 500px;
        /* 确保在大屏幕上有足够的高度 */
    }
}

@media (max-width: 768px) {
    .chart-container {
        height: 300px;
    }
}
</style>