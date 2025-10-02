<template>
  <q-dialog v-model="showModal">
    <q-card style="width: 600px; max-width: 90vw">
      <q-card-section>
        <div class="text-h6">Edit {{ kingdomData.kingdom }} Skills</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form @submit="handleUpdate" class="q-gutter-md">
          <q-input
            v-model="skillsString"
            type="textarea"
            label="Skills (comma separated)"
            :rules="[(val) => !!val || 'Skills are required']"
            outlined
            rows="6"
            hint="Enter skills separated by commas"
          />

          <div class="text-caption text-grey">
            Current format: {{ skillsString.split(',').length }} skills
          </div>

          <q-card-actions align="right" class="q-pa-none q-mt-md">
            <q-btn flat label="Cancel" color="primary" v-close-popup />
            <q-btn label="Update" type="submit" color="primary" :loading="loading" />
          </q-card-actions>
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'

const $q = useQuasar()
const showModal = ref(false)
const loading = ref(false)
const kingdomData = ref({})
const skillsString = ref('')

const open = (data) => {
  kingdomData.value = data
  skillsString.value = data.items.join(', ')
  showModal.value = true
}

const handleUpdate = async () => {
  loading.value = true

  try {
    await api.patch(`/technologies/${kingdomData.value.key}`, {
      skills: skillsString.value,
    })

    $q.notify({
      type: 'positive',
      message: `${kingdomData.value.kingdom} skills updated successfully!`,
    })

    showModal.value = false
    resetForm()
    emit('updated')
  } catch (error) {
    console.error('Error updating skills:', error)
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to update skills',
    })
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  kingdomData.value = {}
  skillsString.value = ''
  loading.value = false
}

const emit = defineEmits(['updated'])
defineExpose({
  open,
})
</script>
