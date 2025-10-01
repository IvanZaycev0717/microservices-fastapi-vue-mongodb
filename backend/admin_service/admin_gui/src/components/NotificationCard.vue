<template>
  <q-card class="notification-card q-mb-md">
    <div class="card-actions">
      <q-btn 
        icon="delete" 
        color="negative" 
        size="sm" 
        round 
        flat
        class="action-btn"
        @click="handleDelete"
        :loading="deleteLoading"
      />
    </div>

    <q-card-section class="q-pa-md">
      <div class="row items-start q-col-gutter-md">
        <!-- Основная информация -->
        <div class="col-12 col-md-8">
          <div class="text-h6 q-mb-xs">{{ notification.to_email }}</div>
          <div class="text-subtitle1 text-weight-medium q-mb-sm">
            {{ notification.subject }}
          </div>
          <div class="text-body1 q-mb-sm">
            {{ notification.message }}
          </div>
        </div>

        <!-- Мета-информация -->
        <div class="col-12 col-md-4">
          <div class="row items-center q-gutter-xs q-mb-sm">
            <q-badge 
              :color="getStatusColor(notification.status)" 
              class="q-px-sm q-py-xs"
            >
              {{ notification.status }}
            </q-badge>
          </div>
          <div class="text-caption text-grey">
            <q-icon name="schedule" class="q-mr-xs" size="14px" />
            Created: {{ formatDate(notification.created_at) }}
          </div>
          <div class="text-caption text-grey q-mt-xs">
            <q-icon name="send" class="q-mr-xs" size="14px" />
            Sent: {{ formatDate(notification.sent_at) }}
          </div>
          <div class="text-caption text-grey q-mt-xs">
            ID: {{ notification._id }}
          </div>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const props = defineProps({
  notification: {
    type: Object,
    required: true,
    default: () => ({
      _id: '',
      to_email: '',
      subject: '',
      message: '',
      status: '',
      created_at: '',
      sent_at: ''
    })
  }
})

const emit = defineEmits(['delete'])
const deleteLoading = ref(false)

const formatDate = (dateString) => {
  if (!dateString) return 'Not sent'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusColor = (status) => {
  const statusColors = {
    'sent': 'positive',
    'failed': 'negative',
    'pending': 'warning'
  }
  return statusColors[status] || 'grey'
}

const handleDelete = () => {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Are you sure you want to delete this notification for "${props.notification.to_email}"?`,
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      deleteLoading.value = true
      emit('delete', props.notification._id)
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: error,
        position: 'top'
      })
    } finally {
      deleteLoading.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.notification-card {
  width: 100%;
  position: relative;
}

.card-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
}

.action-btn {
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  
  &:hover {
    background-color: rgba(255, 255, 255, 1);
  }
}
</style>