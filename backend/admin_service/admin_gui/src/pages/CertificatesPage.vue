<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="col">
        <h2 class="text-h4 q-mb-none">Certificates</h2>
      </div>
      <div class="col-auto">
        <q-btn
          color="primary"
          icon="add"
          label="Create Certificate"
          @click="createModalRef?.open()"
        />
      </div>
    </div>

    <div class="certificates-list">
      <CertificateCard
        v-for="certificate in certificates"
        :key="certificate.id"
        :certificate="certificate"
        @delete="handleDeleteCertificate"
        @edit="handleEditCertificate"
      />
    </div>

    <CreateCertificateModal ref="createModalRef" @created="handleCertificateCreated" />

    <UpdateCertificateModal ref="updateModalRef" @updated="handleCertificateUpdated" />
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import CertificateCard from 'components/CertificateCard.vue'
import CreateCertificateModal from 'components/CreateCertificateModal.vue'
import UpdateCertificateModal from 'components/UpdateCertificateModal.vue'
import { getCertificates, deleteCertificate } from 'boot/axios'

const $q = useQuasar()
const certificates = ref([])
const createModalRef = ref(null)
const updateModalRef = ref(null)

const fetchCertificates = async () => {
  try {
    const response = await getCertificates('date_desc')
    certificates.value = response.data
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error,
      position: 'top',
    })
  }
}

const handleCertificateCreated = () => {
  fetchCertificates()
}

const handleCertificateUpdated = () => {
  fetchCertificates()
}

const handleDeleteCertificate = async (certificateId) => {
  try {
    await deleteCertificate(certificateId)

    $q.notify({
      type: 'positive',
      message: 'Certificate deleted successfully!',
      position: 'top',
    })

    certificates.value = certificates.value.filter((cert) => cert.id !== certificateId)
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to delete certificate',
      position: 'top',
    })
  }
}

const handleEditCertificate = (certificate) => {
  updateModalRef.value?.open(certificate)
}

onMounted(() => {
  fetchCertificates()
})
</script>

<style lang="scss" scoped>
.certificates-list {
  max-width: 700px;
  margin: 0 auto;
}
</style>
