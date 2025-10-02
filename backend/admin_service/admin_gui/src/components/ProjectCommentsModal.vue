<template>
  <q-dialog v-model="showModal" maximized>
    <q-card class="comments-modal">
      <q-bar class="bg-primary text-white">
        <div class="text-h6">Comments for: {{ project?.title?.en }}</div>
        <q-space />
        <q-btn dense flat icon="close" v-close-popup>
          <q-tooltip>Close</q-tooltip>
        </q-btn>
      </q-bar>

      <q-card-section class="q-pa-none">
        <div class="row full-height">
          <div class="col-12 col-md-8 q-pa-md">
            <div v-if="loading" class="text-center q-pa-lg">
              <q-spinner size="50px" color="primary" />
              <div class="q-mt-md">Loading comments...</div>
            </div>

            <div v-else-if="comments.length === 0" class="text-center q-pa-xl">
              <q-icon name="chat" size="64px" color="grey-5" class="q-mb-md" />
              <h4 class="text-h5 q-mb-sm">No comments yet</h4>
              <p class="text-grey-7">This project doesn't have any comments.</p>
            </div>

            <div v-else class="comments-tree">
              <CommentItem
                v-for="comment in rootComments"
                :key="comment.id"
                :comment="comment"
                :all-comments="sortedComments"
                level="0"
                @comment-deleted="handleCommentDeleted"
                @comment-updated="handleCommentUpdated"
              />
            </div>
          </div>

          <div class="col-12 col-md-4 bg-grey-2 q-pa-md">
            <div class="text-h6 q-mb-md">Project Info</div>
            <q-img
              v-if="project?.thumbnail"
              :src="project.thumbnail"
              height="150px"
              class="q-mb-md"
            />
            <div class="text-weight-medium">{{ project?.title?.ru }}</div>
            <div class="text-caption text-grey">{{ project?.title?.en }}</div>
            <div class="text-caption text-grey q-mt-sm">Popularity: {{ project?.popularity }}</div>
            <div class="text-caption text-grey">Date: {{ formatDate(project?.date) }}</div>

            <div class="q-mt-lg">
              <div class="text-weight-medium">Comments Statistics</div>
              <div class="text-caption">Total: {{ comments.length }}</div>
              <div class="text-caption">Root: {{ rootComments.length }}</div>
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import { getCommentsByProjectId } from 'boot/axios'
import CommentItem from 'components/CommentItem.vue'

const $q = useQuasar()
const showModal = ref(false)
const project = ref(null)
const comments = ref([])
const loading = ref(false)

const sortedComments = computed(() => {
  return [...comments.value].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
})

const rootComments = computed(() => {
  return sortedComments.value.filter((comment) => comment.parent_comment_id === null)
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('ru-RU')
}

const handleCommentDeleted = (deletedCommentId) => {
  comments.value = comments.value.filter((comment) => comment.id !== deletedCommentId)

  const removeChildren = (parentId) => {
    const children = comments.value.filter((comment) => comment.parent_comment_id === parentId)
    children.forEach((child) => {
      comments.value = comments.value.filter((c) => c.id !== child.id)
      removeChildren(child.id)
    })
  }

  removeChildren(deletedCommentId)
}

const handleCommentUpdated = (updatedComment) => {
  const index = comments.value.findIndex((comment) => comment.id === updatedComment.id)
  if (index !== -1) {
    comments.value[index].comment_text = updatedComment.new_text
  }
}

const open = async (selectedProject) => {
  showModal.value = true
  project.value = selectedProject
  comments.value = []
  loading.value = true

  try {
    const response = await getCommentsByProjectId(selectedProject.id)
    comments.value = response.data
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error,
      position: 'top',
    })
    comments.value = []
  } finally {
    loading.value = false
  }
}

defineExpose({
  open,
})
</script>

<style lang="scss" scoped>
.comments-modal {
  width: 90vw;
  height: 90vh;
}

.full-height {
  height: calc(90vh - 50px);
}

.comments-tree {
  max-height: calc(90vh - 100px);
  overflow-y: auto;
}
</style>
