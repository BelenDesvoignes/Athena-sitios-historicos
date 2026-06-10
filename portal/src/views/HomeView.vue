<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';
import FeaturedSection from '@/components/FeaturedSection.vue';

const router = useRouter();
const authStore = useAuthStore();
const { isLoggedIn } = storeToRefs(authStore);

const searchText = ref('');

const performSearch = () => {
  if (searchText.value.trim()) {
    router.push({
      path: '/sitios',
      query: { search: searchText.value }
    });
  }
};
</script>

<template>
<div class="home-portal">

  <section class="hero-section">
    <div class="hero-content">
      <p class="hero-eyebrow">Descubrí la Argentina</p>
      <h1 class="hero-title">Patrimonio Histórico Argentino</h1>
      <p class="hero-subtitle">Explorá monumentos, sitios arqueológicos y lugares históricos de todo el país.</p>

      <div class="search-bar">
        <div class="search-input-wrapper">
          <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <input
            type="text"
            v-model="searchText"
            placeholder="Buscar por nombre, ciudad o descripción..."
            @keyup.enter="performSearch"
            class="search-input"
          />
        </div>
        <button @click="performSearch" class="search-button">Buscar</button>
      </div>

      <div class="hero-actions">
        <button @click="router.push('/sitios')" class="btn-secondary-hero">
          Ver todos los sitios →
        </button>
      </div>
    </div>

    <div class="hero-decoration">
      <div class="hero-circle hero-circle-1"></div>
      <div class="hero-circle hero-circle-2"></div>
    </div>
  </section>

  <main class="main-content">
    <FeaturedSection
      v-if="isLoggedIn"
      title="Tus Favoritos"
      orderByParam="calificacion"
      :isFavorite="true"
    />

    <FeaturedSection
      title="Mejor Puntuados"
      orderByParam="calificacion"
    />

    <FeaturedSection
      title="Recientemente Agregados"
      orderByParam="registrado"
    />
  </main>

</div>
</template>

<style scoped>
.home-portal {
  min-height: calc(100vh - 64px);
}

/* Hero */
.hero-section {
  position: relative;
  background: linear-gradient(135deg, var(--color-primary-dark, #172554) 0%, var(--color-primary, #1E3A8A) 50%, #3B82F6 100%);
  padding: 72px 24px 80px;
  overflow: hidden;
  text-align: center;
}

.hero-content {
  position: relative;
  z-index: 2;
  max-width: 720px;
  margin: 0 auto;
}

.hero-eyebrow {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: rgba(255,255,255,0.7);
  margin-bottom: 12px;
}

.hero-title {
  font-family: 'Nunito', sans-serif;
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 800;
  color: white;
  line-height: 1.15;
  margin-bottom: 16px;
}

.hero-subtitle {
  font-size: 1.1rem;
  color: rgba(255,255,255,0.85);
  margin-bottom: 36px;
  line-height: 1.6;
}

.search-bar {
  display: flex;
  gap: 8px;
  max-width: 580px;
  margin: 0 auto 20px;
}

.search-input-wrapper {
  position: relative;
  flex-grow: 1;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted, #9CA3AF);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 14px 16px 14px 44px;
  font-size: 1rem;
  border: 2px solid transparent;
  border-radius: var(--radius-md, 12px);
  background: white;
  color: var(--text-primary, #111827);
  outline: none;
  transition: border-color 0.2s;
  font-family: 'Inter', sans-serif;
}

.search-input:focus {
  border-color: rgba(255,255,255,0.5);
  box-shadow: 0 0 0 4px rgba(255,255,255,0.15);
}

.search-input::placeholder {
  color: var(--text-muted, #9CA3AF);
}

.search-button {
  padding: 14px 28px;
  background-color: var(--color-accent, #E8613C);
  color: white;
  border: none;
  border-radius: var(--radius-md, 12px);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 0.2s, transform 0.1s;
  font-family: 'Inter', sans-serif;
}

.search-button:hover {
  background-color: var(--color-accent-dark, #C84E2C);
}

.search-button:active {
  transform: scale(0.98);
}

.hero-actions {
  margin-top: 8px;
}

.btn-secondary-hero {
  background: none;
  border: 2px solid rgba(255,255,255,0.5);
  color: white;
  padding: 10px 22px;
  border-radius: 100px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;
}

.btn-secondary-hero:hover {
  background-color: rgba(255,255,255,0.12);
  border-color: rgba(255,255,255,0.8);
}

/* Decorative circles */
.hero-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}

.hero-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.06);
}

.hero-circle-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  right: -80px;
}

.hero-circle-2 {
  width: 250px;
  height: 250px;
  bottom: -60px;
  left: 5%;
}

/* Main content */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 24px 60px;
}

@media (max-width: 600px) {
  .hero-section { padding: 48px 20px 56px; }
  .search-bar { flex-direction: column; }
  .search-button { width: 100%; }
}
</style>
