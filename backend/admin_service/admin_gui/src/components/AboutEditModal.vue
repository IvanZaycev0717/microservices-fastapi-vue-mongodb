<template>
  <q-dialog v-model="showModal">
    <q-card style="width: 700px; max-width: 90vw">
      <q-card-section>
        <div class="text-h6">Edit About Card</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form @submit="handleUpdate" class="q-gutter-md">
          <div class="row items-center q-gutter-md">
            <q-file
              v-model="imageFile"
              label="Change Image"
              accept=".jpg,.jpeg,.png,.webp"
              max-file-size="524288"
              @rejected="onFileRejected"
              @update:model-value="onFileSelected"
              style="width: 200px"
            >
              <template v-slot:prepend>
                <q-icon name="attach_file" />
              </template>
            </q-file>

            <div class="image-preview">
              <q-img
                :src="imagePreview || currentCard.image_url"
                height="100px"
                width="100px"
                style="border-radius: 4px"
              />
              <div v-if="imageFile" class="text-caption text-center q-mt-xs">
                {{ getFileSize(imageFile) }}
              </div>
            </div>
          </div>

          <div class="text-h6">Russian Version</div>
          <q-input
            v-model="formData.title_ru"
            label="Title RU"
            :rules="[
              (val) => !!val || 'Title is required',
              (val) => val.length <= 255 || 'Max 255 characters',
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
              (val) => !!val || 'Description is required',
              (val) => val.length <= 1000 || 'Max 1000 characters',
            ]"
            counter
            maxlength="1000"
            outlined
            rows="3"
          />

          <div class="text-h6">English Version</div>
          <q-input
            v-model="formData.title_en"
            label="Title EN"
            :rules="[
              (val) => !!val || 'Title is required',
              (val) => val.length <= 255 || 'Max 255 characters',
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
              (val) => !!val || 'Description is required',
              (val) => val.length <= 1000 || 'Max 1000 characters',
            ]"
            counter
            maxlength="1000"
            outlined
            rows="3"
          />

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
import { getAboutCardById, updateAboutText, updateAboutImage } from 'boot/axios'

const $q = useQuasar()
const showModal = ref(false)
const loading = ref(false)
const imageFile = ref(null)
const imagePreview = ref(null)
const currentCardId = ref(null)

const currentCard = reactive({
  image_url: '',
  translations: {
    en: { title: '', description: '' },
    ru: { title: '', description: '' },
  },
})

const formData = reactive({
  title_ru: '',
  description_ru: '',
  title_en: '',
  description_en: '',
})

const hasTextChanges = computed(() => {
  return (
    formData.title_ru !== currentCard.translations.ru.title ||
    formData.description_ru !== currentCard.translations.ru.description ||
    formData.title_en !== currentCard.translations.en.title ||
    formData.description_en !== currentCard.translations.en.description
  )
})

const hasImageChanges = computed(() => {
  return !!imageFile.value
})

const open = async (cardId) => {
  currentCardId.value = cardId
  showModal.value = true
  loading.value = true

  try {
    const response = await getAboutCardById(cardId)
    Object.assign(currentCard, response.data)

    formData.title_ru = currentCard.translations.ru.title
    formData.description_ru = currentCard.translations.ru.description
    formData.title_en = currentCard.translations.en.title
    formData.description_en = currentCard.translations.en.description
  } catch (error) {
    console.error('Error loading card data:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to load card data',
    })
    showModal.value = false
  } finally {
    loading.value = false
  }
}

const handleUpdate = async () => {
  loading.value = true

  try {
    if (hasTextChanges.value) {
      await updateAboutText(currentCardId.value, formData)
    }

    if (hasImageChanges.value) {
      await updateAboutImage(currentCardId.value, imageFile.value)
    }

    $q.notify({
      type: 'positive',
      message: 'Card updated successfully!',
    })

    showModal.value = false
    resetForm()
    emit('updated')
  } catch (error) {
    console.error('Error updating card:', error)
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to update card',
    })
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  currentCardId.value = null
  imageFile.value = null
  imagePreview.value = null
  loading.value = false
}

const emit = defineEmits(['updated'])
defineExpose({
  open,
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
