<template>
  <q-dialog v-model="showModal">
    <q-card style="width: 700px; max-width: 90vw;">
      <q-card-section>
        <div class="text-h6">Create Project</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form @submit="handleCreate" class="q-gutter-md">
          <!-- Загрузка изображения -->
          <div class="row items-center q-gutter-md">
            <q-file
              v-model="imageFile"
              label="Project Image"
              accept=".jpg,.jpeg,.png,.gif,.webp"
              max-file-size="5242880"
              @rejected="onFileRejected"
              @update:model-value="onFileSelected"
              style="width: 200px"
              :rules="[val => !!val || 'Image is required']"
            >
              <template v-slot:prepend>
                <q-icon name="attach_file" />
              </template>
            </q-file>

            <!-- Preview изображения -->
            <div v-if="imagePreview" class="image-preview">
              <q-img
                :src="imagePreview"
                height="100px"
                width="100px"
                style="border-radius: 4px;"
              />
              <div class="text-caption text-center q-mt-xs">
                {{ getFileSize(imageFile) }}
              </div>
            </div>
          </div>

          <!-- Русская версия -->
          <div class="text-h6">Russian Version</div>
          <q-input
            v-model="formData.title_ru"
            label="Title RU"
            :rules="[val => !!val || 'Title is required']"
            outlined
          />
          <q-input
            v-model="formData.description_ru"
            label="Description RU"
            type="textarea"
            :rules="[val => !!val || 'Description is required']"
            outlined
            rows="3"
          />

          <!-- Английская версия -->
          <div class="text-h6">English Version</div>
          <q-input
            v-model="formData.title_en"
            label="Title EN"
            :rules="[val => !!val || 'Title is required']"
            outlined
          />
          <q-input
            v-model="formData.description_en"
            label="Description EN"
            type="textarea"
            :rules="[val => !!val || 'Description is required']"
            outlined
            rows="3"
          />

          <!-- Ссылка и дата -->
          <div class="row q-col-gutter-md">
            <div class="col-8">
              <q-input
                v-model="formData.link"
                label="Project Link"
                :rules="[val => !!val || 'Link is required', isValidUrl]"
                outlined
              />
            </div>
            <div class="col-4">
              <q-input
                v-model="formData.date"
                label="Date"
                type="date"
                outlined
              />
            </div>
          </div>

          <!-- Popularity -->
          <q-input
            v-model="formData.popularity"
            label="Popularity"
            type="number"
            min="0"
            outlined
          />

          <q-card-actions align="right" class="q-pa-none q-mt-md">
            <q-btn flat label="Cancel" color="primary" v-close-popup />
            <q-btn label="Create" type="submit" color="primary" :loading="loading" />
          </q-card-actions>
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useQuasar } from 'quasar'
import { createProject } from 'boot/axios'

const $q = useQuasar()
const showModal = ref(false)
const loading = ref(false)
const imageFile = ref(null)
const imagePreview = ref(null)

const formData = reactive({
  title_ru: '',
  description_ru: '',
  title_en: '',
  description_en: '',
  link: '',
  date: new Date().toISOString().split('T')[0], // текущая дата
  popularity: 0
})

const isValidUrl = (val) => {
  try {
    new URL(val)
    return true
  } catch {
    return 'Please enter a valid URL'
  }
}

const isFormValid = computed(() => {
  return imageFile.value &&
    formData.title_ru.trim() &&
    formData.description_ru.trim() &&
    formData.title_en.trim() &&
    formData.description_en.trim() &&
    formData.link.trim() &&
    isValidUrl(formData.link) === true
})

const getFileSize = (file) => {
  if (!file) return ''
  const sizeInMB = (file.size / (1024 * 1024)).toFixed(2)
  return `${sizeInMB} MB`
}

const onFileSelected = (file) => {
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  } else {
    imagePreview.value = null
  }
}

const onFileRejected = (rejectedEntries) => {
  $q.notify({
    type: 'negative',
    message: `${rejectedEntries} File must be JPG, PNG, GIF or WebP and less than 5MB`
  })
}

const prepareFormData = () => {
  const formDataObj = new FormData()
  
  // Текстовые поля
  formDataObj.append('title_ru', formData.title_ru)
  formDataObj.append('description_ru', formData.description_ru)
  formDataObj.append('title_en', formData.title_en)
  formDataObj.append('description_en', formData.description_en)
  formDataObj.append('link', formData.link)
  formDataObj.append('date', formData.date)
  formDataObj.append('popularity', formData.popularity.toString())
  
  // Файл изображения
  if (imageFile.value) {
    formDataObj.append('image', imageFile.value)
  }
  
  return formDataObj
}

const handleCreate = async () => {
  if (!isFormValid.value) {
    $q.notify({
      type: 'warning',
      message: 'Please fill all required fields correctly'
    })
    return
  }

  loading.value = true

  try {
    const formDataObj = prepareFormData()
    await createProject(formDataObj)
    
    $q.notify({
      type: 'positive',
      message: 'Project created successfully!'
    })
    
    showModal.value = false
    resetForm()
    emit('created')
    
  } catch (error) {
    console.error('Error creating project:', error)
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to create project'
    })
  } finally {
    loading.value = false
  }
}

const open = () => {
  showModal.value = true
}

const resetForm = () => {
  formData.title_ru = ''
  formData.description_ru = ''
  formData.title_en = ''
  formData.description_en = ''
  formData.link = ''
  formData.date = new Date().toISOString().split('T')[0]
  formData.popularity = 0
  imageFile.value = null
  imagePreview.value = null
  loading.value = false
}

const emit = defineEmits(['created'])
defineExpose({
  open
})
</script>

<style lang="scss" scoped>
.image-preview {
  border: 2px dashed #ccc;
  border-radius: 4px;
  padding: 4px;
  
  .text-caption {
    color: #666;
  }
}
</style>