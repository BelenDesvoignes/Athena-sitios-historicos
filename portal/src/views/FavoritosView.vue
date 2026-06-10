<template>
  <div class="favoritos-page">
    <BackButton />
    <header class="page-header">
      <h1>Mis Sitios Favoritos</h1>
      <p class="subtitle">Los lugares que has marcado como preferidos.</p>
    </header>

    <main class="favoritos-main">
      <div v-if="isLoading" class="status-message loading-box">
        Cargando tus sitios favoritos...
      </div>
      <div v-else-if="error" class="error-message message-box">
        ❌ Error al cargar favoritos: **{{ errorMessage }}**
        <p v-if="errorStatusCode === 401">
          Por favor, <router-link to="/login">inicia sesión</router-link> para ver esta sección.
        </p>
      </div>

      <div v-else-if="sites.length > 0" class="list-grid">
        <SiteCard
          v-for="site in sites"
          :key="site.id"
          :site="site"
        />
      </div>
      <div v-else class="empty-message message-box">
        Aún no has agregado sitios a tu lista de favoritos.
        <p>¡Explora el portal y marca tus lugares históricos preferidos!</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import SiteCard from '@/components/SiteCard.vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import BackButton from '@/components/BackButton.vue';

const authStore = useAuthStore();
const router = useRouter();

const sites = ref([]);
const isLoading = ref(true);
const error = ref(null);
const errorMessage = ref('');
const errorStatusCode = ref(null);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const fetchFavorites = async () => {
    if (!authStore.isLoggedIn) {
        router.push('/login');
        return;
    }

    isLoading.value = true;
    error.value = null;
    errorMessage.value = '';
    errorStatusCode.value = null;

    const url = `${API_BASE_URL}/me/favorites`;

    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...authStore.authHeader
            }
        });

        if (response.status === 401) {
            authStore.logout();
            errorMessage.value = 'Tu sesión ha expirado.';
            errorStatusCode.value = 401;
            error.value = true;
            return;
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        // Extraemos la lista de favoritos desde data.data
        sites.value = data.data || [];

    } catch (err) {
        console.error('Fetch error for favorites:', err);
        errorMessage.value = err.message;
        error.value = true;
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    fetchFavorites();
});
</script>

<style scoped>
.favoritos-page {
  padding: 40px 24px 60px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 40px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--border, #E5E7EB);
  position: relative;
}

.page-header::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -2px;
  width: 48px;
  height: 2px;
  background-color: var(--color-primary, #0D9488);
}

.page-header h1 {
  font-family: 'Nunito', sans-serif;
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--text-primary, #111827);
  margin-bottom: 6px;
}

.subtitle {
  color: var(--text-secondary, #6B7280);
  font-size: 1rem;
}

.list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 8px 0;
}

.message-box {
  text-align: center;
  padding: 32px;
  border-radius: var(--radius-md, 12px);
  margin-top: 16px;
  font-size: 1rem;
}

.loading-box {
  color: var(--color-primary, #0D9488);
  background-color: var(--color-primary-light, #CCFBF1);
  font-style: italic;
}

.error-message {
  background-color: #FEF2F2;
  color: #991B1B;
  border: 1px solid #FECACA;
}

.empty-message {
  background-color: var(--surface, #F9FAFB);
  color: var(--text-secondary, #6B7280);
  border: 1px solid var(--border, #E5E7EB);
}

.empty-message p {
  margin-top: 10px;
  font-style: italic;
  color: var(--text-muted, #9CA3AF);
}

.error-message a {
  color: var(--color-primary, #0D9488);
  font-weight: bold;
}
</style>
