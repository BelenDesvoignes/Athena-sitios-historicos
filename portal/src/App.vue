<script setup>
import { RouterView, useRouter } from 'vue-router'
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { googleSdkLoaded } from 'vue3-google-login'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const useIconButton = ref(false);

const checkScreenSize = () => {
  useIconButton.value = window.innerWidth <= 500;
};

onMounted(() => {
  checkScreenSize();
  window.addEventListener("resize", checkScreenSize);
  googleSdkLoaded((google) => {
    _tokenClient = google.accounts.oauth2.initTokenClient({
      client_id: '567138964451-npnnabs0o6lc434dgtj0fqp8a904cd35.apps.googleusercontent.com',
      scope: 'email profile',
      callback: async (response) => {
        if (response.error) return
        await authStore.loginWithGoogle(response)
      }
    })
  })
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", checkScreenSize);
});

const isMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

let _tokenClient = null

const googleLogin = () => _tokenClient?.requestAccessToken()

const logout = () => {
  const confirmar = window.confirm("¿Estás seguro de que querés cerrar sesión?")
  if (confirmar) {
    authStore.logout()
    router.push('/')
  }
}
</script>

<template>
  <div id="app-wrapper">

    <header class="main-header">
      <div class="header-left">
        <button @click="toggleMenu" class="menu-hamburguer-btn" aria-label="Abrir Menú">
          <span class="icon-line"></span>
          <span class="icon-line"></span>
          <span class="icon-line"></span>
        </button>
      </div>

      <div class="header-center">
        <span class="app-title" @click="router.push('/')">Athena</span>
      </div>

      <div class="header-right">
        <div v-if="authStore.isLoggedIn" class="user-avatar-wrapper">
          <img
            :src="authStore.user.imageUrl"
            alt="Perfil"
            class="user-avatar"
            @click="router.push('/perfil')"
          />
        </div>
        <button @click="googleLogin()" class="google-sign-in-btn" :class="{ 'icon-only': useIconButton }" aria-label="Iniciar sesión con Google">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="18" height="18" aria-hidden="true">
            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
            <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
            <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.36-8.16 2.36-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
          </svg>
          <span v-if="!useIconButton">Ingresar</span>
        </button>
      </div>
    </header>

    <aside :class="['sidebar', { 'is-open': isMenuOpen }]">
      <div class="sidebar-header">
        <span class="sidebar-brand">Athena</span>
        <button @click="toggleMenu" class="close-menu-btn" aria-label="Cerrar menú">✕</button>
      </div>

      <nav class="sidebar-nav">
        <button @click="router.push('/'); toggleMenu();" class="sidebar-link">Inicio</button>
        <button @click="router.push('/sitios'); toggleMenu();" class="sidebar-link">Listado de Sitios</button>

        <template v-if="authStore.isLoggedIn">
          <div class="sidebar-divider"></div>
          <button @click="router.push('/perfil'); toggleMenu();" class="sidebar-link">Perfil</button>
          <button @click="logout(); toggleMenu();" class="sidebar-link logout-link">Cerrar Sesión</button>
        </template>
      </nav>
    </aside>

    <div v-if="isMenuOpen" @click="toggleMenu" class="menu-overlay"></div>

    <RouterView />
  </div>
</template>

<style>
#app-wrapper {
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--text-primary, #111827);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-header {
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 64px;
  background-color: var(--color-primary, #1E3A8A);
  box-shadow: 0 2px 8px rgba(13,148,136,0.3);
  position: sticky;
  top: 0;
  z-index: 1000;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.menu-hamburguer-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.icon-line {
  display: block;
  width: 24px;
  height: 2px;
  background-color: white;
  border-radius: 2px;
}

.header-center {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  flex-shrink: 0;
}

.app-logo {
  height: 36px;
  width: auto;
}

.app-title {
  font-family: 'Nunito', sans-serif;
  font-size: 1.4rem;
  font-weight: 800;
  color: white;
  letter-spacing: -0.3px;
}

.header-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.user-avatar-wrapper {
  cursor: pointer;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.6);
  object-fit: cover;
  transition: border-color 0.2s;
}

.user-avatar:hover {
  border-color: white;
}

/* Sidebar */
.sidebar {
  position: fixed;
  top: 0;
  left: -320px;
  width: 280px;
  height: 100%;
  background-color: white;
  box-shadow: 4px 0 20px rgba(0,0,0,0.12);
  transition: left 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1010;
  display: flex;
  flex-direction: column;
}

.sidebar.is-open {
  left: 0;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 16px;
  background-color: var(--color-primary, #1E3A8A);
}

.sidebar-brand {
  font-family: 'Nunito', sans-serif;
  font-size: 1.3rem;
  font-weight: 800;
  color: white;
}

.close-menu-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  color: rgba(255,255,255,0.8);
  padding: 4px;
  line-height: 1;
  border-radius: 4px;
  transition: color 0.15s, background-color 0.15s;
}

.close-menu-btn:hover {
  color: white;
  background-color: rgba(255,255,255,0.15);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 12px 12px;
  flex-grow: 1;
}

.sidebar-divider {
  height: 1px;
  background-color: var(--border, #E5E7EB);
  margin: 8px 0;
}

.sidebar-link {
  background: none;
  border: none;
  text-align: left;
  padding: 12px 16px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  color: var(--text-primary, #111827);
  border-radius: 8px;
  width: 100%;
  transition: background-color 0.15s;
}

.sidebar-link:hover {
  background-color: var(--surface, #F9FAFB);
  color: var(--color-primary, #1E3A8A);
}

.logout-link {
  color: var(--danger, #EF4444);
}

.logout-link:hover {
  background-color: #FEF2F2;
  color: #DC2626;
}

.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);
  z-index: 1005;
  backdrop-filter: blur(2px);
}

.google-sign-in-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  border: 1px solid rgba(255,255,255,0.4);
  border-radius: 6px;
  padding: 7px 14px;
  font-size: 0.85rem;
  font-weight: 500;
  color: #3c4043;
  cursor: pointer;
  transition: box-shadow 0.15s, background-color 0.15s;
  white-space: nowrap;
  flex-shrink: 0;
}

.google-sign-in-btn:hover {
  background-color: #f8f9fa;
  box-shadow: 0 1px 4px rgba(0,0,0,0.25);
}

.google-sign-in-btn.icon-only {
  padding: 7px;
  border-radius: 50%;
}
</style>
