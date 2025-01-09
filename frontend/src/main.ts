// src/main.ts
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import vuetify from './plugins/vuetify';
import '@mdi/font/css/materialdesignicons.css'; // 导入 mdi 图标库
import './main.css'; // 导入 Tailwind CSS

// 引入 ECharts 所需模块
import * as echarts from 'echarts/core';
import {
  BarChart,
  LineChart
} from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent
} from 'echarts/components';
import { LabelLayout, UniversalTransition } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';

// 注册必须的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  BarChart,
  LineChart,
  LabelLayout,
  UniversalTransition,
  CanvasRenderer
]);

const app = createApp(App)
  .use(router)
  .use(vuetify);

// 将 echarts 挂载到全局
app.config.globalProperties.$echarts = echarts;

app.mount('#app');