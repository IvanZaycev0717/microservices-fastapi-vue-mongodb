<template>
  <q-page class="q-pa-lg">
    <div class="row items-center q-mb-md">
      <div class="col">
        <h2 class="text-h4 q-mb-none">Comments</h2>
        <p class="text-grey-7 q-mt-sm">Moderate comments for projects</p>
      </div>
    </div>

    <ProjectCommentsCard @show-comments="handleShowComments" />

    <ProjectCommentsModal ref="commentsModalRef" />
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import ProjectCommentsCard from 'components/ProjectCommentsCard.vue'
import ProjectCommentsModal from 'components/ProjectCommentsModal.vue'

const commentsModalRef = ref(null)

const handleShowComments = (project) => {
  commentsModalRef.value?.open(project)
}
</script>
