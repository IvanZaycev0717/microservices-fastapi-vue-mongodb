import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import axios from 'axios'

export function useSkills() {
  const { t } = useI18n()

  const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: parseInt(import.meta.env.VITE_API_TIMEOUT),
    headers: {
      'Content-Type': 'application/json',
    },
  })

  const loading = ref(true)
  const error = ref(null)

  const fetchTechData = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await apiClient.get(import.meta.env.VITE_API_CONTENT_TECH)
      return response
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  const BASE_SKILLS_DATA = {
    backend_kingdom: {
      kingdom: 'Backend',
      items: [
        'Skill 1',
        'Skill 2',
      ],
    },
    database_kingdom: {
      kingdom: 'Databases',
      items: [
        'Skill 1',
        'Skill 2',
      ],
    },
    frontend_kingdom: {
      kingdom: 'Frontend',
      items: [
        'Skill 1',
        'Skill 2',
      ],
    },
    desktop_kingdom: {
      kingdom: 'Desktop',
      items: [
        'Skill 1',
        'Skill 2',
      ],
    },
    devops_kingdom: {
      kingdom: 'DevOps',
      items: [
        'Skill 1',
        'Skill 2',
      ],
    },
    telegram_kingdom: {
      kingdom: 'Telegram',
      items: [
        'Skill 1',
        'Skill 2',
      ],
    },
    parsing_kingdom: {
      kingdom: 'Parsing',
      items: [
        'Skill 1',
        'Skill 2',
      ],
    },
    computerscience_kingdom: {
      kingdom: 'ComputerScience',
      items: [
        'Skill 1',
        'Skill 2',
      ],
    },
    gamedev_kingdom: {
      kingdom: 'GameDev',
      items: [
        'Skill 1',
        'Skill 2',
      ],
    },
    ai_kingdom: {
      kingdom: 'AI',
      items: [
        'Skill 1',
        'Skill 2',
      ],
    },
  }

  const skillsData = computed(() => {
    return Object.entries(BASE_SKILLS_DATA).reduce((acc, [key, category]) => {
      acc[key] = {
        kingdom: t(`MapMarkers.${category.kingdom}`, { defaultValue: category.kingdom }),
        items: category.items.map((item) => {
          const translation = t(`MapMarkers.${item}`, { defaultValue: item })
          return translation.startsWith('MapMarkers.')
            ? translation.slice('MapMarkers.'.length)
            : translation
        }),
      }
      return acc
    }, {})
  })

  return [skillsData, fetchTechData, loading, error]
}