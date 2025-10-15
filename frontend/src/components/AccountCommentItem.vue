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
      <button v-if="!showDeleteConfirm" @click="toggleEdit" class="action-btn">
        {{ t('ProjectComments.edit') }}
      </button>

      <!-- Кнопка удаления -->
      <button v-if="!showDeleteConfirm" @click="showDeleteConfirm = true" class="action-btn delete">
        {{ t('ProjectComments.delete') }}
      </button>

      <!-- Подтверждение удаления -->
      <div v-if="showDeleteConfirm" class="delete-confirm">
        <span class="confirm-text">{{ t('Comment.deleteConfirm') }}</span>
        <button @click="performDelete" class="confirm-btn delete">
          {{ t('Comment.delete') }}
        </button>
        <button @click="showDeleteConfirm = false" class="confirm-btn cancel">
          {{ t('Comment.cancel') }}
        </button>
      </div>
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
import createAuthInterceptor from '@utils/axiosInterceptor.js'

const { t } = useI18n()

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT),
})

createAuthInterceptor(apiClient)

const props = defineProps({
  comment: Object,
})

const emit = defineEmits(['update', 'delete'])

const showEditForm = ref(false)
const showDeleteConfirm = ref(false)
const editText = ref(props.comment.comment_text)

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return (
    date.toLocaleDateString() +
    ' ' +
    date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  )
}

const toggleEdit = () => {
  showEditForm.value = !showEditForm.value
  editText.value = props.comment.comment_text
}

const saveEdit = async () => {
  if (!editText.value.trim()) return

  try {
    await apiClient.put(`${import.meta.env.VITE_API_CONTENT_COMMENTS}/${props.comment.id}`, {
      new_text: editText.value,
    })
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

const performDelete = async () => {
  try {
    await apiClient.delete(`${import.meta.env.VITE_API_CONTENT_COMMENTS}/${props.comment.id}`)
    emit('delete', props.comment.id)
    showDeleteConfirm.value = false
  } catch (err) {
    console.error('Ошибка удаления комментария:', err)
    showDeleteConfirm.value = false
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

.delete-confirm {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.confirm-text {
  font-size: 0.875rem;
  color: #666;
}

.confirm-btn {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
}

.confirm-btn.delete {
  background: #dc3545;
  color: white;
}

.confirm-btn.cancel {
  background: #6c757d;
  color: white;
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
