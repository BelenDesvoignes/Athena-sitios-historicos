<template>
  <router-link :to="`/sitios/${site.id}`" class="site-card">
    <div class="card-image-container">
      <img
        v-if="site.image_url"
        :src="site.image_url"
        :alt="site.image_title || site.name"
        class="card-image"
      />
      <div v-else class="card-image-placeholder">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3 3h18M3 21h18M3 3v18M21 3v18"/></svg>
        <span>Sin fotografía</span>
      </div>
    </div>
    <div class="card-body">
      <h3 class="card-title">{{ site.name }}</h3>
      <p class="card-location">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
        {{ site.city }}, {{ site.province }}
      </p>
      <div class="card-meta">
        <span class="conservation-badge" :class="conservationClass">{{ site.state_of_conservation }}</span>
      </div>
      <div v-if="site.tags && site.tags.length" class="tags">
        <span v-for="tag in site.tags.slice(0, 3)" :key="tag.id" class="tag">{{ tag.name }}</span>
        <span v-if="site.tags.length > 3" class="tag tag-more">+{{ site.tags.length - 3 }}</span>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  site: { type: Object, required: true }
});

const conservationClass = computed(() => {
  const map = {
    EXCELENTE: 'badge-excellent',
    BUENO: 'badge-good',
    REGULAR: 'badge-regular',
    MALO: 'badge-bad',
  };
  return map[props.site.state_of_conservation] || 'badge-default';
});
</script>

<style scoped>
.site-card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: var(--text-primary, #111827);
  background: white;
  border: 1px solid var(--border, #E5E7EB);
  border-radius: var(--radius-lg, 16px);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.site-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary, #0D9488);
}

.card-image-container {
  width: 100%;
  height: 190px;
  overflow: hidden;
  background-color: var(--surface-2, #F3F4F6);
  flex-shrink: 0;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transition: transform 0.3s ease;
}

.site-card:hover .card-image {
  transform: scale(1.04);
}

.card-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--text-muted, #9CA3AF);
  font-size: 0.85rem;
}

.card-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex-grow: 1;
}

.card-title {
  font-family: 'Nunito', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
  line-height: 1.3;
  margin: 0;
}

.card-location {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  color: var(--text-secondary, #6B7280);
  margin: 0;
  fill: currentColor;
}

.card-meta {
  margin-top: 2px;
}

.conservation-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.badge-excellent { background-color: #D1FAE5; color: #065F46; }
.badge-good      { background-color: #CCFBF1; color: #0F766E; }
.badge-regular   { background-color: #FEF3C7; color: #92400E; }
.badge-bad       { background-color: #FEE2E2; color: #991B1B; }
.badge-default   { background-color: var(--surface-2, #F3F4F6); color: var(--text-secondary, #6B7280); }

.tags {
  margin-top: 6px;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tag {
  background: var(--color-primary-light, #CCFBF1);
  color: var(--color-primary-dark, #0F766E);
  padding: 3px 8px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 500;
}

.tag-more {
  background: var(--surface-2, #F3F4F6);
  color: var(--text-muted, #9CA3AF);
}
</style>
