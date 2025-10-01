<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="col">
        <h2 class="text-h4 q-mb-none">Publications</h2>
      </div>
      <div class="col-auto">
        <q-btn
          color="primary"
          icon="add"
          label="Create Publication"
          @click="createModalRef?.open()"
        />
      </div>
    </div>

    <div class="publications-list">
      <PublicationCard
        v-for="publication in publications"
        :key="publication.id"
        :publication="publication"
        @delete="handleDeletePublication"
        @edit="handleEditPublication"
      />
    </div>

    <CreatePublicationModal 
      ref="createModalRef" 
      @created="handlePublicationCreated"
    />
    
    <UpdatePublicationModal 
      ref="updateModalRef" 
      @updated="handlePublicationUpdated"
    />
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import PublicationCard from 'components/PublicationCard.vue'
import CreatePublicationModal from 'components/CreatePublicationModal.vue'
import UpdatePublicationModal from 'components/UpdatePublicationModal.vue'
import { getPublications, deletePublication } from 'boot/axios'

const $q = useQuasar()
const publications = ref([])
const createModalRef = ref(null)
const updateModalRef = ref(null)

const fetchPublications = async () => {
  try {
    const response = await getPublications('Each lang', 'date_desc')
    publications.value = response.data
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to load publications',
      position: 'top'
    })
  }
}

const handlePublicationCreated = () => {
  fetchPublications()
}

const handlePublicationUpdated = () => {
  fetchPublications()
}

const handleDeletePublication = async (publicationId) => {
  try {
    await deletePublication(publicationId)
    
    $q.notify({
      type: 'positive',
      message: 'Publication deleted successfully!',
      position: 'top'
    })
    
    publications.value = publications.value.filter(pub => pub.id !== publicationId)
    
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to delete publication',
      position: 'top'
    })
  }
}

const handleEditPublication = (publication) => {
  updateModalRef.value?.open(publication)
}

onMounted(() => {
  fetchPublications()
})
</script>

<style lang="scss" scoped>
.publications-list {
  max-width: 900px;
  margin: 0 auto;
}
</style>