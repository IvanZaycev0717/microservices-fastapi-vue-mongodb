<template>
  <div class="modal-overlay" @click.self="handleClose">
    <div class="modal-content">
      <div class="modal-header">
        <slot name="title">
          <h2></h2>
        </slot>
        <button class="close-button" @click="handleClose">
          <svg
            width="14"
            height="14"
            viewBox="0 0 14 14"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M1 1L13 13M13 1L1 13"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <slot name="skills_list">
          <ul>
            <li></li>
          </ul>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['close'])

const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  perspective: 1000px;
}

.modal-content {
  background: var(--selection-color);
  padding: 20px;
  border-radius: 8px;
  min-width: 300px;
  max-width: 80%;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
  color: var(--text-color);
  border: 2px solid;
  border-color: var(--text-color);
  transform-style: preserve-3d;
  backface-visibility: hidden;
}

.modal-header {
  display: flex;
  justify-content: center;
  align-items: center;
  backface-visibility: hidden;
}

.close-button {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  color: var(--text-color);
  transition: color 0.2s;
  backface-visibility: hidden;
}

.close-button:hover {
  color: var(--button-background-color);
}

.close-button svg {
  display: block;
}

.modal-body {
  max-height: 70vh;
  overflow-y: auto;
  backface-visibility: hidden;
}
</style>
