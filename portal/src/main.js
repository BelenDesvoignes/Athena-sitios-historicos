import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import vue3GoogleLogin from 'vue3-google-login'

import 'leaflet/dist/leaflet.css'
const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vue3GoogleLogin, {
  clientId: '567138964451-npnnabs0o6lc434dgtj0fqp8a904cd35.apps.googleusercontent.com'
})

app.mount('#app')
