<!-- frontend/src/layouts/MainLayout.vue -->
<template>
  <v-app>
    <Sidebar />
    <Navbar />
    <v-main>
      <router-view />
    </v-main>
    <AppFooter />
  </v-app>
</template>

<script lang="ts" setup>
import { ref, provide } from 'vue'
import Sidebar from './Sidebar.vue'
import Navbar from './NavBar.vue'

const drawer = ref(true)
const toggleDrawer = () => {
  drawer.value = !drawer.value
}

provide('drawer', drawer)
provide('toggleDrawer', toggleDrawer)
</script>

<style scoped>
/* 响应式布局样式 */
@media (max-width: 600px) {
  .v-navigation-drawer {
    display: none;
  }
  .v-app-bar {
    position: fixed;
    top: 0;
    width: 100%;
  }
  .v-main {
    margin-top: 64px; /* Adjust based on the height of your app bar */
  }
}
</style>