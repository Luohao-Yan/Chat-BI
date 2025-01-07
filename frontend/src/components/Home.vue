<template>
    <div class="container mx-auto p-4">
        <input v-model="inputValue" @input="updateChart" type="text" placeholder="请输入数据"
            class="border p-2 mb-4 w-full" />
        <div>
            <v-text-field :rules="rules" hide-details="auto" label="Main input"></v-text-field>
            <v-text-field label="Another input"></v-text-field>
        </div>
        <div ref="chart" class="w-full h-96"></div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';

const inputValue = ref('');
const chart = ref<HTMLElement | null>(null);
let myChart: echarts.ECharts | null = null;

const rules = [
    (value: string) => !!value || 'Required.',
    (value: string) => (value && value.length >= 3) || 'Min 3 characters',
];

const updateChart = () => {
    if (myChart) {
        const data = inputValue.value.split(',').map(Number);
        myChart.setOption({
            series: [
                {
                    data,
                    type: 'line',
                },
            ],
        });
    }
};

onMounted(() => {
    if (chart.value) {
        myChart = echarts.init(chart.value);
        myChart.setOption({
            xAxis: {
                type: 'category',
                data: ['A', 'B', 'C', 'D', 'E'],
            },
            yAxis: {
                type: 'value',
            },
            series: [
                {
                    data: [],
                    type: 'line',
                },
            ],
        });
    }
});
</script>

<style scoped>
.container {
    max-width: 800px;
}
</style>