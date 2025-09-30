<template>
  <div class="about-cards">
    <!-- Загрузка -->
    <div v-if="loading" class="text-center q-pa-lg">
      <q-spinner size="50px" color="primary" />
    </div>

    <!-- Данные -->
    <q-card
      v-for="card in cards"
      :key="card._id"
      class="about-card q-mb-md"
      v-else-if="cards.length"
    >
      <div class="card-actions">
        <q-btn 
          icon="edit" 
          color="primary" 
          size="sm" 
          round 
          flat
          @click="handleEdit(card)"
          class="action-btn q-mr-xs"
        />
        <q-btn 
          icon="delete" 
          color="negative" 
          size="sm" 
          round 
          flat
          @click="confirmDelete(card)"
          class="action-btn"
        />
      </div>

      <div class="row no-wrap">
        <div class="col-auto">
          <q-img
            :src="card.image_url"
            height="200px"
            width="200px"
          />
        </div>

        <div class="col q-pa-md">
          <div class="q-mb-md">
            <div class="text-h6">{{ card.translations.ru.title }}</div>
            <div class="text-body1">{{ card.translations.ru.description }}</div>
          </div>

          <div>
            <div class="text-h6">{{ card.translations.en.title }}</div>
            <div class="text-body1">{{ card.translations.en.description }}</div>
          </div>
        </div>
      </div>
    </q-card>

    <!-- Пустое состояние -->
    <div v-else class="text-center q-pa-lg">
      <p>No data available</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const cards = ref([])
const loading = ref(true)

const fetchAboutData = async () => {
  try {
    loading.value = true
    const response = await api.get('/about')
    cards.value = response.data
  } catch (error) {
    console.error('Error fetching about data:', error)
    cards.value = []
  } finally {
    loading.value = false
  }
}

const handleEdit = (card) => {
  console.log('Edit card:', card)
}

const confirmDelete = (card) => {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Are you sure you want to delete "${card.translations.en.title}"?`,
    cancel: true,
    persistent: true
  }).onOk(() => {
    deleteCard(card)
  })
}

const deleteCard = async (card) => {
  try {
    await api.delete(`/about/${card._id}`)
    
    $q.notify({
      type: 'positive',
      message: 'Card deleted successfully!'
    })
    
    cards.value = cards.value.filter(c => c._id !== card._id)
    
  } catch (error) {
    console.error('Error deleting card:', error)
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to delete card'
    })
  }
}

onMounted(() => {
  fetchAboutData()
})

defineExpose({
  fetchAboutData
})
</script>

<style lang="scss" scoped>
.about-cards {
  max-width: 800px;
  margin: 0 auto;
}

.about-card {
  max-width: 700px;
  position: relative;
}

.card-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
}

.action-btn {
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  
  &:hover {
    background-color: rgba(255, 255, 255, 1);
  }
}
</style>