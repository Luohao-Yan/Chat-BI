<template>
  <v-app>
    <Sidebar />
    <Navbar />
    <v-main class="main-content">
      <router-view />
    </v-main>
  </v-app>
</template>

<script lang="ts" setup>
import { provide, computed } from 'vue'
import { useAppStore } from '@/stores/app'
import Sidebar from './Sidebar.vue'
import Navbar from './NavBar.vue'

const appStore = useAppStore()

// 通过 computed 提供响应式的值给子组件
provide('drawer', computed(() => appStore.drawer))
provide('miniVariant', computed(() => appStore.miniVariant))
provide('toggleDrawer', () => appStore.toggleDrawer())
provide('toggleMiniVariant', () => appStore.toggleMiniVariant())
</script>

<style>
/* Vuetify 使用 app prop 自动处理布局，v-main 会自动获得正确的 margin */
/* 不要使用 !important 覆盖 Vuetify 的自动布局 */

.main-content {
  height: calc(100vh - 64px); /* 减去 app-bar 的高度 */
}

.main-content :deep(.v-main__wrap) {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0; /* 只移除内部 padding，但保留 Vuetify 为 drawer 添加的 margin */
}

/* 响应式布局样式 */
@media (max-width: 600px) {
  .v-navigation-drawer {
    display: none;
  }
}
</style>
