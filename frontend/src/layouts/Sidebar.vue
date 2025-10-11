<template>
  <v-navigation-drawer
    v-model="drawer"
    app
    :rail="miniVariant"
    :permanent="true"
    :width="256"
  >
    <!-- Logo 区域 -->
    <div class="logo-section" :class="{ 'logo-section--rail': miniVariant }">
      <v-avatar :size="miniVariant ? 32 : 48" color="primary">
        <v-icon :size="miniVariant ? 20 : 32">mdi-chart-bar</v-icon>
      </v-avatar>
      <div v-if="!miniVariant" class="logo-text">
        <h3>Chat BI</h3>
        <p class="text-caption">Luohao Lab</p>
      </div>
    </div>

    <!-- 主菜单内容 -->
    <v-list class="flex-grow-1">
      <v-list-item link>
        <template v-slot:prepend>
          <v-icon>mdi-home</v-icon>
        </template>
        <v-list-item-title>Home</v-list-item-title>
      </v-list-item>

      <v-list-item link>
        <template v-slot:prepend>
          <v-icon>mdi-database-cog</v-icon>
        </template>
        <v-list-item-title>数据爬取源管理</v-list-item-title>
      </v-list-item>

      <v-list-item link>
        <template v-slot:prepend>
          <v-icon>mdi-table-eye</v-icon>
        </template>
        <v-list-item-title>数据爬取结果展示</v-list-item-title>
      </v-list-item>

      <v-list-item link @click="showAIConfig">
        <template v-slot:prepend>
          <v-icon>mdi-robot</v-icon>
        </template>
        <v-list-item-title>AI模型配置</v-list-item-title>
      </v-list-item>
    </v-list>

    <!-- 底部用户头像区域 -->
    <template v-slot:append>
      <div class="user-section">
        <v-list-item link>
          <template v-slot:prepend>
            <v-avatar color="primary" :size="miniVariant ? 32 : 40">
              <v-icon :size="miniVariant ? 20 : 24">mdi-account</v-icon>
            </v-avatar>
          </template>
          <v-list-item-title v-if="!miniVariant">用户</v-list-item-title>
          <v-list-item-subtitle v-if="!miniVariant" class="text-caption">admin@chatbi.com</v-list-item-subtitle>
        </v-list-item>
      </div>
    </template>
  </v-navigation-drawer>

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
import { inject, ref } from 'vue'
import {
  VNavigationDrawer,
  VList,
  VListItem,
  VListItemTitle,
  VListItemSubtitle,
  VIcon,
  VDivider,
  VDialog,
  VCard,
  VCardTitle,
  VCardText,
  VBtn,
  VSpacer,
  VAvatar,
} from 'vuetify/components'
import AIModelConfig from '../components/AIModelConfig.vue'

// 指定 drawer 和 miniVariant 的类型
const drawer = inject<boolean | null | undefined>('drawer')
const miniVariant = inject<boolean>('miniVariant')

const aiConfigDialog = ref(false)

const showAIConfig = () => {
  aiConfigDialog.value = true
}
</script>

<style scoped>
.logo-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1rem;
}

.logo-section--rail {
  justify-content: center;
  padding: 1rem;
}

.logo-text h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.2;
}

.logo-text p {
  margin: 0;
  opacity: 0.7;
}

.user-section {
  padding: 0.5rem 0;
}

/* 响应式布局样式 */
@media (max-width: 600px) {
  .v-navigation-drawer {
    display: none;
  }
}
</style>
