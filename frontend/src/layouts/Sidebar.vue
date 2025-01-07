<!-- frontend/src/layouts/Sidebar.vue -->
<template>
    <v-navigation-drawer v-model="drawer" app>
      <!-- 侧边栏内容 -->
      <v-list>
        <v-list-item link>
          <v-list-item-icon>
            <v-icon>mdi-home</v-icon>
          </v-list-item-icon>
          <v-list-item-title>Home</v-list-item-title>
        </v-list-item>
        <!-- 其他侧边栏项 -->
      </v-list>
    </v-navigation-drawer>
  </template>
  
  <script lang="ts" setup>
  import { inject } from 'vue'
  import { VNavigationDrawer, VList, VListItem, VListItemTitle, VIcon } from 'vuetify/components'
  
  // 指定 drawer 的类型为 boolean | null | undefined
  const drawer = inject<boolean | null | undefined>('drawer')
  </script>

  <style scoped>
  /* 响应式布局样式 */
  @media (max-width: 600px) {
    .v-navigation-drawer {
      display: none;
    }
  }
  </style>