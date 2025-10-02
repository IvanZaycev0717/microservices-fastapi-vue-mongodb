<template>
  <q-card class="publication-card q-mb-md">
    <div class="card-actions">
      <q-btn
        icon="edit"
        color="primary"
        size="sm"
        round
        flat
        class="action-btn q-mr-xs"
        @click="handleEdit"
      />
      <q-btn
        icon="delete"
        color="negative"
        size="sm"
        round
        flat
        class="action-btn"
        @click="handleDelete"
        :loading="deleteLoading"
      />
    </div>

    <q-card-section class="q-pa-md">
      <div class="row items-start q-col-gutter-md">
        <div class="col-12 col-md-6">
          <div class="text-subtitle2 text-grey-7 q-mb-xs">English</div>
          <div class="text-h6 q-mb-sm">{{ publication.title.en }}</div>
        </div>

        <div class="col-12 col-md-6">
          <div class="text-subtitle2 text-grey-7 q-mb-xs">Russian</div>
          <div class="text-h6 q-mb-sm">{{ publication.title.ru }}</div>
        </div>
      </div>

      <q-separator class="q-my-md" />

      <div class="row items-center q-col-gutter-md">
        <div class="col-12 col-sm-6">
          <div class="row items-center q-gutter-xs">
            <q-icon name="link" size="16px" color="primary" />
            <a :href="publication.page" target="_blank" class="text-primary"> Page Link </a>
          </div>
          <div class="row items-center q-gutter-xs q-mt-xs">
            <q-icon name="public" size="16px" color="secondary" />
            <a :href="publication.site" target="_blank" class="text-secondary"> Site Link </a>
          </div>
        </div>

        <div class="col-12 col-sm-6">
          <div class="row items-center justify-end q-gutter-md">
            <q-badge color="orange" class="q-px-sm q-py-xs">
              <q-icon name="star" class="q-mr-xs" size="12px" />
              Rating: {{ publication.rating }}
            </q-badge>
            <div class="text-caption text-grey">
              {{ formatDate(publication.date) }}
            </div>
          </div>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const props = defineProps({
  publication: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      title: {
        en: '',
        ru: '',
      },
      page: '',
      site: '',
      rating: 0,
      date: '',
    }),
  },
})

const emit = defineEmits(['delete', 'edit'])
const deleteLoading = ref(false)

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const handleEdit = () => {
  emit('edit', props.publication)
}

const handleDelete = () => {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Are you sure you want to delete "${props.publication.title.en}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      deleteLoading.value = true
      emit('delete', props.publication.id)
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: error,
        position: 'top',
      })
    } finally {
      deleteLoading.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.publication-card {
  width: 100%;
  position: relative;
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

a {
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
}
</style>
