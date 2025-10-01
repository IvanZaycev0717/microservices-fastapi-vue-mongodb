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
        
        <div class="comment-text q-mt-xs">
          {{ comment.comment_text }}
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
          
          <div class="row items-center q-gutter-xs">
            <q-btn 
              icon="reply" 
              size="xs" 
              flat 
              dense
              color="primary"
            />
            <q-btn 
              icon="edit" 
              size="xs" 
              flat 
              dense
              color="primary"
            />
            <q-btn 
              icon="delete" 
              size="xs" 
              flat 
              dense
              color="negative"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Рекурсивное отображение дочерних комментариев -->
    <CommentItem
      v-for="child in directChildren"
      :key="child.id"
      :comment="child"
      :all-comments="allComments"
      :level="level + 1"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

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

// Получаем прямых потомков текущего комментария
const directChildren = computed(() => {
  return props.allComments.filter(child => child.parent_comment_id === props.comment.id)
})

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
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
}
</style>