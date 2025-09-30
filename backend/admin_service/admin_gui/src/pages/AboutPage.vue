<template>
  <q-page class="q-pa-md">
    <div class="row justify-between items-center q-mb-md">
      <div class="text-h4">About</div>
      <q-btn 
        label="Create" 
        color="primary" 
        icon="add" 
        @click="openCreateModal" 
      />
    </div>
    <AboutCard ref="aboutCardRef" />
    <AboutCreateModal ref="createModalRef" @created="refreshAboutCards" />
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import AboutCard from 'components/AboutCard.vue'
import AboutCreateModal from 'components/AboutCreateModal.vue'

const aboutCardRef = ref(null)
const createModalRef = ref(null)

const openCreateModal = () => {
  createModalRef.value?.open()
}

const refreshAboutCards = () => {
  aboutCardRef.value?.fetchAboutData()
}
</script>