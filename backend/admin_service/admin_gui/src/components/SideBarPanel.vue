<template>
  <q-drawer
    v-model="leftDrawerOpen"
    show-if-above
    bordered
    :width="250"
    class="bg-primary text-white"
  >
    <q-list padding>
      <q-item-label header class="text-white">
        Admin Panel Menu
      </q-item-label>

      <q-item 
        clickable 
        v-ripple 
        to="/about"
        exact
        active-class="active-link"
      >
        <q-item-section avatar>
          <q-icon name="info" />
        </q-item-section>
        <q-item-section>About</q-item-section>
      </q-item>

      <q-item 
        clickable 
        v-ripple 
        to="/tech"
        exact
        active-class="active-link"
      >
        <q-item-section avatar>
          <q-icon name="code" />
        </q-item-section>
        <q-item-section>Tech Stack</q-item-section>
      </q-item>

      <q-item 
        clickable 
        v-ripple 
        to="/projects"
        exact
        active-class="active-link"
      >
        <q-item-section avatar>
          <q-icon name="folder" />
        </q-item-section>
        <q-item-section>Projects</q-item-section>
      </q-item>

      <q-item 
        clickable 
        v-ripple 
        to="/certificates"
        exact
        active-class="active-link"
      >
        <q-item-section avatar>
          <q-icon name="school" />
        </q-item-section>
        <q-item-section>Certificates</q-item-section>
      </q-item>

      <q-item 
        clickable 
        v-ripple 
        to="/publications"
        exact
        active-class="active-link"
      >
        <q-item-section avatar>
          <q-icon name="article" />
        </q-item-section>
        <q-item-section>Publications</q-item-section>
      </q-item>

      <q-item 
        clickable 
        v-ripple 
        to="/auth"
        exact
        active-class="active-link"
      >
        <q-item-section avatar>
          <q-icon name="security" />
        </q-item-section>
        <q-item-section>Auth</q-item-section>
      </q-item>

      <q-item 
        clickable 
        v-ripple 
        to="/comments"
        exact
        active-class="active-link"
      >
        <q-item-section avatar>
          <q-icon name="chat" />
        </q-item-section>
        <q-item-section>Comments</q-item-section>
      </q-item>

      <q-item 
        clickable 
        v-ripple 
        to="/notifications"
        exact
        active-class="active-link"
      >
        <q-item-section avatar>
          <q-icon name="notifications" />
        </q-item-section>
        <q-item-section>Notifications</q-item-section>
      </q-item>
    </q-list>
  </q-drawer>
</template>

<script setup>
import { ref } from 'vue'

const leftDrawerOpen = ref(true)
</script>

<style lang="scss" scoped>
.active-link {
  background-color: rgba(255, 255, 255, 0.1);
  border-left: 3px solid white;
  
  .q-item__section--avatar {
    .q-icon {
      color: white;
    }
  }
  
  .q-item__label {
    font-weight: bold;
  }
}

.q-item {
  transition: all 0.3s ease;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.05);
  }
}

.q-drawer {
  .q-list {
    .q-item-label {
      opacity: 0.8;
    }
  }
}
</style>