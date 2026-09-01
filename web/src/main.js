import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import './styles/index.scss'

// 修复 Vue DevTools 扩展的 startTime 报错问题
// 原因：DevTools 在组件快速卸载时，reportAllChanges 仍尝试访问已清理的性能数据
if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) {
  try {
    const hook = window.__VUE_DEVTOOLS_GLOBAL_HOOK__
    // 禁用性能追踪（startTime 属于性能追踪数据）
    hook.config = hook.config || {}
    hook.config.performance = false
    hook.config.renderTracker = false
    // 包装 emit 捕获 DevTools 内部错误
    const originalEmit = hook.emit
    if (originalEmit) {
      hook.emit = function (...args) {
        try {
          return originalEmit.apply(this, args)
        } catch (e) { /* 忽略 DevTools 内部错误 */ }
      }
    }
    // 包装 on 方法，拦截 component 事件并包装 reportAllChanges
    const originalOn = hook.on
    if (originalOn) {
      hook.on = function (event, handler) {
        if (event === 'component:added' || event === 'component:updated') {
          const wrappedHandler = function (...args) {
            try {
              // 包装组件实例的 reportAllChanges 方法
              const instance = args[0]
              if (instance && typeof instance.reportAllChanges === 'function') {
                const originalReport = instance.reportAllChanges
                instance.reportAllChanges = function (...reportArgs) {
                  try {
                    return originalReport.apply(this, reportArgs)
                  } catch (e) { /* 忽略 */ }
                }
              }
              return handler.apply(this, args)
            } catch (e) { /* 忽略 */ }
          }
          return originalOn.call(this, event, wrappedHandler)
        }
        return originalOn.call(this, event, handler)
      }
    }
  } catch (e) {}
}

const app = createApp(App)

// 禁用 Vue DevTools 集成，修复 DevTools 扩展的 startTime 报错
// 原因：DevTools 在组件快速卸载时，reportAllChanges 仍访问已清理的性能数据(startTime)
// 如需使用 DevTools 调试，可注释掉此行（但 DevTools 的 startTime 报错会恢复）
app.config.devtools = false

const pinia = createPinia()

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 先注册 pinia，再注册 router（因为路由守卫中使用了 pinia store）
app.use(pinia)
app.use(router)
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')
