<template>
  <q-dialog v-model="showModal">
    <q-card style="width: 600px; max-width: 90vw;">
      <q-card-section class="row items-center">
        <div class="text-h6">Create New Publication</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form class="q-gutter-md" @submit.prevent="handleSubmit">
          <!-- English Title -->
          <q-input
            v-model="formData.title_en"
            label="Title (English)"
            outlined
            :rules="[val => !!val || 'English title is required']"
          />
          
          <!-- Russian Title -->
          <q-input
            v-model="formData.title_ru"
            label="Title (Russian)"
            outlined
            :rules="[val => !!val || 'Russian title is required']"
          />

          <!-- Page URL -->
          <q-input
            v-model="formData.page"
            label="Page URL"
            type="url"
            outlined
            :rules="[
              val => !!val || 'Page URL is required',
              isValidUrl
            ]"
          />

          <!-- Site URL -->
          <q-input
            v-model="formData.site"
            label="Site URL"
            type="url"
            outlined
            :rules="[
              val => !!val || 'Site URL is required',
              isValidUrl
            ]"
          />

          <!-- Rating -->
          <q-input
            v-model="formData.rating"
            label="Rating"
            type="number"
            outlined
            :rules="[
              val => !!val || 'Rating is required',
              val => val >= 0 || 'Rating must be positive'
            ]"
          />

          <!-- Date -->
          <q-input
            v-model="formData.date"
            label="Date"
            type="date"
            outlined
            :rules="[val => !!val || 'Date is required']"
          />
        </q-form>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="primary" v-close-popup />
        <q-btn 
          label="Create" 
          color="primary" 
          @click="handleSubmit"
          :loading="loading"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { createPublication } from 'boot/axios'

const $q = useQuasar()
const showModal = ref(false)
const loading = ref(false)

const formData = ref({
  title_en: '',
  title_ru: '',
  page: '',
  site: '',
  rating: 0,
  date: ''
})

const emit = defineEmits(['created'])

// Валидация URL
const isValidUrl = (val) => {
  try {
    new URL(val)
    return true
  } catch (error) {
    return `${error} Please enter a valid URL (e.g., https://example.com)`
  }
}

const open = () => {
  showModal.value = true
  formData.value = {
    title_en: '',
    title_ru: '',
    page: '',
    site: '',
    rating: 0,
    date: ''
  }
}

const handleSubmit = async () => {
  try {
    loading.value = true

    await createPublication(formData.value)
    
    $q.notify({
      type: 'positive',
      message: 'Publication created successfully!',
      position: 'top'
    })

    showModal.value = false
    emit('created')
    
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to create publication',
      position: 'top'
    })
  } finally {
    loading.value = false
  }
}

defineExpose({
  open
})
</script>