<template>
  <div class="AccountView">
    <h2>{{ t('AccountView.title') }}</h2>
    <p>{{ t('AccountView.description') }}</p>
    
    <div class="comments-list">
      <AccountCommentItem 
        v-for="comment in userComments"
        :key="comment.id"
        :comment="comment"
        @update="handleUpdate"
        @delete="handleDelete"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@stores/authStore.js'
import axios from 'axios'
import createAuthInterceptor from '@utils/axiosInterceptor.js'
import AccountCommentItem from '@components/AccountCommentItem.vue'

const { t } = useI18n()
const authStore = useAuthStore()

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT),
})

// Применяем interceptor к нашему экземпляру axios
createAuthInterceptor(apiClient)

const userComments = ref([])
const loading = ref(false)

const fetchUserComments = async () => {
  try {
    loading.value = true
    const response = await apiClient.get(`${import.meta.env.VITE_API_CONTENT_COMMENTS}/my`)
    userComments.value = response.data.comments || []
  } catch (err) {
    console.error('Ошибка загрузки комментариев:', err)
    userComments.value = []
  } finally {
    loading.value = false
  }
}

const handleUpdate = (commentId, newText) => {
  const comment = userComments.value.find(c => c.id === commentId)
  if (comment) {
    comment.comment_text = newText
  }
}

const handleDelete = (commentId) => {
  userComments.value = userComments.value.filter(c => c.id !== commentId)
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchUserComments()
  }
})
</script>

<style scoped>
.AccountView {
  padding: 1rem;
  overflow: auto;
}

.comments-list {
  max-width: 800px;
  margin: 0 auto;
}
</style>