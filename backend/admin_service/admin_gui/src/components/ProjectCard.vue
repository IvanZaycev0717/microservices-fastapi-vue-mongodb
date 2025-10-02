<template>
  <div class="project-cards">
    <div v-if="loading" class="text-center q-pa-lg">
      <q-spinner size="50px" color="primary" />
    </div>

    <div v-else-if="projects.length" class="row q-col-gutter-md">
      <div v-for="project in projects" :key="project.id" class="col-12 col-sm-6 col-lg-4">
        <q-card class="project-card">
          <div class="card-actions">
            <q-btn
              icon="edit"
              color="primary"
              size="sm"
              round
              flat
              @click="handleEdit(project)"
              class="action-btn q-mr-xs"
            />
            <q-btn
              icon="delete"
              color="negative"
              size="sm"
              round
              flat
              @click="confirmDelete(project)"
              class="action-btn"
            />
          </div>

          <q-img :src="project.thumbnail" height="200px" class="project-thumbnail" />

          <q-card-section>
            <div class="text-h6">{{ project.title.ru }}</div>
            <div class="text-subtitle2 text-grey">{{ project.title.en }}</div>

            <div class="q-mt-sm">
              <div class="text-body2">{{ project.description.ru }}</div>
              <div class="text-caption text-grey">{{ project.description.en }}</div>
            </div>

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

          <q-card-actions vertical>
            <q-btn
              :href="project.link"
              target="_blank"
              color="primary"
              icon="open_in_new"
              label="View Project"
              no-caps
              class="full-width"
            />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <div v-else class="text-center q-pa-lg">
      <p>No projects available</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { getProjects, deleteProject } from 'boot/axios'

const emit = defineEmits(['edit-project'])
const $q = useQuasar()
const projects = ref([])
const loading = ref(true)

const fetchProjectsData = async () => {
  try {
    loading.value = true
    const response = await getProjects()
    projects.value = response.data
    if (projects.value.length > 0 && !projects.value[0].id) {
      console.warn('Project structure warning: id not found')
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to load projects: ' + (error.response?.data?.detail || 'Network error'),
    })
    projects.value = []
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}

const getPopularityColor = (popularity) => {
  if (popularity >= 10) return 'positive'
  if (popularity >= 5) return 'warning'
  return 'grey'
}

const handleEdit = (project) => {
  emit('edit-project', project)
}

const confirmDelete = (project) => {
  const projectId = project.id

  if (!projectId) {
    console.warn('Project ID not found in:', Object.keys(project))
    $q.notify({
      type: 'negative',
      message: 'Invalid project data - ID not found',
    })
    return
  }

  $q.dialog({
    title: 'Confirm Delete',
    message: `Are you sure you want to delete "${project.title?.en || 'Unknown Project'}"?`,
    cancel: true,
    persistent: true,
  }).onOk(() => {
    deleteProjectHandler(project, projectId)
  })
}

const deleteProjectHandler = async (project, projectId) => {
  try {
    await deleteProject(projectId)

    $q.notify({
      type: 'positive',
      message: 'Project deleted successfully!',
    })

    projects.value = projects.value.filter((p) => p.id !== projectId)
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to delete project',
    })
  }
}

onMounted(() => {
  fetchProjectsData()
})

defineExpose({
  fetchProjectsData,
})
</script>

<style lang="scss" scoped>
.project-cards {
  max-width: 1400px;
  margin: 0 auto;
}

.project-card {
  height: 100%;
  position: relative;
  transition: transform 0.2s ease;

  &:hover {
    transform: translateY(-4px);
  }
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

.project-thumbnail {
  border-bottom: 1px solid #e0e0e0;
}

.q-card__actions {
  border-top: 1px solid #e0e0e0;
}
</style>
