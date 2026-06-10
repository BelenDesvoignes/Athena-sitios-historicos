<template>
  <button @click="goBack" class="back-btn">
    ⬅️ Volver
  </button>
</template>

<script>
export default {
  name: "BackButton",
  methods: {
    goBack() {
      if (window.history.length > 1) {
        this.$router.back()
      } else {
        this.$router.push(this.fallbackRoute)
      }
    }
  },
  props: {
    fallbackRoute: {
      type: String,
      default: "/"
    }
  }
}
</script>

<style scoped>
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: var(--radius-sm, 8px);
  border: 1px solid var(--border, #E5E7EB);
  cursor: pointer;
  background-color: white;
  color: var(--text-secondary, #6B7280);
  font-size: 0.88rem;
  font-weight: 500;
  font-family: 'Inter', sans-serif;
  transition: background-color 0.15s, color 0.15s;
  margin-bottom: 20px;
}

.back-btn:hover {
  background-color: var(--color-primary-light, #CCFBF1);
  color: var(--color-primary-dark, #0F766E);
  border-color: var(--color-primary, #0D9488);
}
</style>
