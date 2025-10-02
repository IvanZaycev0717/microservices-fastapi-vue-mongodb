<template>
  <q-dialog v-model="showModal">
    <q-card style="width: 500px; max-width: 90vw">
      <q-card-section class="row items-center">
        <div class="text-h6">Update User</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-card-section class="q-pt-none">
        <div class="text-h6 q-mb-md">{{ currentUser?.email }}</div>

        <q-form class="q-gutter-md" @submit.prevent="handleSubmit">
          <q-toggle
            v-model="formData.is_banned"
            label="Ban User"
            color="negative"
            :false-value="false"
            :true-value="true"
          />

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
        <q-btn label="Update" color="primary" @click="handleSubmit" :loading="loading" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { updateUser } from 'boot/axios'

const $q = useQuasar()
const showModal = ref(false)
const currentUser = ref(null)
const loading = ref(false)

const formData = ref({
  is_banned: false,
  roles: [],
})

const roleOptions = ['user', 'admin']

const emit = defineEmits(['updated'])

const open = (user) => {
  showModal.value = true
  currentUser.value = user

  formData.value = {
    is_banned: user.is_banned,
    roles: [...user.roles],
  }
}

const handleSubmit = async () => {
  try {
    loading.value = true

    const updateData = {}

    if (formData.value.is_banned !== currentUser.value.is_banned) {
      updateData.is_banned = formData.value.is_banned
    }

    const currentRoles = currentUser.value.roles.sort()
    const newRoles = [...formData.value.roles].sort()
    const rolesChanged = JSON.stringify(currentRoles) !== JSON.stringify(newRoles)

    if (rolesChanged) {
      updateData.roles = formData.value.roles
    }

    if (Object.keys(updateData).length > 0) {
      await updateUser(currentUser.value.email, updateData)

      $q.notify({
        type: 'positive',
        message: 'User updated successfully!',
        position: 'top',
      })

      showModal.value = false
      emit('updated')
    } else {
      $q.notify({
        type: 'info',
        message: 'No changes detected',
        position: 'top',
      })
      showModal.value = false
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to update user',
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
