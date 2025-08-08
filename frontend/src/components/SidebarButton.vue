<template>
  <button
    :class="[
      'sidebar-button',
      {
        'sidebar-button--active': active,
        'sidebar-button--disabled': disabled,
      },
    ]"
    :disabled="disabled"
    @click="handleClick"
  >
    <slot />
  </button>
</template>

<script setup>
const props = defineProps({
  disabled: Boolean,
})

const emit = defineEmits(['click'])

const handleClick = () => {
  if (!props.disabled) {
    emit('click')
  }
}
</script>

<style scoped>
.sidebar-button {
  width: 100%;
  height: 7vh;
  padding: 8px 16px;

  background: var(--button-background-color);
  font-family: 'MyFont', sans-serif;
  font-size: 1rem;
  color: var(--sidebar-button-active);

  border-radius: 10px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-button--disabled {
  background-color: var(--hover-button-background-color);
  font-weight: bold;
  border: var(--sidebar-border);
  color: var(--sidebar-button-disabled);
}

.sidebar-button--disabled:hover {
  cursor: default !important;
}

@media (min-width: 1440px) {
  .sidebar-button {
    font-size: 1.5rem;
  }
}

@media (min-width: 2560px) {
  .sidebar-button {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .sidebar-button {
    font-size: 1rem;
    height: 100%;
    background: transparent;
    border: 0;
    text-align: start;
    padding: 0px 16px 0px 0px;
  }
  .sidebar-button:hover {
    font-weight: bold;
  }
}

.sidebar-button:hover {
  background-color: var(--hover-button-background-color);
}
</style>
