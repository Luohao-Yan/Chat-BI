<template>
  <v-navigation-drawer v-model="drawer" app :mini-variant="miniVariant">
    <!-- 侧边栏内容 -->
    <v-list>
      <v-list-item link>
        <template v-slot:prepend>
          <v-icon>mdi-home</v-icon>
        </template>
        <v-list-item-title>Home</v-list-item-title>
      </v-list-item>
      <!-- 其他侧边栏项 -->
    </v-list>
  </v-navigation-drawer>
</template>

<script lang="ts" setup>
import { inject } from 'vue'
import {
  VNavigationDrawer,
  VList,
  VListItem,
  VListItemTitle,
  VIcon,
} from 'vuetify/components'

// 指定 drawer 和 miniVariant 的类型
const drawer = inject<boolean | null | undefined>('drawer')
const miniVariant = inject<boolean>('miniVariant')
</script>

<style scoped>
/* 响应式布局样式 */
@media (max-width: 600px) {
  .v-navigation-drawer {
    display: none;
  }
}
</style>
