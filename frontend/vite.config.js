import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'
import path from 'path'
import svgLoader from 'vite-svg-loader'
import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite'

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: true,
    port: 8080,
  },
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
    VueI18nPlugin({
      runtimeOnly: false,
    }),
    svgLoader({
      svgoConfig: {
        plugins: [
          {
            name: 'preset-default',
            params: {
              overrides: {
                removeViewBox: false,
              },
            },
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@components': path.resolve(__dirname, 'src', 'components'),
      '@assets': path.resolve(__dirname, 'src', 'assets'),
      '@icons': path.resolve(__dirname, 'src', 'components', 'icons'),
      '@stores': path.resolve(__dirname, 'src', 'stores'),
      '@utils': path.resolve(__dirname, 'src', 'utils'),
      '@api': path.resolve(__dirname, 'src', 'api'),
      '@views': path.resolve(__dirname, 'src', 'views'),
      '@composables': path.resolve(__dirname, 'src', 'composables'),
    },
  },
})
