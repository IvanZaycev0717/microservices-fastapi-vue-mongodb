<template>
  <q-card class="certificate-card q-mb-md">
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

    <div class="row no-wrap">
      <div class="col-auto">
        <q-img
          :src="certificate.thumb"
          :alt="certificate.alt"
          height="200px"
          width="200px"
        />
      </div>

      <div class="col q-pa-md">
        <div class="text-h6 q-mb-sm">Certificate</div>
        <div class="text-caption text-grey q-mb-md">
          {{ formatDate(certificate.date) }}
        </div>
        <q-badge color="primary" class="q-mt-md">
          Popularity: {{ certificate.popularity }}
        </q-badge>
      </div>
    </div>
  </q-card>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const props = defineProps({
  certificate: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['deleted', 'edit'])
const deleteLoading = ref(false)

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const handleEdit = () => {
  emit('edit', props.certificate)
}

const handleDelete = () => {
  $q.dialog({
    title: 'Confirm Delete',
    message: 'Are you sure you want to delete this certificate?',
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      deleteLoading.value = true
      emit('delete', props.certificate.id)
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
.certificate-card {
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