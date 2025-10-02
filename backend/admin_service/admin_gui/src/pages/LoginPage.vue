<template>
  <q-layout>
    <q-page-container>
      <q-page class="row justify-center items-center">
        <q-card style="width: 400px">
          <q-card-section>
            <q-form class="q-gutter-md" @submit.prevent="onSubmit">
              <q-input
                v-model="email"
                label="Email"
                type="email"
                outlined
                :rules="[(val) => !!val || 'Email is required', isValidEmail]"
              />
              <q-input
                v-model="password"
                label="Password"
                :type="isPwd ? 'password' : 'text'"
                outlined
                :rules="[(val) => !!val || 'Password is required', isValidPassword]"
              >
                <template v-slot:append>
                  <q-icon
                    :name="isPwd ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="isPwd = !isPwd"
                  />
                </template>
              </q-input>
              <q-btn label="Login" color="primary" type="submit" />
            </q-form>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from 'stores/auth'
import { loginUser } from 'boot/axios'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const isPwd = ref(true)
const $q = useQuasar()
const router = useRouter()

const isValidEmail = (val) => {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return pattern.test(val) || 'Invalid email format'
}

const isValidPassword = (val) => {
  if (val.length < 5) return 'Password must be at least 5 characters'
  if (val.length > 31) return 'Password must be less than 32 characters'
  return true
}

const onSubmit = async () => {
  try {
    const response = await loginUser({
      email: email.value,
      password: password.value,
    })

    const authStore = useAuthStore()
    authStore.setToken(response.data.access_token)

    $q.notify({
      type: 'positive',
      message: response.data?.data || 'Login Successful',
      position: 'top',
    })
    router.push('/')
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.data || 'Login failed',
      position: 'top',
    })
  }
}
</script>
