<template>
  <div class="comment-item" :style="{ marginLeft: `${level * 20}px` }">
    <q-card class="comment-card q-mb-sm">
      <q-card-section class="q-pa-sm">
        <div class="row items-center justify-between">
          <div class="text-caption text-weight-medium">
            {{ comment.author_email }}
          </div>
          <div class="text-caption text-grey">
            {{ formatDate(comment.created_at) }}
          </div>
        </div>
        
        <!-- Режим просмотра -->
        <div v-if="!isEditing" class="comment-text q-mt-xs">
          {{ comment.comment_text }}
        </div>

        <!-- Режим редактирования -->
        <div v-else class="q-mt-xs">
          <q-input
            v-model="editText"
            type="textarea"
            outlined
            :rules="[val => !!val || 'Comment text is required']"
            rows="3"
            autofocus
          />
        </div>

        <div class="row items-center justify-between q-mt-sm">
          <div class="row items-center q-gutter-xs">
            <q-btn 
              icon="thumb_up" 
              size="xs" 
              flat 
              dense
              :label="comment.likes"
            />
            <q-btn 
              icon="thumb_down" 
              size="xs" 
              flat 
              dense
              :label="comment.dislikes"
            />
          </div>
          
          <!-- Кнопки в режиме просмотра -->
          <div v-if="!isEditing" class="row items-center q-gutter-xs">
            <q-btn 
              icon="edit" 
              size="xs" 
              flat 
              dense
              color="primary"
              @click="startEditing"
            />
            <q-btn 
              icon="delete" 
              size="xs" 
              flat 
              dense
              color="negative"
              @click="handleDelete"
              :loading="deleteLoading"
            />
          </div>

          <!-- Кнопки в режиме редактирования -->
          <div v-else class="row items-center q-gutter-xs">
            <q-btn 
              icon="check" 
              size="xs" 
              color="positive"
              @click="handleUpdate"
              :loading="updateLoading"
              label="Update"
            />
            <q-btn 
              icon="close" 
              size="xs" 
              color="negative"
              @click="cancelEditing"
              :disabled="updateLoading"
              label="Cancel"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Рекурсивное отображение дочерних комментариев -->
    <CommentItem
      v-for="child in sortedChildren"
      :key="child.id"
      :comment="child"
      :all-comments="allComments"
      :level="level + 1"
      @comment-deleted="$emit('comment-deleted', $event)"
      @comment-updated="$emit('comment-updated', $event)"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import { deleteComment, updateComment } from 'boot/axios'

const $q = useQuasar()
const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  allComments: {
    type: Array,
    required: true
  },
  level: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['comment-deleted', 'comment-updated'])
const deleteLoading = ref(false)
const updateLoading = ref(false)
const isEditing = ref(false)
const editText = ref('')

// Получаем прямых потомков текущего комментария
const directChildren = computed(() => {
  return props.allComments.filter(child => child.parent_comment_id === props.comment.id)
})

// Сортируем дочерние комментарии по дате создания
const sortedChildren = computed(() => {
  return [...directChildren.value].sort((a, b) => 
    new Date(a.created_at) - new Date(b.created_at)
  )
})

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const startEditing = () => {
  isEditing.value = true
  editText.value = props.comment.comment_text
}

const cancelEditing = () => {
  isEditing.value = false
  editText.value = ''
}

const handleUpdate = async () => {
  if (!editText.value.trim()) {
    $q.notify({
      type: 'negative',
      message: 'Comment text cannot be empty',
      position: 'top'
    })
    return
  }

  try {
    updateLoading.value = true
    await updateComment(props.comment.id, {
      new_text: editText.value
    })
    
    $q.notify({
      type: 'positive',
      message: 'Comment updated successfully!',
      position: 'top'
    })

    isEditing.value = false
    
    // Эмитим событие об обновлении комментария
    emit('comment-updated', {
      id: props.comment.id,
      new_text: editText.value
    })
    
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to update comment',
      position: 'top'
    })
  } finally {
    updateLoading.value = false
  }
}

const handleDelete = () => {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Are you sure you want to delete this comment? This action cannot be undone.`,
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      deleteLoading.value = true
      await deleteComment(props.comment.id)
      
      $q.notify({
        type: 'positive',
        message: 'Comment deleted successfully!',
        position: 'top'
      })
      
      // Эмитим событие об удалении комментария
      emit('comment-deleted', props.comment.id)
      
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: error.response?.data?.detail || 'Failed to delete comment',
        position: 'top'
      })
    } finally {
      deleteLoading.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.comment-item {
  transition: margin-left 0.3s ease;
}

.comment-card {
  border-left: 3px solid $primary;
}

.comment-text {
  line-height: 1.4;
  white-space: pre-wrap;
}
</style>