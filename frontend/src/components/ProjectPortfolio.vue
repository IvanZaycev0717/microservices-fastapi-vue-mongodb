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
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

import { useI18n } from 'vue-i18n'

import { useSortStore } from '@stores/sortStore.js'

const sortStore = useSortStore()

const { t } = useI18n()



const projects = ref([
  {
    id: 1,
    title: 'Project 1',
    thumbnail: 'image1Thumb',
    image: 'image1',
    description: 'Project 1',
    link: 'https://example.com',
    date: new Date(2025, 2, 14),
    popularity: 2,
  },
  {
    id: 2,
    title: 'Project 2',
    thumbnail: 'image2Thumb',
    image: 'image2',
    description: 'Project 2',
    link: 'https://example.com',
    date: new Date(2024, 2, 14),
    popularity: 2,
  },
  {
    id: 3,
    title: 'Project 3',
    thumbnail: 'image3Thumb',
    image: 'image3',
    description: 'Project 3',
    link: 'https://example.com',
    date: new Date(2023, 2, 14),
    popularity: 2,
  },
])

const translatedData = computed(() => {
  const sortOption = sortStore.selectedOption
  const sortedProjects = sortProjects(sortOption)
  return sortedProjects.map((obj) => ({
    id: obj.id,
    title: obj.title,
    thumbnail: obj.thumbnail,
    image: obj.image,
    description: obj.description,
    link: obj.link,
    date: obj.date,
    popularity: obj.popularity,
  }))
})

function sortProjects(sortOption) {
  switch (sortOption) {
    case 'date_desc':
      return [...projects.value].sort((a, b) => b.date - a.date)
    case 'date_asc':
      return [...projects.value].sort((a, b) => a.date - b.date)
    case 'popular':
      return [...projects.value].sort((a, b) => b.popularity - a.popularity)
    default:
      return [...projects.value]
  }
}

const selectedProject = ref(null)

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
  overflow-y: auto;
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
</style>
