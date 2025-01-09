<template>
  <v-app-bar app>
    <v-btn icon @click="toggleDrawer">
      <v-icon>mdi-menu</v-icon>
    </v-btn>
    <v-toolbar-title>Chat BI Lab</v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn icon @click="toggleTheme">
      <v-icon>{{
        isDarkTheme ? 'mdi-weather-sunny' : 'mdi-weather-night'
        }}</v-icon>
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
            <v-icon >mdi-home</v-icon>
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
            <v-icon>mdi-contact-mail</v-icon>
          </template>
          <v-list-item-title>Contact</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script lang="ts" setup>
import { inject, computed } from 'vue'
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
} from 'vuetify/components'

const toggleDrawer = inject('toggleDrawer')

const theme = useTheme()
const isDarkTheme = computed(() => theme.global.name.value === 'darkTheme')

const toggleTheme = () => {
  theme.global.name.value = isDarkTheme.value ? 'lightTheme' : 'darkTheme'
}
</script>
