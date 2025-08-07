<template>
  <v-app-bar app>
    <v-btn icon @click="toggleDrawer">
      <v-icon>mdi-menu</v-icon>
    </v-btn>
    <v-toolbar-title>Chat BI Lab</v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn icon @click="toggleTheme">
      <v-icon>{{ isDarkTheme ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
    </v-btn>
    <v-menu>
      <template #activator="{ props }">
        <v-btn icon v-bind="props">
          <v-icon>mdi-dots-vertical</v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item link>
          <template v-slot:prepend>
            <v-icon>mdi-home</v-icon>
          </template>
          <v-list-item-title>Home</v-list-item-title>
        </v-list-item>
        <v-list-item link>
          <template v-slot:prepend>
            <v-icon>mdi-information</v-icon>
          </template>
          <v-list-item-title>About</v-list-item-title>
        </v-list-item>
        <v-list-item link>
          <template v-slot:prepend>
            <v-icon>mdi-mail</v-icon>
          </template>
          <v-list-item-title>Contact</v-list-item-title>
        </v-list-item>
        <v-divider></v-divider>
        <v-list-item link @click="showAIConfig">
          <template v-slot:prepend>
            <v-icon>mdi-robot</v-icon>
          </template>
          <v-list-item-title>AI模型配置</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>

  <!-- AI配置对话框 -->
  <v-dialog v-model="aiConfigDialog" max-width="900px" persistent>
    <v-card>
      <v-card-title class="d-flex align-center">
        <span>AI模型配置</span>
        <v-spacer></v-spacer>
        <v-btn icon @click="aiConfigDialog = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <AIModelConfig @close="aiConfigDialog = false" />
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script lang="ts" setup>
import { inject, computed, ref } from 'vue'
import { useTheme } from 'vuetify'
import {
  VAppBar,
  VBtn,
  VIcon,
  VToolbarTitle,
  VSpacer,
  VMenu,
  VList,
  VListItem,
  VListItemTitle,
  VDialog,
  VCard,
  VCardTitle,
  VCardText,
  VDivider,
} from 'vuetify/components'
import AIModelConfig from '../components/AIModelConfig.vue'

const toggleDrawer = inject('toggleDrawer')

const theme = useTheme()
const isDarkTheme = computed(() => theme.global.name.value === 'darkTheme')
const aiConfigDialog = ref(false)

const toggleTheme = () => {
  theme.global.name.value = isDarkTheme.value ? 'lightTheme' : 'darkTheme'
}

const showAIConfig = () => {
  aiConfigDialog.value = true
}
</script>