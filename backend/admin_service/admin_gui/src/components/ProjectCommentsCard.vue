<template>
  <div class="project-comments-cards">
    <!-- Загрузка -->
    <div v-if="loading" class="text-center q-pa-lg">
      <q-spinner size="50px" color="primary" />
    </div>

    <!-- Данные -->
    <div v-else-if="projects.length" class="row q-col-gutter-md">
      <div 
        v-for="project in projects" 
        :key="project.id"
        class="col-12 col-sm-6 col-lg-4"
      >
        <q-card class="project-comments-card">
          <!-- Изображение проекта -->
          <q-img
            :src="project.thumbnail"
            height="200px"
            class="project-thumbnail"
          />

          <q-card-section>
            <!-- Заголовки -->
            <div class="text-h6">{{ project.title.ru }}</div>
            <div class="text-subtitle2 text-grey">{{ project.title.en }}</div>

            <!-- Мета-информация -->
            <div class="row items-center justify-between q-mt-md">
              <div class="text-caption text-grey">
                {{ formatDate(project.date) }}
              </div>
              <q-badge 
                :color="getPopularityColor(project.popularity)"
                :label="`Popularity: ${project.popularity}`"
              />
            </div>
          </q-card-section>

          <!-- Кнопка Show Comments -->
          <q-card-actions vertical>
            <q-btn 
              color="primary" 
              icon="chat"
              :label="`Show Comments (${getCommentCount(project.id)})`"
              no-caps
              class="full-width"
              @click="handleShowComments(project)"
              :loading="commentLoading[project.id]"
            />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <!-- Пустое состояние -->
    <div v-else class="text-center q-pa-lg">
      <p>No projects available</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { getProjects, getCommentsByProjectId } from 'boot/axios'

const emit = defineEmits(['show-comments'])
const $q = useQuasar()
const projects = ref([])
const loading = ref(true)
const commentCounts = ref({})
const commentLoading = ref({})

const fetchProjectsData = async () => {
  try {
    loading.value = true
    const response = await getProjects()
    projects.value = response.data
    
    // Загружаем количество комментариев для каждого проекта
    await loadCommentCounts()
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to load projects: ' + (error.response?.data?.detail || 'Network error')
    })
    projects.value = []
  } finally {
    loading.value = false
  }
}

const loadCommentCounts = async () => {
  for (const project of projects.value) {
    try {
      commentLoading.value[project.id] = true
      const response = await getCommentsByProjectId(project.id)
      commentCounts.value[project.id] = response.data.length
    } catch (error) {
      // Если комментариев нет или ошибка - показываем 0
      error
      commentCounts.value[project.id] = 0
    } finally {
      commentLoading.value[project.id] = false
    }
  }
}

const getCommentCount = (projectId) => {
  return commentCounts.value[projectId] || 0
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}

const getPopularityColor = (popularity) => {
  if (popularity >= 10) return 'positive'
  if (popularity >= 5) return 'warning'
  return 'grey'
}

const handleShowComments = (project) => {
  emit('show-comments', project)
}

onMounted(() => {
  fetchProjectsData()
})

defineExpose({
  fetchProjectsData
})
</script>

<style lang="scss" scoped>
.project-comments-cards {
  max-width: 1400px;
  margin: 0 auto;
}

.project-comments-card {
  height: 100%;
  transition: transform 0.2s ease;

  &:hover {
    transform: translateY(-4px);
  }
}

.project-thumbnail {
  border-bottom: 1px solid #e0e0e0;
}

.q-card__actions {
  border-top: 1px solid #e0e0e0;
}
</style>