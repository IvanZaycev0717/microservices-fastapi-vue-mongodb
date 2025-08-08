<template>
  <div class="PublicationsView">
    <h2>{{ t('SidebarButton.Publications') }}</h2>
    <p>{{ t('PublicationsView.description') }}</p>
    <EasyDataTable
      :headers="translatedHeaders"
      :items="sortedArticles"
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
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import { useSortStore } from '@stores/sortStore.js'

const sortStore = useSortStore()

const articles = ref([
  {
    id: 1,
    title: 'Some random text',
    page: 'https://example.com',
    site: 'https://example.com',
    rating: 18,
    date: '08.08.2025',
  },
])

const translatedHeaders = computed(() => [
  {
    text: t('PublicationsView.title'),
    value: 'title',
  },
  {
    text: t('PublicationsView.site'),
    value: 'site',
  },
  {
    text: t('PublicationsView.rating'),
    value: 'rating',
  },
  {
    text: t('PublicationsView.pub_date'),
    value: 'date',
    width: 150,
  },
])

const parseDate = (dateString) => {
  const [day, month, year] = dateString.split('.')
  return new Date(`${month}.${day}.${year}`)
}

const sortedArticles = computed(() => {
  const articlesBefore = [...articles.value]

  switch (sortStore.selectedOption) {
    case 'date_desc':
      return articlesBefore.sort((a, b) => parseDate(b.date) - parseDate(a.date))
    case 'date_asc':
      return articlesBefore.sort((a, b) => parseDate(a.date) - parseDate(b.date))
    case 'popular':
      return articlesBefore.sort((a, b) => b.rating - a.rating)
    default:
      return articlesBefore
  }
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
