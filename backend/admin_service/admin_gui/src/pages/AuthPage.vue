<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="col">
        <h2 class="text-h4 q-mb-none">User Management</h2>
        <p class="text-grey-7 q-mt-sm">Manage users and their permissions</p>
      </div>
      <div class="col-auto">
        <q-btn
          color="primary"
          icon="add"
          label="Create User"
          @click="createModalRef?.open()"
        />
      </div>
    </div>

    <div class="users-list">
      <UserCard
        v-for="user in users"
        :key="user.id"
        :user="user"
        @delete="handleDeleteUser"
        @edit="handleEditUser"
      />
    </div>

    <CreateUserModal 
      ref="createModalRef" 
      @created="handleUserCreated"
    />
    
    <UpdateUserModal 
      ref="updateModalRef" 
      @updated="handleUserUpdated"
    />
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import UserCard from 'components/UserCard.vue'
import CreateUserModal from 'components/CreateUserModal.vue'
import UpdateUserModal from 'components/UpdateUserModal.vue'
import { getUsers, deleteUser } from 'boot/axios'

const $q = useQuasar()
const users = ref([])
const createModalRef = ref(null)
const updateModalRef = ref(null)

const fetchUsers = async () => {
  try {
    const response = await getUsers()
    users.value = response.data
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to load users',
      position: 'top'
    })
  }
}

const handleUserCreated = () => {
  fetchUsers()
}

const handleUserUpdated = () => {
  fetchUsers()
}

const handleDeleteUser = async (userEmail) => {
  try {
    await deleteUser(userEmail)
    
    $q.notify({
      type: 'positive',
      message: 'User deleted successfully!',
      position: 'top'
    })
    
    users.value = users.value.filter(user => user.email !== userEmail)
    
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to delete user',
      position: 'top'
    })
  }
}

const handleEditUser = (user) => {
  updateModalRef.value?.open(user)
}

onMounted(() => {
  fetchUsers()
})
</script>

<style lang="scss" scoped>
.users-list {
  max-width: 900px;
  margin: 0 auto;
}
</style>