<template>
  <q-dialog v-model="showModal">
    <q-card style="width: 500px; max-width: 90vw">
      <q-card-section class="row items-center">
        <div class="text-h6">Create New Certificate</div>
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
            label="Certificate File (PDF or Image)"
            outlined
            :rules="[(val) => !!val || 'File is required']"
          >
            <template v-slot:prepend>
              <q-icon name="attach_file" />
            </template>
          </q-file>
        </q-form>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="primary" v-close-popup />
        <q-btn label="Create" color="primary" @click="handleSubmit" :loading="loading" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { createCertificate } from 'boot/axios'

const $q = useQuasar()
const showModal = ref(false)
const loading = ref(false)

const formData = ref({
  date: '',
  popularity: 10,
  file: null,
})

const emit = defineEmits(['created'])

const open = () => {
  showModal.value = true
  formData.value = {
    date: '',
    popularity: 10,
    file: null,
  }
}

const handleSubmit = async () => {
  try {
    loading.value = true

    const formDataToSend = new FormData()
    formDataToSend.append('date', formData.value.date)
    formDataToSend.append('popularity', formData.value.popularity.toString())
    formDataToSend.append('file', formData.value.file)

    await createCertificate(formDataToSend)

    $q.notify({
      type: 'positive',
      message: 'Certificate created successfully!',
      position: 'top',
    })

    showModal.value = false
    emit('created')
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to create certificate',
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
