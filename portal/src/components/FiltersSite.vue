<template>
  <div class="filter-controls-wrapper">
    <div class="filter-header" @click="isFiltersOpen = !isFiltersOpen">
      <h3>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M4.5 6.375a4.125 4.125 0 118.25 0 4.125 4.125 0 01-8.25 0zM14.25 8.625a3.375 3.375 0 116.75 0 3.375 3.375 0 01-6.75 0zM1.5 19.125a7.125 7.125 0 0114.25 0v.003l-.001.119a.75.75 0 01-.363.63 13.067 13.067 0 01-6.761 1.873c-2.472 0-4.786-.684-6.76-1.873a.75.75 0 01-.364-.63l-.001-.122zM17.25 19.128l-.001.144a2.25 2.25 0 01-.233.96 10.088 10.088 0 005.06-1.01.75.75 0 00.42-.643 4.875 4.875 0 00-6.957-4.611 8.586 8.586 0 011.71 5.157v.003z"/></svg>
        Filtros
      </h3>
      <span class="toggle-icon" :class="{ 'is-open': isFiltersOpen }">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path d="M11.9997 10.8284L7.04996 15.7782L5.63574 14.364L11.9997 8L18.3637 14.364L16.9495 15.7782L11.9997 10.8284Z" />
        </svg>
      </span>
    </div>

    <div :class="['filtros-container', { 'is-open': isFiltersOpen }]">
      <input
        v-model="searchTerm"
        @input="updateFilters"
        type="text"
        placeholder="Buscar sitio..."
        class="input-filtro"
      />

      <input
        v-model="city"
        @input="updateFilters"
        type="text"
        placeholder="Ciudad..."
        class="input-filtro"
      />

      <select v-model="province" @change="updateFilters" class="select-filtro">
        <option value="">Todas las provincias</option>
        <option v-for="prov in provinces" :key="prov" :value="prov">{{ prov }}</option>
      </select>

      <select v-model="state" @change="updateFilters" class="select-filtro">
        <option value="">Estado de conservación</option>
        <option value="EXCELENTE">Excelente</option>
        <option value="BUENO">Bueno</option>
        <option value="REGULAR">Regular</option>
        <option value="MALO">Malo</option>
      </select>

      <select v-model="orderByCombined" @change="handleCombinedOrderChange" class="select-filtro">
        <option value="">Ordenar por...</option>
        <option value="registrado_desc">Más recientes</option>
        <option value="registrado_asc">Más antiguos</option>
        <option value="nombre_asc">Nombre (A-Z)</option>
        <option value="nombre_desc">Nombre (Z-A)</option>
        <option value="calificacion_desc">Mejor calificados</option>
        <option value="calificacion_asc">Peor calificados</option>
      </select>

      <label v-if="token" class="tag-checkbox favorite-filter-button" :class="{ 'is-active': onlyFavorites }">
        <input type="checkbox" :value="true" v-model="onlyFavorites" @change="updateFilters" />
        <span>♥ Mis Favoritos</span>
      </label>

      <div class="tag-filter-group">
        <label class="tag-group-label">Categorías</label>
        <div class="tags-list">
          <label v-for="tag in availableTags" :key="tag.id" class="tag-checkbox" :class="{ 'is-active': selectedTags.includes(tag.id) }">
            <input type="checkbox" :value="tag.id" v-model="selectedTags" @change="updateFilters" />
            <span>{{ tag.name }}</span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const router = useRouter()
const route = useRoute()

const authStore = useAuthStore()
const { token } = storeToRefs(authStore)

const isFiltersOpen = ref(true);

const searchTerm = ref(route.query.search || '')
const province = ref(route.query.province || '')
const city = ref(route.query.city || '')
const state = ref(route.query.state || '')

const onlyFavorites = ref(route.query.favorites === 'true')

const orderBy = ref(route.query.order_by || 'registrado')
const orderDirection = ref(route.query.order || 'desc')

const orderByCombined = ref(
  (route.query.order_by && route.query.order)
  ? `${route.query.order_by}_${route.query.order}`
  : 'registrado_desc'
)

const availableTags = ref([])
const selectedTags = ref([])

const provinces = ref([])

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const fetchProvinces = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/provinces`)
    if (!response.ok) throw new Error('Error al obtener provincias')
    provinces.value = await response.json()
  } catch (err) {
    console.error('Error al cargar provincias:', err)
  }
}

const fetchTags = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/tags`)
    if (!response.ok) throw new Error('Error al obtener tags')
    availableTags.value = await response.json()
  } catch (err) {
    console.error('Error al cargar tags:', err)
  }
}

const initSelectedTags = () => {
    if (route.query.tags) {
        selectedTags.value = Array.isArray(route.query.tags)
            ? route.query.tags.map(id => parseInt(id)).filter(id => !isNaN(id))
            : route.query.tags.split(',').map(id => parseInt(id)).filter(id => !isNaN(id));
    } else {
        selectedTags.value = [];
    }
}

const handleCombinedOrderChange = () => {
  const value = orderByCombined.value;
  if (value) {
    const parts = value.split('_');
    if (parts.length === 2) {
      orderBy.value = parts[0];
      orderDirection.value = parts[1];
    }
  } else {
    orderBy.value = 'registrado';
    orderDirection.value = 'desc';
  }
  updateFilters();
}

const updateFilters = () => {
  const tagsParam = selectedTags.value.length > 0 ? selectedTags.value.join(',') : undefined;
  const favoritesParam = onlyFavorites.value ? 'true' : undefined;

  const query = {
    search: searchTerm.value || undefined,
    province: province.value || undefined,
    city: city.value || undefined,
    state: state.value || undefined,
    tags: tagsParam,
    favorites: favoritesParam,
    order_by: orderBy.value || 'registrado',
    order: orderDirection.value || 'desc',
    page: 1
  };

  router.push({ path: '/sitios', query });
}

const resetForm = () => {
    searchTerm.value = '';
    province.value = '';
    city.value = '';
    state.value = '';
    onlyFavorites.value = false;
    selectedTags.value = [];
    orderBy.value = 'registrado';
    orderDirection.value = 'desc';
    orderByCombined.value = 'registrado_desc';
    if (window.innerWidth < 768) {
        isFiltersOpen.value = false;
    }
}

defineExpose({ resetForm })

watch(() => route.query.tags, initSelectedTags, { immediate: true });

watch(
    [() => route.query.order_by, () => route.query.order],
    ([newOrderBy, newOrder]) => {
        orderBy.value = newOrderBy || 'registrado';
        orderDirection.value = newOrder || 'desc';
        orderByCombined.value = `${orderBy.value}_${orderDirection.value}`;
    }
);

watch(
    () => route.query.favorites,
    (newFavorites) => {
        onlyFavorites.value = newFavorites === 'true';
        if (newFavorites === 'true') {
             isFiltersOpen.value = true;
        }
    },
    { immediate: true }
);

onMounted(() => {
    fetchProvinces();
    fetchTags();
    initSelectedTags();
    if (window.innerWidth < 768) {
        isFiltersOpen.value = false;
    }
});
</script>

<style scoped>
.filter-controls-wrapper {
  margin-bottom: 24px;
  background: white;
  border: 1px solid var(--border, #E5E7EB);
  border-radius: var(--radius-md, 12px);
  overflow: hidden;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  cursor: pointer;
  background: var(--surface, #F9FAFB);
  color: var(--text-primary, #111827);
  user-select: none;
}

.filter-header:hover {
  background-color: var(--surface-2, #F3F4F6);
}

.filter-header h3 {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-primary, #0D9488);
}

.toggle-icon {
  width: 20px;
  height: 20px;
  color: var(--text-secondary, #6B7280);
  transition: transform 0.25s ease;
}

.toggle-icon svg {
  width: 100%;
  height: 100%;
  fill: currentColor;
  transform: rotate(180deg);
}

.toggle-icon.is-open svg {
  transform: rotate(0deg);
}

.filtros-container {
  display: none;
  padding: 16px;
  gap: 10px;
  flex-wrap: wrap;
  align-items: flex-start;
  border-top: 1px solid var(--border, #E5E7EB);
}

.filtros-container.is-open {
  display: flex;
}

@media (min-width: 768px) {
  .filter-header { display: none; }
  .filtros-container {
    display: flex !important;
    border-top: none;
    padding: 16px;
  }
}

.input-filtro,
.select-filtro {
  padding: 9px 12px;
  border: 1px solid var(--border, #E5E7EB);
  border-radius: var(--radius-sm, 8px);
  font-size: 0.9rem;
  flex-grow: 1;
  min-width: 160px;
  background: white;
  color: var(--text-primary, #111827);
  font-family: 'Inter', sans-serif;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
}

.input-filtro:focus,
.select-filtro:focus {
  border-color: var(--color-primary, #0D9488);
  box-shadow: 0 0 0 3px rgba(13,148,136,0.1);
}

.tag-filter-group {
  padding: 10px 12px;
  border: 1px solid var(--border, #E5E7EB);
  border-radius: var(--radius-sm, 8px);
  display: flex;
  flex-direction: column;
  gap: 8px;
  background-color: var(--surface, #F9FAFB);
  width: 100%;
}

.tag-group-label {
  font-weight: 600;
  font-size: 0.82rem;
  color: var(--text-secondary, #6B7280);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-checkbox input[type="checkbox"] {
  display: none;
}

.tag-checkbox {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  padding: 5px 12px;
  border: 1px solid var(--border, #E5E7EB);
  border-radius: 20px;
  background-color: white;
  color: var(--text-secondary, #6B7280);
  transition: all 0.15s ease;
  user-select: none;
}

.tag-checkbox:hover {
  border-color: var(--color-primary, #0D9488);
  color: var(--color-primary, #0D9488);
  background-color: var(--color-primary-light, #CCFBF1);
}

.tag-checkbox.is-active,
.tag-checkbox input:checked ~ * {
  background-color: var(--color-primary, #0D9488);
  border-color: var(--color-primary, #0D9488);
  color: white;
}

.tag-checkbox.is-active span {
  background: none;
  padding: 0;
}

.favorite-filter-button {
  padding: 9px 12px;
  border-radius: var(--radius-sm, 8px);
  border: 1px solid var(--border, #E5E7EB);
  background-color: white;
  color: var(--text-primary, #111827);
  font-size: 0.9rem;
  flex-grow: 1;
  min-width: 160px;
  font-weight: 500;
}

.favorite-filter-button.is-active {
  background-color: var(--color-accent, #E8613C);
  border-color: var(--color-accent, #E8613C);
  color: white;
}

.favorite-filter-button span {
  padding: 0;
}
</style>
