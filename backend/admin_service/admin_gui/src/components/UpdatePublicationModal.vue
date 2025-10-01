<template>
  <q-dialog v-model="showModal">
    <q-card style="width: 600px; max-width: 90vw;">
      <q-card-section class="row items-center">
        <div class="text-h6">Update Publication</div>
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
        </q-form>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="primary" v-close-popup />
        <q-btn 
          label="Update" 
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
import { updatePublication } from 'boot/axios'

const $q = useQuasar()
const showModal = ref(false)
const currentPublication = ref(null)
const loading = ref(false)

const formData = ref({
  title_en: '',
  title_ru: '',
  page: '',
  site: '',
  rating: 0
})

const emit = defineEmits(['updated'])

// Валидация URL
const isValidUrl = (val) => {
  try {
    new URL(val)
    return true
  } catch {
    return 'Please enter a valid URL (e.g., https://example.com)'
  }
}

// Метод для открытия модального окна с данными публикации
const open = (publication) => {
  showModal.value = true
  currentPublication.value = publication
  
  // Заполняем форму текущими данными
  formData.value = {
    title_en: publication.title.en,
    title_ru: publication.title.ru,
    page: publication.page,
    site: publication.site,
    rating: publication.rating
  }
}

const handleSubmit = async () => {
  try {
    loading.value = true

    await updatePublication(currentPublication.value.id, formData.value)
    
    $q.notify({
      type: 'positive',
      message: 'Publication updated successfully!',
      position: 'top'
    })

    showModal.value = false
    emit('updated')
    
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to update publication',
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