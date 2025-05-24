import { globalIgnores } from 'eslint/config'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
import pluginVue from 'eslint-plugin-vue'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'

export default [
  // 全局忽略
  {
    ignores: ['**/dist/**', '**/dist-ssr/**', '**/coverage/**'],
  },

  // Vue + TypeScript 规则配置
  ...defineConfigWithVueTs(),

  // vue 基础配置
  {
    files: ['**/*.vue'],
    ...pluginVue.configs['flat/essential'],
  },

  // 额外 TS 配置
  {
    files: ['**/*.{ts,tsx,mts}'],
    ...vueTsConfigs.recommended,
  },

  // 关闭 Prettier 格式化（如适用）
  skipFormatting,
]
