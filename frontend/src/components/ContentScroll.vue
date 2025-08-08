<template>
  <div class="ContentScroll">
    <div class="content-panel">
      <BreadcrumbsPanel />
      <SortControl />
    </div>

    <router-view></router-view>
  </div>
</template>
<script setup>
import BreadcrumbsPanel from '@components/BreadcrumbsPanel.vue'
import SortControl from '@components/SortControl.vue'
</script>
<style>
.ContentScroll {
  height: 85%;
  background-color: var(--button-background-color);
  color: var(--text-color);

  display: flex;
  flex-direction: column;
  flex: 1;

  margin-top: 0;
  margin-left: 10px;
  padding: 20px;

  text-align: justify;

  border-radius: 10px;

  overscroll-behavior: contain;
  overflow-y: hidden;
}

.content-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

@media (max-width: 768px) {
  .ContentScroll {
    width: 100%;
    padding: 10px;
    margin: 0;
    height: 95%;
  }
}
</style>
