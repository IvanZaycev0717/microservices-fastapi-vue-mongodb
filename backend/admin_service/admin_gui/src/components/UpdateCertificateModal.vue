<template>
  <q-dialog v-model="showModal">
    <q-card style="width: 500px; max-width: 90vw">
      <q-card-section class="row items-center">
        <div class="text-h6">Update Certificate</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form class="q-gutter-md" @submit.prevent="handleSubmit">
          <q-input
            v-model="formData.date"
            label="Date"
            type="date"
            outlined
            :rules="[(val) => !!val || 'Date is required']"
          />

          <q-input
            v-model="formData.popularity"
            label="Popularity"
            type="number"
            outlined
            :rules="[
              (val) => !!val || 'Popularity is required',
              (val) => (val >= 0 && val <= 1000) || 'Popularity must be between 0 and 1000',
            ]"
          />

          <q-file
            v-model="formData.file"
            label="New Certificate File (PDF or Image) - Optional"
            outlined
          >
            <template v-slot:prepend>
              <q-icon name="attach_file" />
            </template>
          </q-file>
        </q-form>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="primary" v-close-popup />
        <q-btn label="Update" color="primary" @click="handleSubmit" :loading="loading" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { updateCertificateImage, updateCertificatePopularity } from 'boot/axios'

const $q = useQuasar()
const showModal = ref(false)
const currentCertificate = ref(null)
const loading = ref(false)

const formData = ref({
  date: '',
  popularity: 10,
  file: null,
})

const emit = defineEmits(['updated'])

const open = (certificate) => {
  showModal.value = true
  currentCertificate.value = certificate

  formData.value = {
    date: certificate.date.split('T')[0],
    popularity: certificate.popularity,
    file: null,
  }
}

const handleSubmit = async () => {
  try {
    loading.value = true

    await updateCertificatePopularity(currentCertificate.value.id, formData.value.popularity)

    if (formData.value.file) {
      const fileFormData = new FormData()
      fileFormData.append('file', formData.value.file)

      await updateCertificateImage(currentCertificate.value.id, fileFormData)
    }

    $q.notify({
      type: 'positive',
      message: 'Certificate updated successfully!',
      position: 'top',
    })

    showModal.value = false
    emit('updated')
  } catch (error) {
    console.error('Update error:', error)
    console.error('Error response:', error.response)

    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || `Failed to update certificate: ${error.message}`,
      position: 'top',
    })
  } finally {
    loading.value = false
  }
}

defineExpose({
  open,
})
</script>
