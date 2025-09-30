<template>
  <div class="tech-cards">
    <!-- Загрузка -->
    <div v-if="loading" class="text-center q-pa-lg">
      <q-spinner size="50px" color="primary" />
    </div>

    <!-- Данные -->
    <div v-else-if="techData.length" class="row q-col-gutter-md">
      <div 
        v-for="kingdom in kingdoms" 
        :key="kingdom.key"
        class="col-12 col-sm-6 col-md-4"
      >
        <q-card class="tech-card">
          <q-card-section>
            <div class="text-h6">{{ kingdom.kingdom }}</div>
            <q-list dense>
              <q-item
                v-for="(skill, index) in kingdom.items"
                :key="index"
                class="skill-item"
              >
                <q-item-section>
                  <q-item-label>{{ skill }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn 
              icon="edit" 
              color="primary" 
              size="sm" 
              flat
              @click="handleEdit(kingdom)"
              label="Edit"
            />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <!-- Пустое состояние -->
    <div v-else class="text-center q-pa-lg">
      <p>No tech skills data available</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from 'boot/axios'

const emit = defineEmits(['edit-kingdom'])
const techData = ref([])
const loading = ref(true)

// Список всех kingdom ключей
const kingdomKeys = [
  'backend_kingdom',
  'database_kingdom', 
  'frontend_kingdom',
  'desktop_kingdom',
  'devops_kingdom',
  'telegram_kingdom',
  'parsing_kingdom',
  'computerscience_kingdom',
  'gamedev_kingdom',
  'ai_kingdom'
]

// Вычисляемое свойство для удобного доступа к kingdoms
const kingdoms = computed(() => {
  if (!techData.value.length) return []
  
  const data = techData.value[0] // Берем первый элемент массива
  return kingdomKeys
    .filter(key => data[key]) // Фильтруем существующие kingdoms
    .map(key => ({
      key: key,
      kingdom: data[key].kingdom,
      items: data[key].items
    }))
})

const fetchTechData = async () => {
  try {
    loading.value = true
    const response = await api.get('/technologies')
    techData.value = response.data
  } catch (error) {
    console.error('Error fetching tech data:', error)
    techData.value = []
  } finally {
    loading.value = false
  }
}

const handleEdit = (kingdom) => {
  emit('edit-kingdom', {
    key: kingdom.key,
    kingdom: kingdom.kingdom,
    items: kingdom.items
  })
}

onMounted(() => {
  fetchTechData()
})

defineExpose({
  fetchTechData
})
</script>

<style lang="scss" scoped>
.tech-cards {
  max-width: 1200px;
  margin: 0 auto;
}

.tech-card {
  height: 100%;
  
  .q-card__section {
    padding-bottom: 0;
  }
}

.skill-item {
  padding: 4px 0;
  
  .q-item__label {
    font-size: 0.9rem;
  }
}

.q-list {
  max-height: 200px;
  overflow-y: auto;
}
</style>