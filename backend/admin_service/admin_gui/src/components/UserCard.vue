<template>
  <q-card class="user-card q-mb-md">
    <div class="card-actions">
      <q-btn 
        icon="edit" 
        color="primary" 
        size="sm" 
        round 
        flat
        class="action-btn q-mr-xs"
        @click="handleEdit"
      />
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
        <div class="col-12 col-md-6">
          <div class="text-h6 q-mb-xs">{{ user.email }}</div>
          <div class="text-caption text-grey">
            ID: {{ user.id }}
          </div>
        </div>

        <!-- Статус и роли -->
        <div class="col-12 col-md-6">
          <div class="row items-center q-gutter-sm q-mb-xs">
            <q-badge 
              :color="user.is_banned ? 'negative' : 'positive'" 
              class="q-px-sm q-py-xs"
            >
              {{ user.is_banned ? 'Banned' : 'Active' }}
            </q-badge>
            
            <q-badge 
              v-for="role in user.roles" 
              :key="role"
              color="secondary" 
              class="q-px-sm q-py-xs"
            >
              {{ role }}
            </q-badge>
          </div>
        </div>
      </div>

      <q-separator class="q-my-md" />

      <div class="row items-center q-col-gutter-md">
        <!-- Даты -->
        <div class="col-12 col-sm-6">
          <div class="text-caption text-grey">
            <q-icon name="event" class="q-mr-xs" size="14px" />
            Created: {{ formatDate(user.created_at) }}
          </div>
          <div class="text-caption text-grey q-mt-xs">
            <q-icon name="login" class="q-mr-xs" size="14px" />
            Last login: {{ formatDate(user.last_login_at) }}
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
  user: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      email: '',
      is_banned: false,
      roles: [],
      created_at: '',
      last_login_at: ''
    })
  }
})

const emit = defineEmits(['delete', 'edit'])
const deleteLoading = ref(false)

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleEdit = () => {
  emit('edit', props.user)
}

const handleDelete = () => {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Are you sure you want to delete user "${props.user.email}"? This action cannot be undone.`,
    cancel: true,
    persistent: true
  }).onOk(() => {
    deleteLoading.value = true
    emit('delete', props.user.email)
    deleteLoading.value = false
  })
}
</script>

<style lang="scss" scoped>
.user-card {
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