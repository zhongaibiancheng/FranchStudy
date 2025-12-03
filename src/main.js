import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 确保按正确顺序初始化
const app = createApp(App)

// 先使用 router 插件
app.use(router)

// 然后挂载
app.mount('#app')