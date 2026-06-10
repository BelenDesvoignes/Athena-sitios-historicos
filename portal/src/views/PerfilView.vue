<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import BackButton from '@/components/BackButton.vue'

const authStore = useAuthStore()
const router = useRouter()

if (!authStore.isLoggedIn) {
  router.push('/')
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
  <div class="profile-container">
    <BackButton />
    <div class="profile-header">
      <img
        :src="authStore.user.imageUrl"
        alt="Foto de usuario"
        class="profile-avatar"
      />

      <h2 class="profile-name">{{ authStore.user.name }}</h2>

      <p class="profile-email">{{ authStore.user.email }}</p>
    </div>

    <hr class="divider"/>

    <div class="profile-actions">
      <button @click="router.push('/mis-resenas')" class="profile-btn">
        📝 Mis Reseñas
      </button>

      <button @click="router.push('/mis-favoritos')" class="profile-btn">
        ❤️ Sitios Favoritos
      </button>

      <button @click="logout();" class="profile-btn logout-btn">
        🚪 Cerrar Sesión
      </button>
    </div>

  </div>
</template>

<style scoped>
.profile-container {
  padding: 48px 24px 60px;
  max-width: 480px;
  margin: 0 auto;
}

.profile-header {
  text-align: center;
  margin-bottom: 32px;
}

.profile-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--color-primary, #1E3A8A);
  box-shadow: 0 4px 12px rgba(30,58,138,0.2);
}

.profile-name {
  margin-top: 14px;
  font-family: 'Nunito', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
}

.profile-email {
  font-size: 0.92rem;
  color: var(--text-secondary, #6B7280);
  margin-top: 4px;
}

.divider {
  margin: 24px 0;
  border: none;
  border-top: 1px solid var(--border, #E5E7EB);
}

.profile-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.profile-btn {
  width: 100%;
  max-width: 300px;
  background-color: var(--color-primary, #1E3A8A);
  color: white;
  padding: 13px 20px;
  font-size: 0.97rem;
  border-radius: var(--radius-md, 12px);
  border: none;
  cursor: pointer;
  text-align: center;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  transition: background-color 0.2s, transform 0.15s, box-shadow 0.2s;
  box-shadow: var(--shadow-sm);
}

.profile-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  background-color: var(--color-primary-dark, #172554);
}

.logout-btn {
  background-color: transparent;
  color: var(--danger, #EF4444);
  border: 1px solid var(--danger, #EF4444);
}

.logout-btn:hover {
  background-color: #FEF2F2;
  box-shadow: none;
}
</style>
