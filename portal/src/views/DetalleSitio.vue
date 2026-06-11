<template>
  <div class="site-detail-page">
    <div v-if="isLoading" class="status-message">
      Cargando detalles del sitio...
    </div>
    <div v-else-if="error" class="status-message error">
      ❌ {{ errorMessage }}
    </div>
    <section v-else-if="site" class="site-content">
      <BackButton />
      <header class="detail-header">
        <h1>{{ site.name }}</h1>
        <p class="location-info">📍 {{ site.city }}, {{ site.province }}</p>
        <div v-if="site.average_rating" class="rating-badge">
          ⭐ {{ Number(site.average_rating || 0).toFixed(1) }} ({{ totalReviews || 0 }} Reseñas)
        </div>
      </header>

      <hr>

      <div class="main-info-grid">
        <div class="image-container">
          <div class="cover-wrapper">
            <img :src="site.cover_image?.url || '/default.jpg'"
              :alt="site.cover_image?.title || site.name" class="site-cover-image" @click="openByIndex(0)">
            <button class="expand-button cover" @click.stop="openByIndex(0)">🔍</button>
          </div>
        </div>

        <div class="description-section">
          <h2>Descripción Breve</h2>
          <p>{{ site.short_description }}</p>

          <RouterLink
            v-for="tag in site.tags"
            :key="tag.id"
            :to="{
              path: '/sitios',
              query: { tags: tag.id }
            }"
            class="tag-badge">
            {{ tag.name }}
          </RouterLink>


          <div class="action-buttons">
            <!-- Botón de Favorito: Ahora SIEMPRE visible, llama a handleFavoriteAction -->
            <button
              @click="handleFavoriteAction"
              :class="['favorite-button', { 'is-favorite': isFavorite }]"
              :title="isFavorite ? 'Remover de Favoritos' : 'Marcar como Favorito'"
            >
              <span class="heart-icon">{{ isFavorite ? '❤️' : '🤍' }}</span>
              {{ isFavorite ? 'En Favoritos' : 'Añadir a Favoritos' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="site.images && site.images.length > 1" class="gallery-section">
        <div class="gallery-scroll">
          <div class="image-wrapper" v-for="(img, idx) in nonCoverImages" :key="img.id">
            <img :src="img.url" class="gallery-image" :alt="img.alt_text" @click="openByIndex(idx + 1)">
            <button class="expand-btn" @click.stop="openByIndex(idx + 1)">🔍</button>
          </div>
        </div>
      </div>

      <hr>

      <section class="full-description-section">
        <h2>Detalle del Sitio</h2>

        <div>
          <p>
            {{ site.short_description }}
          </p>
          <p>
            {{ showFull ? site.description : None }}
          </p>
        </div>

        <button v-if="site.description" @click="toggleDescription" class="ver-mas-btn">
          {{ showFull ? 'Ver menos' : 'Ver más' }}
        </button>
      </section>


      <hr>
      <section class="map-section">
        <div class="map-card">
          <h3 class="map-title">📍 Ubicación</h3>
          <div id="site-map" class="map-container" style="height: 300px; width: 100%; border-radius: 12px;"></div>

        </div>
      </section>
      <hr>

      <section class="reviews-list">
        <h2>Últimas Reseñas</h2>
        <div v-if="reviewsFeatureDisabled" class="reviews-disabled-msg">
          ✖️ Las reseñas están desactivadas temporalmente.
        </div>
        <div v-else>
          <button v-if="userReview==null" class="write-review-btn" @click="handleWriteReview">
            ✍️ Escribir reseña
          </button>
          <button v-else class="write-review-btn" @click="handleWriteReview">
            ✍️ Editar mi reseña
          </button>

          <div v-if="showReviewModal" class="review-modal-overlay" @click="closeReviewModal">
            <div class="review-modal" @click.stop>

              <div class="review-modal-header">
                <h3 v-if="userReview==null">✍️ Escribir reseña</h3>
                <h3 v-else>✍️ Editar reseña</h3>
                <button class="close-btn" @click="closeReviewModal">✕</button>
              </div>

              <div class="review-modal-body">
                <label class="input-label">Calificación</label>
                <select  v-model="newReview.rating" class="input-select">
                  <option v-if="userReview==null" disabled value="">Selecciona…</option>
                  <option v-if="userReview!=null" :value="userReview.rating">{{ userReview.rating }} ⭐ (actual)</option>
                  <option v-for="n in 5" :key="n" :value="n">{{ n }} ⭐</option>
                </select>

                <label class="input-label">Comentario</label>
                <textarea v-if="userReview==null" v-model="newReview.content" class="input-textarea" rows="4"
                  placeholder="Escribe tu experiencia..."></textarea>
                  <textarea v-if="userReview!=null" v-model="newReview.content" class="input-textarea" rows="4">${{ userReview.comment }}</textarea>
              </div>

              <div class="review-modal-footer">
                <button class="primary-btn" @click="submitReviewModal">Enviar reseña</button>
                <button class="secondary-btn" @click="closeReviewModal">Cancelar</button>
              </div>

            </div>
          </div>

          <div v-if="isLoadingReviews" class="status-message">
            Cargando reseñas...
          </div>

          <!-- Error -->
          <div v-else-if="reviewsError" class="status-message error">
            ❌ {{ reviewsErrorMessage }}
          </div>

          <!-- Lista de reseñas -->
          <div v-else-if="reviews.length > 0" class="review-item" v-for="review in reviews" :key="review.id">
            <div class="review-header">
              <strong>
                <section>
                  {{ review.user_info?.nombre || 'Usuario Anónimo' }}

                  <button v-if="authStore.isLoggedIn &&
                    parseInt(review.user_id) === parseInt(authStore.userId)" class="modal-delete"
                    @click.stop="deleteReview(review.id)" aria-label="Eliminar">
                    🗑️
                  </button>
                </section>
              </strong>
              <span>⭐ {{ review.rating }}/5</span>
              <section>Comentario: {{ review.comment }}</section>
              <small class="review-date">{{ new Date(review.created_at).toLocaleDateString() }}</small>
            </div>
            <br></br>
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

          <!-- Sin reseñas -->
          <p v-if="totalReviews.length < 1" class="empty-message">
            Este sitio aún no tiene reseñas.
          </p>
        </div>
      </section>
    </section>

    <!-- Modal de Galería -->
    <div v-if="isModalOpen" class="image-modal" @click="closeModal">
      <button class="modal-close" @click.stop="closeModal" aria-label="Cerrar">✕</button>

      <button class="modal-nav left" @click.stop="prevImage" aria-label="Anterior">◀</button>
      <div class="modal-inner" @click.stop>
        <img :src="currentImage.url" class="modal-image" :alt="currentImage.alt_text" />
        <div class="modal-counter">{{ currentIndex + 1 }} / {{ imagesList.length }}</div>
      </div>
      <button class="modal-nav right" @click.stop="nextImage" aria-label="Siguiente">▶</button>
    </div>

    <div v-if="showLoginPrompt" class="login-modal-overlay" @click.self="showLoginPrompt = false">
        <div class="login-modal-box">
            <div class="login-modal-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
            </div>
            <h3 class="login-modal-title">Iniciá sesión para continuar</h3>
            <p class="login-modal-desc">Para agregar este sitio a tus favoritos necesitás iniciar sesión con Google.</p>
            <div class="login-modal-google">
                <button @click="handleModalLogin" class="modal-google-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="20" height="20">
                        <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                        <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                        <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                        <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.36-8.16 2.36-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                    </svg>
                    Iniciar sesión con Google
                </button>
            </div>
            <button @click="showLoginPrompt = false" class="login-modal-dismiss">Cancelar</button>
        </div>
    </div>
  </div>

  <div v-if="showLoginPromptReseña" class="login-modal-overlay" @click.self="showLoginPromptReseña = false">
        <div class="login-modal-box">
            <div class="login-modal-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
            </div>
            <h3 class="login-modal-title">Iniciá sesión para escribir una reseña</h3>
            <p class="login-modal-desc">Para compartir tu opinión sobre este sitio necesitás iniciar sesión con Google.</p>
            <div class="login-modal-google">
                <button @click="handleModalLogin" class="modal-google-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="20" height="20">
                        <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                        <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                        <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                        <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.36-8.16 2.36-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                    </svg>
                    Iniciar sesión con Google
                </button>
            </div>
            <button @click="showLoginPromptReseña = false" class="login-modal-dismiss">Cancelar</button>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted,defineExpose, nextTick, onBeforeUnmount, computed } from 'vue';
import { parseQuery, useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';
import BackButton from "@/components/BackButton.vue";
import { googleSdkLoaded } from 'vue3-google-login';
import "leaflet/dist/leaflet.css";

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


const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const { token } = storeToRefs(authStore);
const showFull = ref(false);
const toggleDescription = () => {
  showFull.value = !showFull.value;
};

const site = ref(null);
const isLoading = ref(true);
const error = ref(false);
const errorMessage = ref('');
const isFavorite = ref(false); 
const showLoginPrompt = ref(false);

const siteId = route.params.id;

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const userReview = ref(null);
const reviewRating = ref(5);
const reviewContent = ref("");
const newReview = ref({
  rating: reviewRating.value,
  content: reviewContent.value
});
const reviews = ref([]);
const totalReviews = ref(0);
const isLoadingReviews = ref(true);
const reviewsError = ref(false);
const reviewsErrorMessage = ref('');
const currentPage = ref(1);
const totalPages = ref(1);
const perPage = 25;
const showReviewModal = ref(false);
const showLoginPromptReseña = ref(false);

let _tokenClient = null

const handleModalLogin = () => _tokenClient?.requestAccessToken()
const isModalOpen = ref(false);
const currentIndex = ref(0);
const imagesList = ref([]);

const currentImage = computed(() => imagesList.value[currentIndex.value] || { url: '', alt_text: '' });
const nonCoverImages = computed(() => {
  if (!site.value || !site.value.images) return [];
  return site.value.images
    .filter(i => !i.is_cover)
    .map(i => ({
      ...i,
      alt_text: i.title || `Imagen del sitio ${site.value.name}`
    }));
});



const handleFavoriteAction = () => {
    if (!token.value) {
        
        showLoginPrompt.value = true;
    } else {
        
        toggleFavorite();
    }
};

function openByIndex(idx) {
  buildImagesListIfNeeded();
  if (!imagesList.value.length) return;
  if (idx < 0) idx = 0;
  if (idx >= imagesList.value.length) idx = imagesList.value.length - 1;
  currentIndex.value = idx;
  isModalOpen.value = true;
}

function buildImagesListIfNeeded() {
  if (!site.value) return;
  if (imagesList.value.length > 0) return;

  const list = [];

  if (site.value.cover_image) {
    list.push({
      url: site.value.cover_image.url || site.value.cover_image,
      alt_text: site.value.cover_image.title || site.value.name
    });
  }

  if (site.value.images && site.value.images.length) {
    for (const img of site.value.images) {
      if (!img.is_cover) {
        list.push({
          url: img.url,
          alt_text: img.title || site.value.name
        });
      }
    }
  }

  imagesList.value = list;
}
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchReviews();
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    fetchReviews();
  }
};

function closeModal() {
  isModalOpen.value = false;
}

function nextImage() {
  if (!imagesList.value.length) return;
  currentIndex.value = (currentIndex.value + 1) % imagesList.value.length;
}

function prevImage() {
  if (!imagesList.value.length) return;
  currentIndex.value = (currentIndex.value - 1 + imagesList.value.length) % imagesList.value.length;
}

function onKeydown(e) {
  if (!isModalOpen.value) return;
  if (e.key === 'Escape') closeModal();
  if (e.key === 'ArrowRight') nextImage();
  if (e.key === 'ArrowLeft') prevImage();
}

function handleWriteReview() {
  if (!token.value) {
        // Si no está autenticado, muestra el modal y pide iniciar sesión
        showLoginPromptReseña.value = true;
    } else {
       if (userReview.value != null) {
          newReview.value.rating = userReview.value.rating;
          newReview.value.content = userReview.value.comment;
        } else {
          reviewRating.value = 5;
          reviewContent.value = "";
  }

  showReviewModal.value = true;
}}

function closeLoginPromptReseña() {
  showLoginPrompt.value = false;
}
function closeReviewModal() {
  showReviewModal.value = false;
}

async function submitReviewModal() {
  if (!newReview.value.rating || !newReview.value.content) {
    alert("Completa todos los campos.");
    return;
  }

  await submitReview()

  showReviewModal.value = false;

  newReview.value.rating = "";
  newReview.value.content = "";
}
function cancelReview() {
  showReviewModal.value = false;
  newReview.value.rating = "";
  newReview.value.content = "";
}

import L from "leaflet";
import "leaflet/dist/leaflet.css";


delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
});




const map = ref(null);
const mapLoaded = ref(false);
function loadMap() {
  if (!site.value || mapLoaded.value) return;

  const lat = site.value.latitude;
  const lng = site.value.longitude;
  if (!lat || !lng) {
    console.warn("⚠ Este sitio no tiene coordenadas");
    return;
  }



  map.value = L.map("site-map").setView([lat, lng], 15);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "© OpenStreetMap contributors",
    }).addTo(map.value);

const tooltipText = `
    <strong>${site.value.name}</strong><br>
    ${site.value.short_description || ""}
  `;

  
  L.marker([lat, lng])
    .addTo(map.value)
    .bindTooltip(tooltipText, {
      permanent: false,  
      direction: "top",
    });
  mapLoaded.value = true;
}

const toggleFavorite = async () => {
    if (!token.value) {
        console.warn('Acción bloqueada: El usuario debe iniciar sesión para marcar favoritos.');
        return;
    }

    const isAdding = !isFavorite.value;
    const action = isAdding ? 'POST' : 'DELETE';
    const previousFavoriteState = isFavorite.value;

    
    const url = `${API_BASE_URL}/sites/${siteId}/favorite`;

    try {
       
        isFavorite.value = isAdding;

        const response = await fetch(url, { 
            method: action,
            headers: {
                'Authorization': `Bearer ${token.value}`,
                
            },
           
            // body: JSON.stringify({ site_id: siteId })
        });

        if (!response.ok) {
            
            isFavorite.value = previousFavoriteState;
            const errorData = await response.json().catch(() => ({}));
            console.error(`Error al ${isAdding ? 'añadir' : 'remover'} favorito:`, errorData.message || response.statusText);
        }

    } catch (err) {
        isFavorite.value = previousFavoriteState;
        console.error('Error de red al actualizar favoritos:', err);
    }
};

const fetchSiteDetail = async () => {
  isLoading.value = true;
  error.value = false;
  errorMessage.value = '';

  try {
    const url = `${API_BASE_URL}/sites/${siteId}`;
    const headers = {};

  
    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`;
    }

    const response = await fetch(url, { headers });

    if (response.status === 404) {
      errorMessage.value = `Sitio con ID ${siteId} no encontrado.`;
      error.value = true;
      return;
    }
    if (!response.ok) {
      throw new Error(`Error al obtener el sitio. Código: ${response.status}`);
    }

    const data = await response.json();
    site.value = data.data || data;

    imagesList.value = [];
    buildImagesListIfNeeded();

    await nextTick();
    setTimeout(loadMap, 50);

    
    if (site.value.is_favorite !== undefined) {
      isFavorite.value = site.value.is_favorite;
    }

  } catch (err) {
    errorMessage.value = `Hubo un error de red o del servidor: ${err.message}`;
    error.value = true;
  } finally {
    isLoading.value = false;
  }
};



const fetchUserInfo = async (userId) => {
  const url = `${API_BASE_URL}/internal/users/${userId}`;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      return null;
    }

    const user_info = await response.json();

    return user_info;

  } catch (err) {
    return null;
  }
};

const deleteReview = async (reviewId) => {
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

    const response = await fetch(`${API_BASE_URL}/sites/${siteId}/reviews/${reviewId}`, {
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


const submitReview = async () => {
  try {
    const authStore = useAuthStore();

    if (!authStore.isLoggedIn) {
      alert("Debes iniciar sesión para enviar una reseña.");
      return;
    }

    const authorizationToken = authStore.authHeader.Authorization;
    if (!authorizationToken) {
      alert("Error: No se encontró el token de autenticación.");
      return;
    }

    const payload = {
      rating: parseInt(newReview.value.rating),
      site_id: parseInt(siteId),
      comment: newReview.value.content,

    };

    let url, method;

    if (!userReview.value) {
      
      url = `${API_BASE_URL}/sites/${siteId}/reviews`;
      method = "POST";
    } else if(userReview.value!=null) {
      url = `${API_BASE_URL}/sites/${siteId}/reviews/${userReview.value.id}`;
      method = "PUT";

    }

    const response = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        "Authorization": authorizationToken
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      console.error("❌ Error creando/editando reseña:", data);
      alert(data.msg || data.error || JSON.stringify(data));
      return;
    }

    alert(
      !userReview.value
        ? "Reseña creada con éxito ✔️"
        : "Reseña editada con éxito ✨"
    );

    
    showReviewModal.value = false;


  } catch (error) {
    console.error("❌ Error en submitReview:", error);
    alert("Error de conexión o inesperado al enviar la reseña.");
  }
    currentPage.value = 1;
    await fetchReviews();
};




const fetchCheckReview = async () => {
  if (!authStore.isLoggedIn) {
    showLoginPromptReseña.value = true;
    return;
  }

  const url = `${API_BASE_URL}/sites/${siteId}/reviews/check`;
  const method = "GET";
  const response = fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: authStore.authHeader.Authorization,
    }
  })
  return response;
};


function aprobadas(reviewsList){
  return reviewsList.filter(review => review.status === 'APROBADA');
}



const fetchReviews = async () => {
  isLoadingReviews.value = true;
  reviewsError.value = false;
  reviewsErrorMessage.value = '';
  try {
    const url = `${API_BASE_URL}/sites/${siteId}/reviews?page=${currentPage.value}&per_page=${perPage}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Error al obtener reseñas. Código: ${response.status}`);
    }

    const data = await response.json();
    totalPages.value = data.total_pages || 1;
    totalReviews.value = data.total || 0;
    const reviewsData = data.reviews || [];

    for (const review of reviewsData) {
      if (review.user_id) {
        review.user_info = await fetchUserInfo(review.user_id);
      } else {
        review.user_info = null;
      }
      if (userReview.value==null && parseInt(review.user_info.id) == parseInt(authStore.userId)) {
        userReview.value = review;
      }
    }
    const check = await fetchCheckReview();
    if (check) {
      const checkData = await check.json();
      if (checkData.review) {
        userReview.value = checkData.review;
      }
    }

    console.log(userReview.value);
    reviews.value = reviewsData;
    reviews.value = aprobadas(reviews.value);


  } catch (err) {
    console.error('🔥 Error al cargar reseñas:', err);
    reviewsErrorMessage.value = err.message;
    reviewsError.value = true;
  } finally {
    isLoadingReviews.value = false;
  }
};
onMounted(() => {
  googleSdkLoaded((google) => {
    _tokenClient = google.accounts.oauth2.initTokenClient({
      client_id: '567138964451-npnnabs0o6lc434dgtj0fqp8a904cd35.apps.googleusercontent.com',
      scope: 'email profile',
      callback: async (response) => {
        if (response.error) return
        const success = await authStore.loginWithGoogle(response)
        if (success) {
          showLoginPrompt.value = false
          showLoginPromptReseña.value = false
        }
      }
    })
  })

  fetchReviewsFlag();
  if (siteId) {
    fetchSiteDetail();
    fetchReviews();
  }
  else {
    errorMessage.value = 'ID del sitio no especificado en la URL.';
    error.value = true;
    isLoading.value = false;
  }
  window.addEventListener('keydown', onKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown);
});


</script>

<style scoped>

/* Login Modal */
.login-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(17,24,39,0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9990;
  padding: 20px;
}

.login-modal-box {
  background: white;
  border-radius: 20px;
  padding: 40px 32px 28px;
  max-width: 360px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  text-align: center;
  animation: modal-pop 0.22s cubic-bezier(0.34,1.56,0.64,1);
}

@keyframes modal-pop {
  from { opacity: 0; transform: scale(0.92) translateY(10px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}

.login-modal-icon {
  width: 60px;
  height: 60px;
  background: var(--color-primary-light, #DBEAFE);
  color: var(--color-primary, #1E3A8A);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.login-modal-title {
  font-family: 'Nunito', sans-serif;
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--text-primary, #111827);
  margin: 0 0 10px;
}

.login-modal-desc {
  font-size: 0.9rem;
  color: var(--text-secondary, #6B7280);
  line-height: 1.5;
  margin: 0 0 24px;
}

.login-modal-google {
  display: flex;
  justify-content: center;
  margin-bottom: 14px;
}

.login-modal-dismiss {
  background: none;
  border: none;
  color: var(--text-muted, #9CA3AF);
  font-size: 0.85rem;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 6px;
  transition: color 0.15s;
}

.login-modal-dismiss:hover {
  color: var(--text-secondary, #6B7280);
}

.modal-google-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: white;
  border: 1px solid #dadce0;
  border-radius: 6px;
  padding: 11px 24px;
  font-size: 0.95rem;
  font-weight: 500;
  color: #3c4043;
  cursor: pointer;
  width: 100%;
  transition: box-shadow 0.15s, background-color 0.15s;
}

.modal-google-btn:hover {
  background-color: #f8f9fa;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
}

.btn-primary {
  background-color: var(--color-primary, #1E3A8A);
  color: white;
  padding: 9px 18px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-primary:hover { background-color: var(--color-primary-dark, #172554); }

.btn-cancel {
  background-color: var(--surface-2, #F3F4F6);
  color: var(--text-primary, #111827);
  padding: 9px 18px;
  border-radius: 8px;
  border: 1px solid var(--border, #E5E7EB);
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-cancel:hover { background-color: var(--border, #E5E7EB); }

/* Page layout */
.site-detail-page {
  padding: 24px 20px 60px;
  max-width: 1200px;
  margin: 0 auto;
}

.detail-header {
  text-align: left;
  margin-bottom: 20px;
}

.detail-header h1 {
  font-family: 'Nunito', sans-serif;
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 800;
  color: var(--text-primary, #111827);
  margin-bottom: 6px;
}

.rating-badge {
  display: inline-block;
  margin-top: 8px;
  background: var(--color-primary-light, #DBEAFE);
  color: var(--color-primary-dark, #172554);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.88rem;
  font-weight: 600;
}

.site-cover-image {
  width: 100%;
  height: auto;
  max-height: 400px;
  object-fit: cover;
  border-radius: var(--radius-md, 12px);
  cursor: zoom-in;
}

.cover-wrapper {
  position: relative;
  display: block;
}

.expand-button.cover {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--border, #E5E7EB);
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
  z-index: 5;
  transition: background 0.15s;
}

.expand-button.cover:hover { background: white; }

.map-container {
  height: 300px;
  width: 100%;
  border-radius: var(--radius-md, 12px);
}

.page-button {
  background-color: var(--surface-2, #F3F4F6);
  border: 1px solid var(--border, #E5E7EB);
  border-radius: 6px;
  color: var(--text-secondary, #6B7280);
  padding: 6px 14px;
  font-size: 14px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: 0.15s;
}

.page-button:hover { background-color: var(--border, #E5E7EB); }

.page-button.active {
  background-color: var(--color-primary-light, #DBEAFE);
  border-color: var(--color-primary, #1E3A8A);
  color: var(--color-primary-dark, #172554);
  font-weight: 600;
}

.page-button:disabled {
  background-color: var(--surface, #F9FAFB);
  color: var(--text-muted, #9CA3AF);
  cursor: not-allowed;
  opacity: 0.7;
}

.login-warning {
  text-align: center;
  padding: 20px;
  margin: 25px auto;
  background: var(--surface, #F9FAFB);
  border: 1px solid var(--border, #E5E7EB);
  border-radius: var(--radius-md, 12px);
  max-width: 450px;
}

.login-text {
  font-size: 1rem;
  margin-bottom: 14px;
  color: var(--text-secondary, #6B7280);
}

.login-btn {
  background: var(--color-primary, #1E3A8A);
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s, transform 0.1s;
}
.login-btn:hover { background: var(--color-primary-dark, #172554); }
.login-btn:active { transform: scale(0.97); }

.description-section { padding: 0; }

.full-description-section {
  margin-top: 20px;
  padding: 15px 0;
}

.tags-section { margin-top: 15px; }

.tag-badge {
  display: inline-block;
  background-color: var(--color-primary-light, #DBEAFE);
  color: var(--color-primary-dark, #172554);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.83rem;
  font-weight: 500;
  margin-right: 5px;
  margin-bottom: 4px;
  text-decoration: none;
  transition: background 0.15s;
}

.tag-badge:hover { background-color: var(--color-primary, #1E3A8A); color: white; }

/* Favorite button */
.action-buttons { margin-top: 20px; }

.favorite-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: var(--radius-sm, 8px);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid var(--border, #E5E7EB);
  background-color: white;
  color: var(--text-secondary, #6B7280);
  font-size: 0.9rem;
}

.favorite-button:hover {
  border-color: var(--color-primary, #1E3A8A);
  color: var(--color-primary, #1E3A8A);
  transform: translateY(-1px);
}

.favorite-button.is-favorite {
  background-color: #FEE2E2;
  color: #991B1B;
  border-color: #FECACA;
}

.heart-icon {
  font-size: 1.1em;
  transition: transform 0.3s;
}

.favorite-button.is-favorite .heart-icon {
  animation: pulse 0.5s ease-out;
}

@keyframes pulse {
  0%   { transform: scale(1); }
  50%  { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.login-tip {
  font-style: italic;
  color: var(--text-muted, #9CA3AF);
  font-size: 0.88rem;
}

.review-form-section {
  margin-top: 24px;
  padding: 20px;
  border: 1px solid var(--border, #E5E7EB);
  border-radius: var(--radius-md, 12px);
  background: var(--surface, #F9FAFB);
}

.review-form h3 {
  margin-bottom: 14px;
  font-family: 'Nunito', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
}

.write-review-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  border-radius: var(--radius-sm, 8px);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid var(--color-primary, #1E3A8A);
  background-color: white;
  color: var(--color-primary, #1E3A8A);
  font-size: 0.9rem;
}

.write-review-btn:hover {
  background-color: var(--color-primary, #1E3A8A);
  color: white;
  transform: translateY(-1px);
}

/* Review modal */
.review-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9998;
  animation: fadeIn 0.2s ease;
}

.review-modal {
  width: 400px;
  background: white;
  border-radius: var(--radius-lg, 16px);
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  animation: popIn 0.22s ease;
}

.review-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border, #E5E7EB);
}

.review-modal-header h3 {
  margin: 0;
  font-family: 'Nunito', sans-serif;
  font-size: 1.05rem;
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

.review-modal-body { margin-top: 4px; }

.input-label {
  display: block;
  margin-bottom: 5px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary, #6B7280);
}

.input-select,
.input-textarea {
  width: 100%;
  padding: 9px 12px;
  border-radius: var(--radius-sm, 8px);
  border: 1px solid var(--border, #E5E7EB);
  font-size: 0.9rem;
  font-family: 'Inter', sans-serif;
  transition: border-color 0.2s;
  margin-bottom: 14px;
  outline: none;
  background: white;
  color: var(--text-primary, #111827);
}

.input-select:focus,
.input-textarea:focus {
  border-color: var(--color-primary, #1E3A8A);
  box-shadow: 0 0 0 3px rgba(30,58,138,0.1);
}

.review-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 4px;
}

.primary-btn {
  background: var(--color-primary, #1E3A8A);
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius-sm, 8px);
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: background 0.2s;
}
.primary-btn:hover { background: var(--color-primary-dark, #172554); }

.secondary-btn {
  background: var(--surface-2, #F3F4F6);
  color: var(--text-primary, #111827);
  padding: 10px 20px;
  border: 1px solid var(--border, #E5E7EB);
  border-radius: var(--radius-sm, 8px);
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: background 0.2s;
}
.secondary-btn:hover { background: var(--border, #E5E7EB); }

@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.93); }
  to   { opacity: 1; transform: scale(1); }
}

@media (min-width: 768px) {
  .site-content > .detail-header { margin-bottom: 28px; }
  .main-info-grid {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 40px;
  }
  .detail-header { text-align: left; }
}

/* Gallery */
.gallery-section { width: 100%; margin-top: 20px; }

.gallery-scroll {
  display: flex;
  overflow-x: auto;
  gap: 12px;
  padding: 8px 0;
}

.image-wrapper {
  position: relative;
  display: inline-block;
  flex-shrink: 0;
}

.gallery-image {
  width: 220px;
  height: 150px;
  object-fit: cover;
  border-radius: var(--radius-sm, 8px);
  border: 1px solid var(--border, #E5E7EB);
  cursor: zoom-in;
  transition: transform 0.2s;
}

.gallery-image:hover { transform: scale(1.03); }

.expand-btn {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background-color: rgba(0,0,0,0.65);
  color: white;
  border: none;
  padding: 5px 8px;
  font-size: 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}
.expand-btn:hover { background-color: rgba(0,0,0,0.85); }

/* Image lightbox */
.image-modal {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.88);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-inner {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 95%;
  max-height: 95%;
}

.modal-delete {
  background: rgba(255,255,255,0.85);
  border: none;
  font-size: 18px;
  padding: 5px 8px;
  cursor: pointer;
  border-radius: 50%;
  transition: background 0.2s;
}
.modal-delete:hover { background: rgba(255,80,80,0.3); }

.modal-image {
  max-width: 100%;
  max-height: 100%;
  border-radius: 10px;
  object-fit: contain;
}

.modal-nav {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  color: white;
  width: 44px; height: 44px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10000;
  font-size: 18px;
}
.modal-nav.left  { left: 18px; }
.modal-nav.right { right: 18px; }

.modal-close {
  position: fixed;
  top: 18px; right: 18px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  color: white;
  width: 40px; height: 40px;
  border-radius: 8px;
  cursor: pointer;
  z-index: 10000;
  font-size: 18px;
}

.modal-counter {
  position: absolute;
  bottom: 12px; right: 12px;
  background: rgba(0,0,0,0.5);
  color: white;
  padding: 6px 8px;
  border-radius: 8px;
  font-size: 0.88rem;
}

.ver-mas-btn {
  margin-top: 10px;
  background: none;
  color: var(--color-primary, #1E3A8A);
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.ver-mas-btn:hover { color: var(--color-primary-dark, #172554); }

.reviews-disabled-msg {
  padding: 12px 16px;
  background: #FEF3C7;
  border: 1px solid #FDE68A;
  border-radius: var(--radius-sm, 8px);
  font-size: 0.9rem;
  color: #92400E;
  margin-bottom: 16px;
}

.status-message {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary, #6B7280);
  font-size: 1rem;
}

.status-message.error {
  color: #991B1B;
  background: #FEF2F2;
  border-radius: var(--radius-md, 12px);
  border: 1px solid #FECACA;
  margin: 40px auto;
  max-width: 600px;
}
</style>

