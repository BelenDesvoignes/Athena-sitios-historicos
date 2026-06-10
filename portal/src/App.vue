<script setup>
import { RouterView, useRouter } from 'vue-router'
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { GoogleLogin } from 'vue3-google-login'
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
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", checkScreenSize);
});

const isMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const callback = async (response) => {
  console.log("Respuesta de Google recibida. Procesando login en Pinia Store...")
  await authStore.loginWithGoogle(response)
}

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
        <div v-else class="google-login-btn-wrapper">
          <GoogleLogin
            v-if="!useIconButton"
            :callback="callback"
            :buttonConfig="{ type: 'standard', theme: 'outline', size: 'medium' }"
          />
          <GoogleLogin
            v-else
            :callback="callback"
            :buttonConfig="{ type: 'icon', shape: 'circle', size: 'medium' }"
          />
        </div>
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

</style>
