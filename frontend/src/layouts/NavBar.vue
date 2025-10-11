<template>
  <v-app-bar app>
    <v-btn icon @click="toggleMiniVariant">
      <v-icon>mdi-menu</v-icon>
    </v-btn>
    <v-toolbar-title>Chat BI Lab</v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn icon @click="toggleTheme">
      <v-icon>{{ themeStore.isDark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
    </v-btn>
  </v-app-bar>
</template>

<script lang="ts" setup>
import { inject, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import {
  VAppBar,
  VBtn,
  VIcon,
  VToolbarTitle,
  VSpacer,
} from 'vuetify/components'

const toggleMiniVariant = inject('toggleMiniVariant')
const themeStore = useThemeStore()

// 初始化主题
onMounted(() => {
  themeStore.initTheme()
})

const toggleTheme = () => {
  themeStore.toggleTheme()
}
</script>