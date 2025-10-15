<template>
  <div class="comments-section">
    <h4>{{ t('ProjectComments.title') }}</h4>

    <!-- Форма добавления комментария -->
    <div class="comment-form" v-if="authStore.isAuthenticated">
      <textarea
        v-model="newComment"
        :placeholder="t('ProjectComments.placeholder')"
        rows="3"
      ></textarea>
      <button @click="addComment">{{ t('ProjectComments.add') }}</button>
    </div>
    <div v-else class="login-prompt">
      <p>{{ t('ProjectComments.loginToComment') }}</p>
    </div>

    <div class="comments-list">
      <CommentItem
        v-for="comment in rootComments"
        :key="comment.id"
        :comment="comment"
        :replies="getReplies(comment.id)"
        @reply="handleReply"
        @update="handleUpdate"
        @delete="handleDelete"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import CommentItem from '@components/CommentItem.vue'
import axios from 'axios'
import createAuthInterceptor from '@utils/axiosInterceptor.js'
import { useAuthStore } from '@stores/authStore.js'

const { t } = useI18n()
const authStore = useAuthStore()

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT),
})

createAuthInterceptor(apiClient)

const props = defineProps({
  projectId: {
    type: String,
    required: true,
  },
})

const comments = ref([])
const loading = ref(false)
const newComment = ref('')

const fetchComments = async (projectId) => {
  try {
    loading.value = true
    const response = await apiClient.get(
      `${import.meta.env.VITE_API_CONTENT_COMMENTS}/project/${projectId}`,
    )
    comments.value = response.data.comments || []
  } catch (err) {
    console.error('Ошибка загрузки комментариев:', err)
    comments.value = []
  } finally {
    loading.value = false
  }
}

const rootComments = computed(() =>
  [...comments.value]
    .filter((comment) => comment.parent_comment_id === null)
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at)),
)

const getReplies = (parentId) =>
  comments.value
    .filter((comment) => comment.parent_comment_id === parentId)
    .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))

const addComment = async () => {
  if (!newComment.value.trim()) return

  try {
    const response = await apiClient.post(import.meta.env.VITE_API_CONTENT_COMMENTS, {
      project_id: props.projectId,
      comment_text: newComment.value,
    })

    await fetchComments(props.projectId)
    newComment.value = ''
  } catch (err) {
    console.error('Ошибка добавления комментария:', err)
  }
}

const handleReply = async (parentComment, replyText) => {
  try {
    const response = await apiClient.post(import.meta.env.VITE_API_CONTENT_COMMENTS, {
      project_id: props.projectId,
      comment_text: replyText,
      parent_comment_id: parentComment.id,
    })

    const newComment = {
      id: response.data.comment_id,
      project_id: props.projectId,
      author_id: authStore.user?.id,
      author_email: authStore.user?.email,
      comment_text: replyText,
      created_at: new Date().toISOString(),
      parent_comment_id: parentComment.id,
      likes: 0,
      dislikes: 0,
    }

    comments.value.push(newComment)
  } catch (err) {
    console.error('Ошибка добавления ответа:', err)
  }
}

const handleUpdate = (commentId, newText) => {
  const updateNested = (comments) => {
    for (let i = 0; i < comments.length; i++) {
      if (comments[i].id === commentId) {
        comments[i].comment_text = newText
        return true
      }
    }
    return false
  }

  updateNested(comments.value)
}

const handleDelete = async (commentId) => {
  try {
    comments.value = comments.value.filter((c) => c.id !== commentId)
  } catch (err) {
    console.error('Ошибка удаления комментария:', err)
  }
}

watch(
  () => props.projectId,
  (newProjectId) => {
    if (newProjectId) {
      fetchComments(newProjectId)
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.comments-section {
  padding: 1rem;
  border-left: 1px solid #ddd;
  height: 100%;
}

.comment-form {
  margin-bottom: 1rem;
}

.comment-form textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
}

.comment-form button {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--button-background-color, #007bff);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.comments-list {
  max-height: 400px;
  overflow-y: auto;
}
</style>
