<template>
  <Teleport to="body">
    <Transition name="toast-top">
      <div
        v-if="isVisible"
        class="toast-top"
        :class="type"
        @mouseenter="pauseTimeout"
        @mouseleave="resumeTimeout"
      >
        <div class="toast-content">
          <span>{{ message }}</span>
        </div>
        <button class="toast-close" @click="hide">&times;</button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  message: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value),
  },
  duration: {
    type: Number,
    default: 3000,
  },
})

const emit = defineEmits(['close'])

const isVisible = ref(false)
let timeoutId = null
let remainingTime = props.duration
let startTime = 0

const show = () => {
  isVisible.value = true
  startTimer()
}

const hide = () => {
  clearTimeout(timeoutId)
  isVisible.value = false
  emit('close')
}

const startTimer = () => {
  startTime = Date.now()
  timeoutId = setTimeout(hide, remainingTime)
}

const pauseTimeout = () => {
  clearTimeout(timeoutId)
  remainingTime -= Date.now() - startTime
}

const resumeTimeout = () => {
  startTimer()
}

onMounted(() => {
  show()
})

onUnmounted(() => {
  clearTimeout(timeoutId)
})

defineExpose({
  show,
  hide,
})
</script>

<style scoped>
.toast-top {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 4px;
  color: black;
  display: flex;
  align-items: center;
  max-width: 80%;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  z-index: 9999;
  animation: toast-in-top 0.3s ease;
}

.toast-top.success {
  background-color: #4caf50;
  border: 1px solid #388e3c;
}

.toast-top.error {
  background-color: #f44336;
  border: 1px solid #d32f2f;
}

.toast-top.warning {
  background-color: #ff9800;
  border: 1px solid #f57c00;
}

.toast-top.info {
  background-color: #2196f3;
  border: 1px solid #1976d2;
}

.toast-content {
  padding-right: 20px;
}

.toast-close {
  margin-left: 10px;
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}

.toast-top-enter-active,
.toast-top-leave-active {
  transition: all 0.3s ease;
}

.toast-top-enter-from,
.toast-top-leave-to {
  opacity: 0;
  transform: translate(-50%, -30px);
}

@keyframes toast-in-top {
  from {
    opacity: 0;
    transform: translate(-50%, -30px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style>
