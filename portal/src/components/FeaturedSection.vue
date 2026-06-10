<template>
<section class="featured-section">
  <header class="section-header">
    <h2 class="section-title">{{ title }}</h2>
    <RouterLink v-if="listRoute && sites.length > 0" :to="fullListRoute" class="btn-ver-todos">
      Ver todos →
    </RouterLink>
  </header>
  <div v-if="isLoading" class="status-message loading-pulse">
    Cargando {{ title.toLowerCase() }}...
  </div>
  <div v-else-if="error" class="status-message error-box">
    Error al cargar los sitios: {{ errorMessage }}
    <p v-if="props.isFavorite && errorMessage.includes('401')">
      Tu sesión ha expirado. Por favor, volvé a iniciar sesión.
    </p>
  </div>
  <div v-else-if="sites.length > 0" class="site-list">
    <SiteCard v-for="site in sites" :key="site.id" :site="site" />
  </div>
  <div v-else-if="props.isFavorite" class="status-message empty-box">
    Aún no tenés sitios marcados como favoritos.
  </div>
  <div v-else class="status-message empty-box">
    No se encontró contenido para esta sección.
  </div>
</section>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { RouterLink } from 'vue-router';
import SiteCard from './SiteCard.vue';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';

const authStore = useAuthStore();
const { token, isLoggedIn } = storeToRefs(authStore);

const props = defineProps({
    title: { type: String, required: true },
    orderByParam: { type: String, required: true },
    listRoute: { type: String, default: '/sitios' },
    isFavorite: { type: Boolean, default: false }
});

const sites = ref([]);
const isLoading = ref(true);
const error = ref(false);
const errorMessage = ref('');

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const MAX_SITES = 4;

const fullListRoute = computed(() => {
    const query = {
        order_by: props.orderByParam,
        order: 'desc',
        page: 1,
    };
    if (props.isFavorite) {
        query.favorites = 'true';
    }
    return { path: props.listRoute, query };
});

const fetchSites = async () => {
    isLoading.value = true;
    error.value = false;
    errorMessage.value = '';
    if (props.isFavorite && !isLoggedIn.value) {
        errorMessage.value = 'Esta funcionalidad requiere iniciar sesión.';
        isLoading.value = false;
        error.value = true;
        return;
    }
    const params = new URLSearchParams({
        order_by: props.orderByParam,
        order: 'desc',
        per_page: MAX_SITES
    });
    const headers = {};
    if (props.isFavorite) {
        params.append('is_favorite', 'true');
        headers['Authorization'] = `Bearer ${token.value}`;
    }
    const url = `${API_BASE_URL}/sites?${params.toString()}`;
    try {
        const response = await fetch(url, { headers, cache: 'no-store' });
        if (response.status === 401) {
            throw new Error(`HTTP error! status: 401 - No Autorizado`);
        }
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        sites.value = data.data || [];
    } catch (err) {
        console.error(`Fetch error for ${props.title}:`, err);
        errorMessage.value = err.message || 'Error desconocido al conectar con la API.';
        error.value = true;
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    fetchSites();
});
</script>

<style scoped>
.featured-section {
  margin-bottom: 56px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 14px;
  border-bottom: 2px solid var(--border, #E5E7EB);
  position: relative;
}

.section-header::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -2px;
  width: 48px;
  height: 2px;
  background-color: var(--color-primary, #0D9488);
  border-radius: 1px;
}

.section-title {
  font-family: 'Nunito', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
  margin: 0;
}

.btn-ver-todos {
  text-decoration: none;
  color: var(--color-primary, #0D9488);
  font-size: 0.9rem;
  font-weight: 600;
  transition: color 0.15s;
}

.btn-ver-todos:hover {
  color: var(--color-primary-dark, #0F766E);
}

.site-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.status-message {
  padding: 24px;
  text-align: center;
  border-radius: var(--radius-md, 12px);
  font-size: 0.95rem;
}

.loading-pulse {
  color: var(--color-primary, #0D9488);
  background-color: var(--color-primary-light, #CCFBF1);
  font-style: italic;
}

.error-box {
  background-color: #FEF2F2;
  color: #991B1B;
  border: 1px solid #FECACA;
}

.empty-box {
  background-color: var(--surface, #F9FAFB);
  color: var(--text-secondary, #6B7280);
}

@media (max-width: 768px) {
  .site-list { grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); }
}
</style>
