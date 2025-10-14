<template>
  <div class="comment-item" :style="{ marginLeft: `${depth * 20}px` }">
    <div class="comment-header">
      <span class="author">{{ comment.author_email }}</span>
      <span class="date">{{ formatDate(comment.created_at) }}</span>
    </div>
    
    <div class="comment-content">
      <p>{{ comment.comment_text }}</p>
    </div>

    <div class="comment-actions">
      <button @click="toggleReply" class="action-btn">
        {{ t('ProjectComments.reply') }}
      </button>
      <button v-if="isAuthor" @click="toggleEdit" class="action-btn">
        {{ t('ProjectComments.edit') }}
      </button>
      <button v-if="isAuthor" @click="deleteComment" class="action-btn delete">
        {{ t('ProjectComments.delete') }}
      </button>
    </div>

    <!-- Форма ответа -->
    <div v-if="showReplyForm" class="reply-form">
      <textarea v-model="replyText" rows="2"></textarea>
      <div class="form-actions">
        <button @click="submitReply" class="comment-submit-btn">
          {{ t('ProjectComments.reply') }}
        </button>
        <button @click="cancelReply" class="cancel-btn">
          {{ t('ProjectComments.cancel') }}
        </button>
      </div>
    </div>

    <!-- Форма редактирования -->
    <div v-if="showEditForm" class="edit-form">
      <textarea v-model="editText" rows="3"></textarea>
      <div class="form-actions">
        <button @click="saveEdit" class="comment-submit-btn">
          {{ t('ProjectComments.save') }}
        </button>
        <button @click="cancelEdit" class="cancel-btn">
          {{ t('ProjectComments.cancel') }}
        </button>
      </div>
    </div>

    <!-- Вложенные комментарии -->
    <div v-if="replies.length" class="replies">
      <CommentItem 
        v-for="reply in replies" 
        :key="reply.id"
        :comment="reply"
        :replies="getReplies(reply.id)"
        :depth="depth + 1"
        @reply="$emit('reply', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  comment: Object,
  replies: Array,
  depth: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['reply'])

// Локальные состояния
const showReplyForm = ref(false)
const showEditForm = ref(false)
const replyText = ref('')
const editText = ref(props.comment.comment_text)

// Проверка авторства (заглушка)
const isAuthor = computed(() => props.comment.author_id === 'current_user')

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const toggleReply = () => {
  showReplyForm.value = !showReplyForm.value
  showEditForm.value = false
}

const toggleEdit = () => {
  showEditForm.value = !showEditForm.value
  showReplyForm.value = false
  editText.value = props.comment.comment_text
}

const submitReply = () => {
  if (replyText.value.trim()) {
    emit('reply', props.comment, replyText.value)
    replyText.value = ''
    showReplyForm.value = false
  }
}

const cancelReply = () => {
  replyText.value = ''
  showReplyForm.value = false
}

const saveEdit = () => {
  if (editText.value.trim()) {
    // Логика сохранения редактирования
    console.log('Save edited comment:', editText.value)
    showEditForm.value = false
  }
}

const cancelEdit = () => {
  editText.value = props.comment.comment_text
  showEditForm.value = false
}

const deleteComment = () => {
  if (confirm('Delete this comment?')) {
    // Логика удаления
    console.log('Delete comment:', props.comment.id)
  }
}

const getReplies = (parentId) => {
  return props.replies.filter(reply => reply.parent_comment_id === parentId)
}
</script>

<style scoped>
.comment-item {
  border-bottom: 1px solid #eee;
  padding: 0.375rem 0;
  font-size: 0.875rem;
  border-bottom: none;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.125rem;
  align-items: center;
}

.author {
  font-weight: bold;
  font-size: 0.875rem;
  background: var(--selection-color, #e3f2fd);
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  color: var(--text-color, #333);
  margin: 0;
}

.date {
  color: #666;
  font-size: 0.75rem;
}

.comment-content {
  padding: 0 0.5rem;
  margin-top: 0.25rem;
}

.comment-content p {
  margin: 0.125rem 0;
  line-height: 1.3;
}

.comment-actions {
  margin-top: 0.25rem;
}

.action-btn {
  background: none;
  border: none;
  color: var(--text-color, #007bff);
  cursor: pointer;
  font-size: 0.75rem;
}

.action-btn:hover {
  text-decoration: underline;
}

.action-btn.delete {
  color: #dc3545;
}

.reply-form,
.edit-form {
  margin-top: 0.375rem;
}

.reply-form textarea,
.edit-form textarea {
  width: 100%;
  padding: 0.25rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
  font-size: 0.875rem;
}

.form-actions {
  margin-top: 0.25rem;
  display: flex;
  gap: 0.375rem;
}

.comment-submit-btn,
.cancel-btn {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
}

.comment-submit-btn {
  background: var(--button-background-color, red) !important;
  color: white;
}

.cancel-btn {
  background: #6c757d;
  color: white;
}

.replies {
  margin-top: 0.375rem;
}
</style>