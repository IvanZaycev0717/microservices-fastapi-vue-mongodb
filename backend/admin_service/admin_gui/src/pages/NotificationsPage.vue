<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="col">
        <h2 class="text-h4 q-mb-none">Notifications</h2>
        <p class="text-grey-7 q-mt-sm">Manage email notifications</p>
      </div>
    </div>

    <div class="row items-center q-gutter-md q-mb-lg">
      <q-input
        v-model="searchEmail"
        label="Search by email"
        type="email"
        outlined
        style="min-width: 300px"
        @keyup.enter="handleSearch"
      />
      <q-btn
        color="primary"
        icon="search"
        label="Find"
        @click="handleSearch"
        :loading="searchLoading"
      />
      <q-btn
        color="secondary"
        icon="email"
        label="Write Email"
        @click="sendEmailModalRef?.open()"
      />
      <q-btn
        color="grey"
        icon="refresh"
        label="Show All"
        @click="fetchAllNotifications"
        :loading="loading"
      />
    </div>

    <div v-if="loading" class="text-center q-pa-lg">
      <q-spinner size="50px" color="primary" />
      <div class="q-mt-md">Loading notifications...</div>
    </div>

    <div v-else class="notifications-list">
      <NotificationCard
        v-for="notification in notifications"
        :key="notification._id"
        :notification="notification"
        @delete="handleDeleteNotification"
      />
    </div>

    <div
      v-if="!loading && notifications.length === 0"
      class="column items-center justify-center q-pa-xl text-center"
    >
      <q-icon name="notifications" size="64px" color="grey-5" class="q-mb-md" />
      <h3 class="text-h5 q-mb-sm">No notifications found</h3>
      <p class="text-grey-7">
        {{
          searchEmail
            ? `No notifications found for email: ${searchEmail}`
            : 'No notifications in the system'
        }}
      </p>
    </div>

    <SendEmailModal ref="sendEmailModalRef" @sent="handleEmailSent" />
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import NotificationCard from 'components/NotificationCard.vue'
import SendEmailModal from 'components/SendEmailModal.vue'
import { getNotifications, getNotificationsByEmail, deleteNotification } from 'boot/axios'

const $q = useQuasar()
const notifications = ref([])
const searchEmail = ref('')
const loading = ref(false)
const searchLoading = ref(false)
const sendEmailModalRef = ref(null)

const fetchAllNotifications = async () => {
  try {
    loading.value = true
    searchEmail.value = ''
    const response = await getNotifications()
    notifications.value = response.data
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to load notifications',
      position: 'top',
    })
    notifications.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  if (!searchEmail.value.trim()) {
    fetchAllNotifications()
    return
  }

  try {
    searchLoading.value = true
    const response = await getNotificationsByEmail(searchEmail.value.trim())
    notifications.value = response.data
  } catch (error) {
    if (error.response?.status === 404) {
      notifications.value = []
      $q.notify({
        type: 'info',
        message: `No notifications found for email: ${searchEmail.value}`,
        position: 'top',
      })
    } else {
      $q.notify({
        type: 'negative',
        message: error.response?.data?.detail || 'Failed to search notifications',
        position: 'top',
      })
    }
  } finally {
    searchLoading.value = false
  }
}

const handleDeleteNotification = async (notificationId) => {
  try {
    await deleteNotification(notificationId)

    $q.notify({
      type: 'positive',
      message: 'Notification deleted successfully!',
      position: 'top',
    })

    notifications.value = notifications.value.filter(
      (notification) => notification._id !== notificationId,
    )
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to delete notification',
      position: 'top',
    })
  }
}

const handleEmailSent = () => {
  fetchAllNotifications()
}

onMounted(() => {
  fetchAllNotifications()
})
</script>

<style lang="scss" scoped>
.notifications-list {
  max-width: 900px;
  margin: 0 auto;
}
</style>
