<template>
  <div class="breadcrumbs">
    <router-link
      v-for="(crumb, index) in crumbs"
      :key="index"
      :to="crumb.path"
      class="breadcrumb-link"
    >
      {{ crumb.title }}
      <span v-if="index < crumbs.length - 1" class="separator">/</span>
    </router-link>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const { t } = useI18n()

const crumbs = computed(() => {
  const pathArray = route.path.split('/').filter((item) => item)

  const breadcrumbs = pathArray.map((path, index) => {
    const routePath = `/${pathArray.slice(0, index + 1).join('/')}`

    return {
      path: routePath,
      title: getPageTitle(path),
    }
  })

  breadcrumbs.unshift({
    path: '/',
    title: t('SidebarButton.Main'),
  })

  return breadcrumbs
})

function getPageTitle(path) {
  const titles = {
    about: t('SidebarButton.AboutMe'),
    technologies: t('SidebarButton.Technologies'),
    projects: t('SidebarButton.Projects'),
    certificates: t('SidebarButton.Certificates'),
    publications: t('SidebarButton.Publications'),
    contacts: t('SidebarButton.Contacts'),
  }

  return titles[path] || path
}
</script>

<style scoped>
.breadcrumbs {
  font-size: 0.75rem;
  padding: 0;
}

.breadcrumb-link {
  text-decoration: none;
  color: var(--text-color);
}

.breadcrumb-link:hover {
  text-decoration: none;
}

.separator {
  margin: 0 5px;
  color: var(--sidebar-button-disabled);
}
</style>
