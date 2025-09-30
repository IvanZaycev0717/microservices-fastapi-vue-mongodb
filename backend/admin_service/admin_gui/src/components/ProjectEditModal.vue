<template>
  <q-dialog v-model="showModal">
    <q-card style="width: 700px; max-width: 90vw;">
      <q-card-section>
        <div class="text-h6">Edit Project</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form @submit="handleUpdate" class="q-gutter-md">
          <!-- Загрузка изображения -->
          <div class="row items-center q-gutter-md">
            <q-file
              v-model="imageFile"
              label="Change Image"
              accept=".jpg,.jpeg,.png,.gif,.webp"
              max-file-size="5242880"
              @rejected="onFileRejected"
              @update:model-value="onFileSelected"
              style="width: 200px"
            >
              <template v-slot:prepend>
                <q-icon name="attach_file" />
              </template>
            </q-file>

            <!-- Preview изображения -->
            <div class="image-preview">
              <q-img
                :src="imagePreview || currentProject.thumbnail"
                height="100px"
                width="100px"
                style="border-radius: 4px;"
              />
              <div v-if="imageFile" class="text-caption text-center q-mt-xs">
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

          <!-- Ссылка и популярность -->
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
                v-model="formData.popularity"
                label="Popularity"
                type="number"
                min="0"
                outlined
              />
            </div>
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
import { ref, reactive, computed } from 'vue'
import { useQuasar } from 'quasar'
import { getProjectById, updateProjectText, updateProjectImage } from 'boot/axios'

const $q = useQuasar()
const showModal = ref(false)
const loading = ref(false)
const imageFile = ref(null)
const imagePreview = ref(null)
const currentProjectId = ref(null)

const currentProject = reactive({
  title: { en: '', ru: '' },
  description: { en: '', ru: '' },
  thumbnail: '',
  link: '',
  popularity: 0
})

const formData = reactive({
  title_ru: '',
  description_ru: '',
  title_en: '',
  description_en: '',
  link: '',
  popularity: 0
})

// Отслеживаем изменения
const hasTextChanges = computed(() => {
  return formData.title_ru !== currentProject.title.ru ||
         formData.description_ru !== currentProject.description.ru ||
         formData.title_en !== currentProject.title.en ||
         formData.description_en !== currentProject.description.en ||
         formData.link !== currentProject.link ||
         formData.popularity !== currentProject.popularity
})

const hasImageChanges = computed(() => {
  return !!imageFile.value
})

const isValidUrl = (val) => {
  try {
    new URL(val)
    return true
  } catch {
    return 'Please enter a valid URL'
  }
}

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
    message: rejectedEntries
  })
}

const open = async (projectId) => {
  currentProjectId.value = projectId
  showModal.value = true
  loading.value = true

  try {
    const response = await getProjectById(projectId)
    Object.assign(currentProject, response.data)
    
    // Предзаполняем форму
    formData.title_ru = currentProject.title.ru
    formData.description_ru = currentProject.description.ru
    formData.title_en = currentProject.title.en
    formData.description_en = currentProject.description.en
    formData.link = currentProject.link
    formData.popularity = currentProject.popularity
    
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error
    })
    showModal.value = false
  } finally {
    loading.value = false
  }
}

const handleUpdate = async () => {
  loading.value = true

  try {
    // Обновляем текст если есть изменения
    if (hasTextChanges.value) {
      await updateProjectText(currentProjectId.value, formData)
    }

    // Обновляем изображение если есть изменения
    if (hasImageChanges.value) {
      await updateProjectImage(currentProjectId.value, imageFile.value)
    }

    $q.notify({
      type: 'positive',
      message: 'Project updated successfully!'
    })
    
    showModal.value = false
    resetForm()
    emit('updated')
    
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to update project'
    })
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  currentProjectId.value = null
  imageFile.value = null
  imagePreview.value = null
  loading.value = false
}

const emit = defineEmits(['updated'])
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