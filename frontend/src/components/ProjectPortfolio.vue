<template>
  <div class="portfolio-container">
    <div class="projects-grid">
      <div
        v-for="project in translatedData"
        :key="project.id"
        class="project-card"
        @click="openModal(project)"
      >
        <img v-lazy="project.thumbnail" :alt="project.title" class="thumbnail" />
        <p class="project-title">{{ project.title }}</p>
      </div>
    </div>

    <div v-if="selectedProject" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeModal">×</button>
        
        <div class="modal-layout">
          <!-- Левая часть - проект -->
          <div class="project-side">
            <h3>{{ selectedProject.title }}</h3>
            <img v-lazy="selectedProject.image" :alt="selectedProject.title" class="modal-image" />
            <p>{{ selectedProject.description }}</p>
            <a
              v-if="selectedProject.link"
              :href="selectedProject.link"
              target="_blank"
              class="project-link"
            >
              {{ t('ProjectPortfolio.look') }}
            </a>
          </div>
          
          <!-- Правая часть - комментарии -->
          <div class="comments-side">
            <ProjectComments :projectId="selectedProject.id" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSortStore } from '@stores/sortStore.js'
import { useLanguageStore } from '@stores/languageStore.js'
import ProjectComments from '@components/ProjectComments.vue'
import axios from 'axios'

const { t } = useI18n()
const sortStore = useSortStore()
const languageStore = useLanguageStore()

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT),
})

const projects = ref([])
const loading = ref(false)
const selectedProject = ref(null)

const fetchProjects = async () => {
  try {
    loading.value = true
    const response = await apiClient.get(import.meta.env.VITE_API_CONTENT_PROJECTS, {
      params: {
        lang: languageStore.language,
        sort: sortStore.selectedOption,
      },
    })
    projects.value = response.data.projects || []
  } catch (err) {
    console.error('Ошибка загрузки проектов:', err)
    projects.value = []
  } finally {
    loading.value = false
  }
}

const translatedData = computed(() => projects.value || [])

onMounted(() => {
  fetchProjects()
})

watch([() => sortStore.selectedOption, () => languageStore.language], () => {
  fetchProjects()
})

const openModal = (project) => {
  selectedProject.value = project
  document.documentElement.style.overflow = 'hidden'
  document.body.style.overflow = 'hidden'
  document.body.style.position = 'fixed'
  document.body.style.width = '100%'
}

const closeModal = () => {
  selectedProject.value = null
  setTimeout(() => {
    document.documentElement.style.overflow = ''
    document.body.style.overflow = ''
    document.body.style.position = ''
    document.body.style.width = ''
    window.scrollTo(0, 0)
  }, 50)
}
</script>

<style scoped>
.portfolio-container {
  overflow-y: auto;
  padding: 0 0 50px 0;
  width: 100%;
  height: 100%;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  padding: 10px;
  width: 100%;
  box-sizing: border-box;
}

.project-card {
  cursor: pointer;
  transition:
    transform 0.3s,
    box-shadow 0.3s;
  border-radius: 8px;
  overflow: hidden;
  background: var(--hover-button-background-color);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.project-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.thumbnail {
  width: 100%;
  height: 240px;
  object-fit: cover;
  border-radius: 8px;
  transition:
    filter 0.4s ease-out,
    transform 0.4s cubic-bezier(0.2, 0.9, 0.4, 1.1);
  filter: blur(3px);
  transform: scale(1.05);
}

.project-card:hover .thumbnail {
  filter: blur(0.5px);
  transform: scale(1.08);
}

.project-title {
  margin: 1rem 0;
  font-weight: 600;
  text-align: center;
  padding: 0 1rem 1rem;
}

@media (max-width: 768px) {
  .projects-grid {
    grid-template-columns: 1fr;
  }
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: var(--hover-button-background-color);
  color: var(--text-color);
  padding: 2rem;
  border-radius: 8px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: hidden;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
}

.modal-content img {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
  margin: 1rem 0;
}

.project-link {
  display: inline-block;
  margin-top: 1rem;
  color: var(--sidebar-button-disabled);
  text-decoration: none;
  font-weight: bold;
}

.project-link:hover {
  text-decoration: underline;
}

.modal-image {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
  margin: 1rem 0;
  background: inherit;
}

img[lazy='loading'] {
  background: inherit;
  opacity: 0.8;
}
img[lazy='error'] {
  background: inherit;
}

.modal-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  height: 100%;
  
}

.project-side {
  display: flex;
  flex-direction: column;
}

.comments-side {
  border-left: none;
  padding-left: 1rem;
}

@media (max-width: 768px) {
  .modal-layout {
    grid-template-columns: 1fr;
  }
  .comments-side {
    padding-left: 0;
    padding-top: 1rem;
  }
}

.comments-section {
  padding: 0.5rem;
  height: 100%;
  width: 100%;
}

.comments-section h4 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
}

.comment-form {
  margin-bottom: 0.75rem;
}

.comment-form textarea {
  font-size: 0.875rem;
  padding: 0.375rem;
}

.comment-form button {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.comments-list {
  max-height: 400px;
}
</style>
