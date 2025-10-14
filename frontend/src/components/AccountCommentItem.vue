<template>
  <div class="account-comment-item">
    <div class="comment-content">
      <p>{{ comment.comment_text }}</p>
      <div class="comment-meta">
        <span class="project">Project: {{ comment.project_id }}</span>
        <span class="date">{{ formatDate(comment.created_at) }}</span>
      </div>
    </div>
    
    <div class="comment-actions">
      <button @click="toggleEdit" class="action-btn">
        {{ t('ProjectComments.edit') }}
      </button>
      <button @click="deleteComment" class="action-btn delete">
        {{ t('ProjectComments.delete') }}
      </button>
    </div>

    <!-- Форма редактирования -->
    <div v-if="showEditForm" class="edit-form">
      <textarea v-model="editText" rows="3"></textarea>
      <div class="form-actions">
        <button @click="saveEdit" class="submit-btn">
          {{ t('ProjectComments.save') }}
        </button>
        <button @click="cancelEdit" class="cancel-btn">
          {{ t('ProjectComments.cancel') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT),
})

const props = defineProps({
  comment: Object
})

const emit = defineEmits(['update', 'delete'])

const showEditForm = ref(false)
const editText = ref(props.comment.comment_text)

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + 
    date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const toggleEdit = () => {
  showEditForm.value = !showEditForm.value
  editText.value = props.comment.comment_text
}

const saveEdit = async () => {
  if (!editText.value.trim()) return
  
  try {
    await apiClient.put(
      `${import.meta.env.VITE_API_CONTENT_COMMENTS}/${props.comment.id}`,
      {
        new_text: editText.value
      }
    )
    showEditForm.value = false
    emit('update', props.comment.id, editText.value)
  } catch (err) {
    console.error('Ошибка редактирования комментария:', err)
  }
}

const cancelEdit = () => {
  editText.value = props.comment.comment_text
  showEditForm.value = false
}

const deleteComment = async () => {
  if (!confirm('Delete this comment?')) return
  
  try {
    await apiClient.delete(
      `${import.meta.env.VITE_API_CONTENT_COMMENTS}/${props.comment.id}`
    )
    emit('delete', props.comment.id)
  } catch (err) {
    console.error('Ошибка удаления комментария:', err)
  }
}
</script>

<style scoped>
.account-comment-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  background: var(--hover-button-background-color);
}

.comment-content p {
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.comment-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #666;
}

.project {
  font-weight: bold;
}

.comment-actions {
  margin-top: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 0.875rem;
  margin-right: 1rem;
}

.action-btn:hover {
  text-decoration: underline;
}

.action-btn.delete {
  color: #dc3545;
}

.edit-form {
  margin-top: 1rem;
}

.edit-form textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
}

.form-actions {
  margin-top: 0.5rem;
  display: flex;
  gap: 0.5rem;
}

.submit-btn,
.cancel-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn {
  background: var(--button-background-color, #007bff);
  color: white;
}

.cancel-btn {
  background: #6c757d;
  color: white;
}
</style>