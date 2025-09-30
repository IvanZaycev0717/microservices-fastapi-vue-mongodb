<template>
  <q-page class="q-pa-md">
    <div class="row justify-between items-center q-mb-md">
      <div class="text-h4">Projects</div>
      <q-btn 
        label="Create Project" 
        color="primary" 
        icon="add" 
        @click="openCreateModal" 
      />
    </div>
    <ProjectCard ref="projectCardRef" @edit-project="openEditModal" />
    <ProjectCreateModal ref="createModalRef" @created="refreshProjects" />
    <ProjectEditModal ref="editModalRef" @updated="refreshProjects" />
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import ProjectCard from 'components/ProjectCard.vue'
import ProjectCreateModal from 'components/ProjectCreateModal.vue'
import ProjectEditModal from 'components/ProjectEditModal.vue'

const projectCardRef = ref(null)
const createModalRef = ref(null)
const editModalRef = ref(null)

const openCreateModal = () => {
  createModalRef.value?.open()
}

const openEditModal = (project) => {
  editModalRef.value?.open(project.id)
}

const refreshProjects = () => {
  projectCardRef.value?.fetchProjectsData()
}
</script>