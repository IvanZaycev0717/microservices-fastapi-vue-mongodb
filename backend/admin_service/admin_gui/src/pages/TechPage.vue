<template>
  <q-page class="q-pa-md">
    <div class="row justify-between items-center q-mb-md">
      <div class="text-h4">Tech Stack</div>
    </div>
    <TechCard ref="techCardRef" @edit-kingdom="openEditModal" />
    <TechEditModal ref="editModalRef" @updated="refreshTechData" />
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import TechCard from 'components/TechCard.vue'
import TechEditModal from 'components/TechEditModal.vue'

const techCardRef = ref(null)
const editModalRef = ref(null)

const openEditModal = (kingdomData) => {
  editModalRef.value?.open(kingdomData)
}

const refreshTechData = () => {
  techCardRef.value?.fetchTechData()
}
</script>
