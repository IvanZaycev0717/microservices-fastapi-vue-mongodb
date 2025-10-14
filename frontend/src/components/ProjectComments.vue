<template>
  <div class="comments-section">
    <h4>{{ t('ProjectComments.title') }}</h4>
    
    <!-- Форма добавления комментария -->
    <div class="comment-form">
      <textarea 
        v-model="newComment" 
        :placeholder="t('ProjectComments.placeholder')"
        rows="3"
      ></textarea>
      <button @click="addComment">{{ t('ProjectComments.add') }}</button>
    </div>

    <div class="comments-list">
      <CommentItem 
        v-for="comment in rootComments" 
        :key="comment.id"
        :comment="comment"
        :replies="getReplies(comment.id)"
        @reply="handleReply"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import CommentItem from '@components/CommentItem.vue'
import axios from 'axios'

const { t } = useI18n()

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT),
})

const props = defineProps({
  projectId: {
    type: String,
    required: true
  }
})

const comments = ref([])
const loading = ref(false)
const newComment = ref('')

const fetchComments = async (projectId) => {
  try {
    loading.value = true
    const response = await apiClient.get(`${import.meta.env.VITE_API_CONTENT_COMMENTS}/project/${projectId}`)
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
    .filter(comment => comment.parent_comment_id === null)
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
)

const getReplies = (parentId) => 
  comments.value
    .filter(comment => comment.parent_comment_id === parentId)
    .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))

const addComment = () => {
  if (!newComment.value.trim()) return
  // TODO: Реализовать POST запрос
  console.log('Add comment:', newComment.value)
  newComment.value = ''
}

const handleReply = (parentComment, replyText) => {
  // TODO: Реализовать POST запрос с parent_comment_id
  console.log('Reply to comment:', parentComment.id, replyText)
}

watch(() => props.projectId, (newProjectId) => {
  if (newProjectId) {
    fetchComments(newProjectId)
  }
}, { immediate: true })
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
  color: var(--text-color);
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.comments-list {
  max-height: 400px;
  overflow-y: auto;
}
</style>