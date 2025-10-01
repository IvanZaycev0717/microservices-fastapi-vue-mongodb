<template>
  <q-dialog v-model="showModal">
    <q-card style="width: 600px; max-width: 90vw;">
      <q-card-section class="row items-center">
        <div class="text-h6">Send Email</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form class="q-gutter-md" @submit.prevent="handleSubmit">
          <!-- To Email -->
          <q-input
            v-model="formData.to_email"
            label="To Email"
            type="email"
            outlined
            :rules="[
              val => !!val || 'Email is required',
              isValidEmail
            ]"
          />
          
          <!-- Subject -->
          <q-input
            v-model="formData.subject"
            label="Subject"
            outlined
            :rules="[
              val => !!val || 'Subject is required',
              val => val.length >= 1 || 'Subject is too short',
              val => val.length <= 200 || 'Subject is too long'
            ]"
            counter
            maxlength="200"
          />

          <!-- Message -->
          <q-input
            v-model="formData.message"
            label="Message"
            type="textarea"
            outlined
            :rules="[
              val => !!val || 'Message is required',
              val => val.length >= 1 || 'Message is too short', 
              val => val.length <= 5000 || 'Message is too long'
            ]"
            counter
            maxlength="5000"
            rows="6"
          />
        </q-form>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="primary" v-close-popup />
        <q-btn 
          label="Send" 
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
import { createNotification } from 'boot/axios'

const $q = useQuasar()
const showModal = ref(false)
const loading = ref(false)

const formData = ref({
  to_email: '',
  subject: '',
  message: ''
})

const emit = defineEmits(['sent'])

// Валидация email
const isValidEmail = (val) => {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return pattern.test(val) || 'Invalid email format'
}

// Метод для открытия модального окна
const open = () => {
  showModal.value = true
  formData.value = {
    to_email: '',
    subject: '',
    message: ''
  }
}

const handleSubmit = async () => {
  try {
    loading.value = true

    await createNotification(formData.value)
    
    $q.notify({
      type: 'positive',
      message: 'Email sent successfully!',
      position: 'top'
    })

    showModal.value = false
    emit('sent')
    
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to send email',
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