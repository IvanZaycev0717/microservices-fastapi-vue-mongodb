<template>
  <div class="ContactsView">
    <h2>{{ t('ContactsView.title') }}</h2>
    <p>{{ t('ContactsView.description') }}</p>
    <div class="cards__container">
      <div
        v-for="(contact, index) in contacts"
        :key="index"
        class="contact-card"
        @mouseenter="hoverCard(index)"
        @mouseleave="resetCards"
        :style="{
          transform: `rotateY(${activeIndex === index ? 0 : -15}deg) rotateX(${activeIndex === index ? 0 : 10}deg)`,
          zIndex: activeIndex === index ? 2 : 1,
          background: contact.background,
        }"
      >
        <a :href="contact.link" target="_blank" rel="noopener noreferrer">
          <img :src="contact.image" :alt="contact.name" class="contact-icon" />
          <div class="contact-name">{{ contact.name }}</div>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import githubIcon from '@assets/social/github-icon.png'
import telegramIcon from '@assets/social/telegram-icon.png'
import leetcodeIcon from '@assets/social/leetcode-icon.png'
const { t } = useI18n()

const activeIndex = ref(null)

const contacts = ref([
  {
    name: 'GitHub',
    link: 'https://github.com/IvanZaycev0717/',
    image: githubIcon,
    background: 'linear-gradient(135deg, #333333, #6e5494)',
  },
  {
    name: 'Telegram',
    link: 'https://t.me/ivanzaycev0717',
    image: telegramIcon,
    background: 'linear-gradient(135deg, #0088cc, #34aadc)',
  },
  {
    name: 'LeetCode',
    link: 'https://leetcode.com/u/IvanZaycev0717/',
    image: leetcodeIcon,
    background: 'linear-gradient(135deg, #f89f1b, #f37021)',
  },
])

const hoverCard = (index) => {
  activeIndex.value = index
}

const resetCards = () => {
  activeIndex.value = null
}
</script>

<style scoped>
.ContactsView {
  display: flex;
  flex-direction: column;
}

.ContactsView h2 {
  margin: 0;
}

.ContactsView p {
  margin: 5px 0 5px 0;
}

.cards__container {
  display: flex;
  justify-content: space-around;
  align-items: center;
  flex-wrap: wrap;
}

.contact-card {
  width: 150px;
  height: 200px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition:
    transform 0.5s ease,
    box-shadow 0.3s ease;
  transform-style: preserve-3d;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.contact-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.contact-card:hover::before {
  opacity: 1;
}

.contact-card a {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  color: white;
  height: 100%;
  width: 100%;
  justify-content: center;
  padding: 1rem;
  box-sizing: border-box;
}

.contact-icon {
  width: 60px;
  height: 60px;
  object-fit: contain;
  margin-bottom: 1rem;
  transition: transform 0.3s ease;
}

.contact-card:hover .contact-icon {
  transform: scale(1.1);
}

.contact-name {
  font-size: 1.2rem;
  font-weight: 600;
  text-align: center;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}
</style>
