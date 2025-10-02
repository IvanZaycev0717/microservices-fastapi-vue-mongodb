<template>
  <q-dialog v-model="showModal">
    <q-card style="width: 500px; max-width: 90vw">
      <q-card-section class="row items-center">
        <div class="text-h6">Create New User</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form class="q-gutter-md" @submit.prevent="handleSubmit">
          <q-input
            v-model="formData.email"
            label="Email"
            type="email"
            outlined
            :rules="[(val) => !!val || 'Email is required', isValidEmail]"
          />

          <q-input
            v-model="formData.password"
            label="Password"
            :type="isPwd ? 'password' : 'text'"
            outlined
            :rules="[
              (val) => !!val || 'Password is required',
              (val) => val.length >= 5 || 'Password must be at least 5 characters',
            ]"
          >
            <template v-slot:append>
              <q-icon
                :name="isPwd ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="isPwd = !isPwd"
              />
            </template>
          </q-input>

          <q-select
            v-model="formData.roles"
            label="Roles"
            multiple
            :options="roleOptions"
            outlined
            use-chips
          />
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
import { registerUser } from 'boot/axios'

const $q = useQuasar()
const showModal = ref(false)
const isPwd = ref(true)
const loading = ref(false)

const formData = ref({
  email: '',
  password: '',
  roles: [],
})

const roleOptions = ['user', 'admin']

const emit = defineEmits(['created'])

const isValidEmail = (val) => {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return pattern.test(val) || 'Invalid email format'
}

const open = () => {
  showModal.value = true
  formData.value = {
    email: '',
    password: '',
    roles: [],
  }
  isPwd.value = true
}

const handleSubmit = async () => {
  try {
    loading.value = true

    await registerUser(formData.value)

    $q.notify({
      type: 'positive',
      message: 'User created successfully!',
      position: 'top',
    })

    showModal.value = false
    emit('created')
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to create user',
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
