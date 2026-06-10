<template>
  <div class="listado-sitios-page">

    <header>
      <BackButton />
      <h1>Listado de Sitios Históricos</h1>
      <!-- FiltersSite maneja todos los filtros, incluyendo el de favoritos -->
      <FiltersSite ref="filtersSiteRef" />

      <div class="controls-group">
        <div class="map-controls">
          <button
            @click="openMapModal"
            :class="{'btn-active': isModalOpen}"
            class="map-toggle-button"
          >
            Ver mapa de sitios
          </button>

          <button v-if="Object.keys(route.query).length > 0"
                  @click="clearAllFilters"
                  class="clear-filters-button">
            Limpiar Filtros
          </button>
        </div>
      </div>
    </header>

    <main>
      <div v-if="isLoading" class="status-message">Cargando sitios...</div>
      <div v-else-if="error" class="error-message">❌ Error al cargar el listado: {{ error }}</div>

      <div v-else-if="sites.length > 0" class="list-grid">
        <SiteCard
          v-for="site in sites"
          :key="site.id"
          :site="site"
          @toggle-favorite="fetchSitesList"
        />
      </div>

      <div v-else class="empty-message">
        No se encontraron sitios con los filtros aplicados.
      </div>
    </main>

    <!-- PAGINACIÓN -->
    <nav v-if="pagination.total > 0" class="pagination-controls">
      <p class="pagination-info">
        Página {{ pagination.page }} de {{ pagination.pages }}
      </p>

      <button @click="goToPage(pagination.page - 1)"
              :disabled="pagination.page === 1"
              class="pagination-button">
        ← Anterior
      </button>

      <button @click="goToPage(pagination.page + 1)"
              :disabled="pagination.page === pagination.pages"
              class="pagination-button">
        Siguiente →
      </button>
    </nav>

    <!-- MODAL MAPA -->
    <div v-if="isModalOpen" class="modal-overlay" @click.self="isModalOpen = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Mapa de Sitios Históricos</h2>
          <button class="close-button" @click="isModalOpen = false">&times;</button>
        </div>

        <div class="modal-body">
          <SiteMap
            ref="siteMapRef"
            :sites="sites"
            :lat="currentLat"
            :lon="currentLon"
            :radius="currentRadius"
            @filterByLocation="applyUserLocationFilter"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import FiltersSite from '@/components/FiltersSite.vue'
import SiteCard from '@/components/SiteCard.vue'
import SiteMap from '@/components/SiteMap.vue'
import BackButton from '@/components/BackButton.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { token } = storeToRefs(authStore) 

const filtersSiteRef = ref(null)
const siteMapRef = ref(null)

const sites = ref([])
const isLoading = ref(true)
const error = ref('')
const isModalOpen = ref(false)

const isFavoriteFilterActive = computed(() => route.query.favorites === 'true')

const currentLat = computed(() => route.query.lat || null)
const currentLon = computed(() => route.query.lon || null)
const currentRadius = computed(() => route.query.radius || null)


const clearAllFilters = () => {
  filtersSiteRef.value?.resetForm?.()
  router.push({ query: {} })
}


const openMapModal = async () => {
  isModalOpen.value = true
  await nextTick()
  siteMapRef.value?.forceUpdate()
}


const applyUserLocationFilter = ({ lat, lon, radius }) => {
  router.push({
    query: {
      ...route.query,
      lat,
      lon,
      radius,
      order_by: "distancia",
      order: "asc",
      page: 1
    }
  })
}


const pagination = ref({
  page: 1,
  pages: 1,
  total: 0,
  per_page: 10
})

const goToPage = (p) => {
  if (p < 1 || p > pagination.value.pages) return
  router.push({ query: { ...route.query, page: p } })
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const fetchSitesList = async () => {
  isLoading.value = true
  error.value = ''

  
  const orderBy = route.query.order_by || "registrado";
  const order = route.query.order || "desc";
  const page = route.query.page || 1;
  const perPage = route.query.per_page || 10;


  const params = new URLSearchParams({
    order_by: orderBy,
    order: order,
    page: page,
    per_page: perPage,
  })

  
  const dynamic = ["search", "province", "city", "state", "tags", "lat", "lon", "radius"]
  dynamic.forEach(p => route.query[p] && params.append(p, route.query[p]))

  const fetchingFavorites = isFavoriteFilterActive.value;
  let headers = {};

  if (fetchingFavorites) {
    
    params.append('is_favorite', 'true');

  
    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`;
    } else {
      
      isLoading.value = false;
      error.value = "Debes iniciar sesión para filtrar tus sitios favoritos.";
      sites.value = [];
    
      const newQuery = { ...route.query };
      delete newQuery.favorites;
      router.replace({ query: newQuery });
      return;
    }
  }

  try {
    const res = await fetch(`${API_BASE_URL}/sites?${params.toString()}`, { headers, cache: 'no-store' })

    if (!res.ok) {
      throw new Error(`Fallo la solicitud del listado. Código: ${res.status}`);
    }

    const data = await res.json()

    sites.value = data.data || []
    pagination.value = {
      page: data.page,
      pages: data.pages,
      total: data.total,
      per_page: data.per_page,
    }

    

  } catch (e) {
    console.error("Error al obtener sitios:", e);
    error.value = e.message || 'Ocurrió un error inesperado al cargar los sitios.';
  } finally {
    isLoading.value = false
  }
}

watch(() => route.query, fetchSitesList, { immediate: true })
onMounted(fetchSitesList)
</script>

<style scoped>
.listado-sitios-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 60px;
}

header {
  margin-bottom: 24px;
}

h1 {
  font-family: 'Nunito', sans-serif;
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--text-primary, #111827);
  margin-bottom: 4px;
}

.controls-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin-top: 12px;
}

.map-controls { display: flex; gap: 10px; flex-wrap: wrap; }

.list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 8px 0;
}

.status-message, .empty-message {
  text-align: center;
  margin-top: 40px;
  color: var(--text-secondary, #6B7280);
  padding: 32px;
  background: var(--surface, #F9FAFB);
  border-radius: var(--radius-md, 12px);
  border: 1px solid var(--border, #E5E7EB);
}

.error-message {
  text-align: center;
  margin-top: 16px;
  background-color: #FEF2F2;
  color: #991B1B;
  padding: 16px;
  border-radius: var(--radius-md, 12px);
  border: 1px solid #FECACA;
}

.map-toggle-button, .clear-filters-button {
  border: none;
  padding: 9px 18px;
  border-radius: var(--radius-sm, 8px);
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  font-family: 'Inter', sans-serif;
  transition: background-color 0.2s, transform 0.1s;
}

.map-toggle-button {
  background-color: var(--color-primary, #1E3A8A);
  color: white;
}

.map-toggle-button:hover, .map-toggle-button.btn-active {
  background-color: var(--color-primary-dark, #172554);
}

.clear-filters-button {
  background-color: var(--surface-2, #F3F4F6);
  color: var(--text-secondary, #6B7280);
  border: 1px solid var(--border, #E5E7EB);
}

.clear-filters-button:hover {
  background-color: #FEE2E2;
  color: #991B1B;
  border-color: #FECACA;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 24px 0;
  margin-top: 16px;
  border-top: 1px solid var(--border, #E5E7EB);
}

.pagination-info {
  color: var(--text-secondary, #6B7280);
  font-size: 0.9rem;
}

.pagination-button {
  background-color: var(--color-primary, #1E3A8A);
  color: white;
  border: none;
  padding: 9px 18px;
  border-radius: var(--radius-sm, 8px);
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.pagination-button:disabled {
  background-color: var(--border, #E5E7EB);
  color: var(--text-muted, #9CA3AF);
  cursor: not-allowed;
}

.pagination-button:not(:disabled):hover {
  background-color: var(--color-primary-dark, #172554);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: var(--radius-lg, 16px);
  width: 90%;
  max-width: 1000px;
  box-shadow: var(--shadow-lg);
  position: relative;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border, #E5E7EB);
  padding-bottom: 12px;
  margin-bottom: 12px;
}

.modal-header h2 {
  font-family: 'Nunito', sans-serif;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: var(--text-secondary, #6B7280);
  padding: 4px;
  border-radius: 4px;
  transition: color 0.15s;
}

.close-button:hover { color: var(--text-primary, #111827); }

.modal-body {
  flex-grow: 1;
  min-height: 500px;
}
</style>