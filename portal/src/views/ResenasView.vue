<template>
  <div class="reviews-page">
    <BackButton />
    <header class="page-header">
      <h1>Mis Reseñas</h1>
      <p class="subtitle">El estado de aprobación de tus comentarios.</p>
    </header>

    <main class="reviews-main">
      <div v-if="reviewsFeatureDisabled" class="reviews-disabled-msg">
          ✖️ Las reseñas están desactivadas temporalmente.
      </div>
      <div v-else>
        <div v-if="isLoading" class="status-message loading-box">
          Cargando tus reseñas...
        </div>

        <div v-else-if="error" class="error-message message-box">
          ❌ Error al cargar reseñas: **{{ errorMessage }}**
          <p v-if="errorStatusCode === 401">
            Por favor, inicia sesión nuevamente.
          </p>
        </div>

        <div v-else-if="reviews.length > 0" class="list-grid">
          <div v-for="review in reviews" :key="review.id" class="review-card">
            <section>
              <h3 class="review-title">Reseña del sitio: {{ review.site_name }}</h3>
        <button @click="openEditReviewModal(review)" class="edit-btn">
          ✏️ Editar
        </button>

        <button @click="deleteReview(review)" class="modal-delete">
          🗑️ Eliminar
        </button>
            </section>

            <p class="review-rating">⭐ {{ review.rating }} / 5</p>
            <p class="review-comment">Comentario: {{ review.comment }}</p>
            <p class="review-status" :class="{
              pendiente: review.status === 'PENDIENTE',
              aprobada: review.status === 'APROBADA',
              rechazada: review.status === 'RECHAZADA'
            }">
              Estado: {{ review.status }}
            </p>

            <p v-if="review.rejection_reason" class="review-rejection">
              Motivo de rechazo: {{ review.rejection_reason }}
            </p>

            <p class="review-date">
              Publicada el {{ formatDate(review.created_at) }}
            </p>

            <p class="review-content">
              {{ review.content }}
            </p>
          </div>
        </div>

        <div v-else class="empty-message message-box">
          Aún no escribiste reseñas.
          <p>¡Explora sitios y comparte tu experiencia!</p>
        </div>
      </div>

<div v-if="showReviewModal" class="review-modal-overlay" @click="closeReviewModal">
  <div class="review-modal" @click.stop>

    <!-- Header -->
    <div class="review-modal-header">
      <h3 v-if="!userReview">✍️ Escribir reseña</h3>
      <h3 v-else>✍️ Editar reseña</h3>
      <button class="close-btn" @click="closeReviewModal">✕</button>
    </div>

    <!-- Body -->
    <div class="review-modal-body">
      <label class="input-label">Calificación</label>
      <select v-model="newReview.rating" class="input-select">
        <option disabled value="">Selecciona…</option>
        <option v-for="n in 5" :key="n" :value="n">{{ n }} ⭐</option>
      </select>
      <label class="input-label">Comentario</label>
      <textarea v-model="newReview.content" class="input-textarea" rows="4"></textarea>
    </div>


        <div class="pagination" v-if="totalPages > 1">
          <button class="page-button" :disabled="currentPage <= 1" @click="prevPage()">
            Anterior
          </button>

          <span>Página {{ currentPage }} de {{ totalPages }}</span>

          <button class="page-button" :disabled="currentPage >= totalPages" @click="nextPage()">
            Siguiente
          </button>
        </div>

    <!-- Footer -->
    <div class="review-modal-footer">
      <button class="primary-btn" @click="submitReview">
        {{ userReview ? "Actualizar reseña" : "Enviar reseña" }}
      </button>
      <button class="secondary-btn" @click="closeReviewModal">Cancelar</button>
    </div>

  </div>
</div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from '@/stores/auth';
import { useRouter } from "vue-router";
import BackButton from '@/components/BackButton.vue';

const reviewsFeatureDisabled = ref(false);

async function fetchReviewsFlag() {
  try {
    const response = await fetch(`${API_BASE_URL}/flags/reviews`);
    const data = await response.json();
    reviewsFeatureDisabled.value = data.disabled;
  } catch (err) {
    console.error("Error obteniendo flag de reseñas:", err);
  }
}

const authStore = useAuthStore();
const router = useRouter();

const showLoginPromptReseña = ref(false);
const reviews = ref([]);
const isLoading = ref(true);
const error = ref(null);
const errorMessage = ref("");
const errorStatusCode = ref(null);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;


const showReviewModal = ref(false);
const userReview = ref(null); 
const newReview = ref({
  rating: "",
  content: "",
  id:""
});


const currentPage = ref(1);
const totalPages = ref(1);
const perPage = 25;

const fetchReviews = async () => {
  if (!authStore.isLoggedIn) {
    router.push("/login");
    return;
  }

  isLoading.value = true;
  error.value = null;
  errorMessage.value = "";

  const url = `${API_BASE_URL}/me/reviews`;

  try {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        Authorization: authStore.authHeader.Authorization,
      }
    });

    if (response.status === 401) {
      errorMessage.value = "Tu sesión ha expirado.";
      errorStatusCode.value = 401;
      error.value = true;
      authStore.logout();
      return;
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }


    const data = await response.json();
    console.log("Fetched reviews data:", data);
    reviews.value = data.reviews || [];
    console.log("Reviews data length:", data.data);
    console.log("Reviews set to:", reviews.value);
  } catch (err) {
    console.error("Fetch error for reviews:", err);
    errorMessage.value = err.message;
    error.value = true;
  } finally {
    isLoading.value = false;
  }


};

function get_reseña(id_reseña) {
  return reviews.value.find(r => r.id == id_reseña);
}


function closeReviewModal() {
  showReviewModal.value = false;
}
const submitReview = async () => {
  if (!authStore.isLoggedIn) return;

  const aEditar = get_reseña(userReview.value.id)
  const url = `${API_BASE_URL}/sites/${aEditar.site_id}/reviews/${userReview.value.id}`  

  const method = "PUT";

  try {
    const res = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: authStore.authHeader.Authorization,
      },
      body: JSON.stringify({
        site_id: aEditar.site_id,
        rating: newReview.value.rating,
        comment: newReview.value.content,
      })
    });

    if (!res.ok) throw new Error("Error guardando la reseña");
    await fetchReviews();
    closeReviewModal();
  } catch (err) {
    alert(err.message);
  }
};

const deleteReview = async (review) => {
  try {
    const authStore = useAuthStore();

    if (!authStore.isLoggedIn) {
      alert("Debes iniciar sesión para eliminar una reseña.");
      return;
    }

    const authorizationToken = authStore.authHeader.Authorization;
    if (!authorizationToken) {
      alert("Error: No se encontró el token de autenticación.");
      return;
    }

    const response = await fetch(`${API_BASE_URL}/sites/${review.site_id}/reviews/${review.id}`, {
      method: "DELETE",
      headers: {
        "Authorization": authorizationToken,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      console.error("❌ Error eliminando reseña:", data);
      alert(data.msg || data.error || JSON.stringify(data));
      return;
    }

    alert("Reseña eliminada con éxito ✔️");

    
    currentPage.value = 1;
    await fetchReviews();

  } catch (error) {
    console.error("❌ Error en deleteReview:", error);
    alert("Error de conexión o inesperado al eliminar la reseña.");
  }
}


const openEditReviewModal = (review) => {
  userReview.value = review;
  newReview.value.rating = review.rating;
  newReview.value.content = review.comment;
  showReviewModal.value = true;
};



const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString();
};

onMounted(() => {
  fetchReviewsFlag();
  fetchReviews();
});
</script>

<style scoped>
.reviews-page {
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
  grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
  gap: 20px;
  padding: 8px 0;
}

.review-card {
  padding: 20px;
  border-radius: var(--radius-lg, 16px);
  border: 1px solid var(--border, #E5E7EB);
  background: white;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.review-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.review-title {
  font-family: 'Nunito', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
  flex: 1;
}

.review-rating {
  margin-top: 8px;
  font-size: 1rem;
  color: var(--text-secondary, #6B7280);
  font-weight: 600;
}

.review-comment {
  margin-top: 10px;
  font-size: 0.95rem;
  color: var(--text-primary, #111827);
  padding: 10px 12px;
  background: var(--surface, #F9FAFB);
  border-radius: var(--radius-sm, 8px);
  border: 1px solid var(--border, #E5E7EB);
  line-height: 1.5;
  display: block;
  overflow: auto;
}

.review-status {
  display: inline-block;
  margin-top: 12px;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  width: fit-content;
}

.review-status.pendiente {
  background-color: #FEF3C7;
  color: #92400E;
}

.review-status.aprobada {
  background-color: #D1FAE5;
  color: #065F46;
}

.review-status.rechazada {
  background-color: #FEE2E2;
  color: #991B1B;
}

.review-rejection {
  margin-top: 8px;
  color: #991B1B;
  font-size: 0.9rem;
  background: #FEF2F2;
  padding: 8px 10px;
  border-radius: var(--radius-sm, 8px);
  border: 1px solid #FECACA;
}

.review-date {
  font-size: 0.82rem;
  color: var(--text-muted, #9CA3AF);
  margin-top: 10px;
}

.review-content {
  margin-top: 8px;
  color: var(--text-secondary, #6B7280);
  line-height: 1.5;
  font-size: 0.92rem;
}

.message-box {
  text-align: center;
  padding: 32px;
  border-radius: var(--radius-md, 12px);
  margin-top: 16px;
  font-size: 1rem;
}

/* Modal */
.review-modal-overlay {
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

.review-modal {
  background: white;
  padding: 24px;
  border-radius: var(--radius-lg, 16px);
  max-width: 500px;
  width: 90%;
  box-shadow: var(--shadow-lg);
}

.review-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border, #E5E7EB);
  padding-bottom: 12px;
  margin-bottom: 16px;
}

.review-modal-header h3 {
  margin: 0;
  font-family: 'Nunito', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  color: var(--text-secondary, #6B7280);
  padding: 4px;
  border-radius: 4px;
  transition: color 0.15s;
}

.close-btn:hover { color: var(--text-primary, #111827); }

.review-modal-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-label {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-secondary, #6B7280);
}

.input-select, .input-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border, #E5E7EB);
  border-radius: var(--radius-sm, 8px);
  font-size: 0.95rem;
  font-family: 'Inter', sans-serif;
  outline: none;
  transition: border-color 0.2s;
}

.input-select:focus, .input-textarea:focus {
  border-color: var(--color-primary, #0D9488);
  box-shadow: 0 0 0 3px rgba(13,148,136,0.1);
}

.review-modal-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.primary-btn {
  padding: 10px 20px;
  background: var(--color-primary, #0D9488);
  color: white;
  border: none;
  border-radius: var(--radius-sm, 8px);
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  transition: background 0.2s;
}

.primary-btn:hover { background: var(--color-primary-dark, #0F766E); }

.secondary-btn {
  padding: 10px 20px;
  background: var(--surface-2, #F3F4F6);
  color: var(--text-primary, #111827);
  border: 1px solid var(--border, #E5E7EB);
  border-radius: var(--radius-sm, 8px);
  cursor: pointer;
  font-size: 0.95rem;
  transition: background 0.2s;
}

.secondary-btn:hover { background: #E5E7EB; }

.review-card section {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.edit-btn {
  background: var(--surface-2, #F3F4F6);
  border: none;
  padding: 6px 10px;
  cursor: pointer;
  border-radius: var(--radius-sm, 8px);
  font-size: 0.88rem;
  transition: background 0.15s;
}

.edit-btn:hover { background: #FEF3C7; }

.modal-delete {
  background: var(--surface-2, #F3F4F6);
  border: none;
  font-size: 0.88rem;
  padding: 6px 10px;
  cursor: pointer;
  border-radius: var(--radius-sm, 8px);
  transition: background 0.15s;
}

.modal-delete:hover { background: #FEE2E2; }

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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border, #E5E7EB);
  font-size: 0.9rem;
  color: var(--text-secondary, #6B7280);
}

.page-button {
  padding: 8px 16px;
  background: var(--color-primary, #0D9488);
  color: white;
  border: none;
  border-radius: var(--radius-sm, 8px);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background 0.2s;
}

.page-button:disabled {
  background: var(--border, #E5E7EB);
  color: var(--text-muted, #9CA3AF);
  cursor: not-allowed;
}

.page-button:not(:disabled):hover { background: var(--color-primary-dark, #0F766E); }

.reviews-disabled-msg {
  text-align: center;
  padding: 14px 18px;
  background: #FEF3C7;
  border: 1px solid #FDE68A;
  border-radius: var(--radius-sm, 8px);
  font-size: 0.95rem;
  color: #92400E;
  margin-bottom: 16px;
}
</style>
