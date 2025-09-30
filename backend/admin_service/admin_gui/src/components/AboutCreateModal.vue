<template>
  <q-dialog v-model="showModal">
    <q-card style="width: 700px; max-width: 90vw;">
      <q-card-section>
        <div class="text-h6">Create About Card</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form @submit="handleCreate" class="q-gutter-md">
          <!-- Загрузка изображения -->
          <div class="row items-center q-gutter-md">
            <q-file
              v-model="imageFile"
              label="Upload Image"
              accept=".jpg,.jpeg,.png,.webp"
              max-file-size="524288"
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
            :rules="[
              val => !!val || 'Title is required',
              val => val.length <= 255 || 'Max 255 characters'
            ]"
            counter
            maxlength="255"
            outlined
          />
          <q-input
            v-model="formData.description_ru"
            label="Description RU"
            type="textarea"
            :rules="[
              val => !!val || 'Description is required',
              val => val.length <= 1000 || 'Max 1000 characters'
            ]"
            counter
            maxlength="1000"
            outlined
            rows="3"
          />

          <!-- Английская версия -->
          <div class="text-h6">English Version</div>
          <q-input
            v-model="formData.title_en"
            label="Title EN"
            :rules="[
              val => !!val || 'Title is required',
              val => val.length <= 255 || 'Max 255 characters'
            ]"
            counter
            maxlength="255"
            outlined
          />
          <q-input
            v-model="formData.description_en"
            label="Description EN"
            type="textarea"
            :rules="[
              val => !!val || 'Description is required',
              val => val.length <= 1000 || 'Max 1000 characters'
            ]"
            counter
            maxlength="1000"
            outlined
            rows="3"
          />

          <q-card-actions align="right" class="q-pa-none q-mt-md">
            <q-btn flat label="Cancel" color="primary" v-close-popup />
            <q-btn 
              label="Create" 
              type="submit" 
              color="primary" 
              :loading="loading" 
              :disable="!isFormValid"
            />
          </q-card-actions>
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useQuasar } from 'quasar'
import { createAboutCard } from 'boot/axios'

const $q = useQuasar()
const showModal = ref(false)
const loading = ref(false)
const imageFile = ref(null)
const imagePreview = ref(null)

const formData = reactive({
  title_ru: '',
  description_ru: '',
  title_en: '',
  description_en: ''
})

// Валидация формы
const isFormValid = computed(() => {
  return imageFile.value &&
    formData.title_ru.trim() &&
    formData.description_ru.trim() &&
    formData.title_en.trim() &&
    formData.description_en.trim() &&
    formData.title_ru.length <= 255 &&
    formData.description_ru.length <= 1000 &&
    formData.title_en.length <= 255 &&
    formData.description_en.length <= 1000
})

const getFileSize = (file) => {
  if (!file) return ''
  const sizeInKB = Math.round(file.size / 1024)
  return `${sizeInKB} KB`
}

const validateImageFormat = (file) => {
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  return allowedTypes.includes(file.type)
}

const validateImageSize = (file) => {
  return file.size <= 524288 // 500KB в байтах
}

const onFileSelected = (file) => {
  if (file) {
    if (!validateImageFormat(file)) {
      $q.notify({
        type: 'negative',
        message: 'Invalid image format. Use JPG, PNG or WebP'
      })
      imageFile.value = null
      return
    }

    if (!validateImageSize(file)) {
      $q.notify({
        type: 'negative',
        message: 'Image size must be less than 500KB'
      })
      imageFile.value = null
      return
    }

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
  const reasons = rejectedEntries.map(entry => entry.failedPropValidation)
  if (reasons.includes('max-file-size')) {
    $q.notify({
      type: 'negative',
      message: 'File size must be less than 500KB'
    })
  } else if (reasons.includes('accept')) {
    $q.notify({
      type: 'negative',
      message: 'File must be JPG, PNG or WebP'
    })
  }
}

const prepareFormData = () => {
  const formDataObj = new FormData()
  
  formDataObj.append('title_ru', formData.title_ru.trim())
  formDataObj.append('description_ru', formData.description_ru.trim())
  formDataObj.append('title_en', formData.title_en.trim())
  formDataObj.append('description_en', formData.description_en.trim())
  
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
    await createAboutCard(formDataObj)
    
    $q.notify({
      type: 'positive',
      message: 'About card created successfully!'
    })
    
    showModal.value = false
    resetForm()
    emit('created')
    
  } catch (error) {
    console.error('Error creating about card:', error)
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to create about card'
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