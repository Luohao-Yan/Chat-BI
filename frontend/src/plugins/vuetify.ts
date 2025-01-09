   // src/plugins/vuetify.ts
   import { createVuetify } from 'vuetify';
   import 'vuetify/styles';
   import { aliases, mdi } from 'vuetify/iconsets/mdi';
   import { colors } from '@/styles/colors';

   const lightTheme = {
     dark: false,
     colors: {
       primary: colors.primary,
       secondary: colors.secondary,
       accent: colors.accent,
       error: colors.error,
       info: colors.info,
       success: colors.success,
       warning: colors.warning,
       // 添加图标颜色
       icon: colors.primary,
     },
   };

   const darkTheme = {
     dark: true,
     colors: {
       primary: colors.primary,
       secondary: colors.secondary,
       accent: colors.accent,
       error: colors.error,
       info: colors.info,
       success: colors.success,
       warning: colors.warning,
       // 添加图标颜色
       icon: colors.primary,
     },
   };

   export default createVuetify({
     theme: {
       defaultTheme: 'lightTheme',
       themes: {
         lightTheme,
         darkTheme,
       },
     },
     icons: {
       defaultSet: 'mdi',
       aliases,
       sets: {
         mdi,
       },
     },
   });