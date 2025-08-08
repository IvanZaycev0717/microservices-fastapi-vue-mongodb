import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AboutMeIcon from '@icons/AboutMeIcon.vue'
import CerfIcon from '@icons/CerfIcon.vue'
import ContactIcon from '@icons/ContactIcon.vue'
import ProjIcon from '@icons/ProjIcon.vue'
import PubIcon from '@icons/PubIcon.vue'
import TechIcon from '@icons/TechIcon.vue'

export function useNavigation() {
  const { t } = useI18n()

  const buttonConfigs = [
    { icon: AboutMeIcon, translationKey: 'SidebarButton.AboutMe', routerName: 'about' },
    { icon: TechIcon, translationKey: 'SidebarButton.Technologies', routerName: 'technologies' },
    { icon: ProjIcon, translationKey: 'SidebarButton.Projects', routerName: 'projects' },
    { icon: CerfIcon, translationKey: 'SidebarButton.Certificates', routerName: 'certificates' },
    { icon: PubIcon, translationKey: 'SidebarButton.Publications', routerName: 'publications' },
    { icon: ContactIcon, translationKey: 'SidebarButton.Contacts', routerName: 'contacts' },
  ]

  const translatedButtons = computed(() =>
    buttonConfigs.map((btn) => ({
      ...btn,
      text: t(btn.translationKey),
    })),
  )

  return {
    translatedButtons,
  }
}
