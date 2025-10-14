<template>
  <div class="PublicationsView">
    <h2>{{ t('SidebarButton.Publications') }}</h2>
    <p>{{ t('PublicationsView.description') }}</p>
    <EasyDataTable
      :headers="translatedHeaders"
      :items="formattedArticles"
      table-class-name="customize-table"
      :rows-per-page="10"
      hide-footer
    >
      <template #item-title="{ title, page }">
        <a :href="page" target="_blank" class="article-link">{{ title }}</a>
      </template>

      <template #item-site="{ site }">
        <a :href="site" target="_blank" class="site-link">{{ site }}</a>
      </template>

      <template #item-rating="{ rating }">
        <span class="rating-badge">{{ rating }}</span>
      </template>
    </EasyDataTable>
  </div>
</template>


<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import { useSortStore } from '@stores/sortStore.js'
import { useLanguageStore } from '@stores/languageStore.js'

const { t } = useI18n()
const sortStore = useSortStore()
const languageStore = useLanguageStore()

const articles = ref([])
const loading = ref(false)

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT),
})

const fetchPublications = async () => {
  try {
    loading.value = true
    const response = await apiClient.get(import.meta.env.VITE_API_CONTENT_PUBLICATIONS, {
      params: {
        lang: languageStore.language,
        sort: sortStore.selectedOption
      }
    })
    articles.value = response.data.publications || []
  } catch (err) {
    console.error('Ошибка загрузки публикаций:', err)
    articles.value = []
  } finally {
    loading.value = false
  }
}

const translatedHeaders = computed(() => [
  { text: t('PublicationsView.title'), value: 'title' },
  { text: t('PublicationsView.site'), value: 'site' },
  { text: t('PublicationsView.rating'), value: 'rating' },
  { text: t('PublicationsView.pub_date'), value: 'date', width: 150 },
])

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}.${month}.${year}`
}

const formattedArticles = computed(() => {
  return (articles.value || []).map(article => ({
    ...article,
    date: formatDate(article.date)
  }))
})

onMounted(() => {
  fetchPublications()
})

watch([() => sortStore.selectedOption, () => languageStore.language], () => {
  fetchPublications()
})
</script>

<style scoped>
.PublicationsView {
  overflow-y: auto;
}

.PublicationsView h2 {
  margin: 0;
}
.PublicationsView p {
  margin-top: 5px;
  margin-bottom: 5px;
}

.customize-table {
  --easy-table-border: none;
  --easy-table-row-border: none;

  --easy-table-header-height: 50px;
  --easy-table-header-background-color: var(--selection-color);
  --easy-table-header-font-color: var(--text-color);

  --easy-table-body-row-font-color: var(--text-color);
  --easy-table-body-row-background-color: var(--multiselect-conten-wrapper-background-color);
  --easy-table-body-row-hover-background-color: var(--multiselect-new-selection-color);
  --easy-table-body-row-hover-font-color: var(--text-color);

  --easy-table-header-font-size: var(--table-header-font-size);
  --easy-table-body-row-font-size: var(--table-row-font-size);
}

@media (min-width: 1440px) {
  .customize-table {
    --easy-table-header-font-size: 1.2rem;
    --easy-table-body-row-font-size: 1.1rem;
  }
}

.article-link {
  color: #3498db;
  text-decoration: none;
  transition: color 0.3s;
  font-weight: 500;
}

.article-link:hover {
  color: #2980b9;
  text-decoration: underline;
}

.site-link {
  color: #27ae60;
  text-decoration: none;
  transition: color 0.3s;
}

.site-link:hover {
  color: #219653;
  text-decoration: underline;
}

.rating-badge {
  display: inline-block;
  padding: 2px 8px;
  background-color: #219653;
  color: #fff;
  border-radius: 10px;
  font-weight: bold;
  font-size: 0.9em;
}
</style>
