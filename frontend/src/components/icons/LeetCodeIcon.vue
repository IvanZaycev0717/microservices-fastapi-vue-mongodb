<template>
  <a
    :href="leetcodeUrl"
    target="_blank"
    rel="noopener noreferrer"
    class="leetcode-link"
    aria-label="My LeetCode profile"
  >
    <svg
      viewBox="0 0 2500 2500"
      xmlns="http://www.w3.org/2000/svg"
      class="leetcode-icon"
      aria-hidden="true"
    >
      <path
        class="st2"
        d="M1110.6,785.6c-149.9,149.8-304.7,295.5-451,449.5-108.4,114.1-99.9,278.1,13.7,395.3,134.7,138.4,273.4,272.7,410.3,408.8,51.8,53.6,51.1,114.9,13.2,171.8-35.1,52.4-85.6,84.6-154,55.1-32.3-15.8-61.7-36.9-87.1-62.4-126.4-127.7-255.7-252.6-380.8-381.8-219.4-226.6-221.9-567.4-1.2-792.5,310.2-317,625-629,938.6-942.4,69.1-69.1,155.8-73.6,212.5-14.7,56.6,58.9,51.3,135.9-15.6,206.3-70.3,73.9-140.8,147.5-211.6,220.8-74.9,116.2-175.3,206.6-286.7,286.2h0Z"
      />
      <path
        class="st0"
        d="M1652.8,1565h-448.2c-99.9,0-171.3-60.4-169.7-141.9,1.5-78.8,68.3-136.7,166.5-137,304.4-1.4,608.7-1.4,913.1,0,97.2,0,152.2,53.8,153,137.9,0,87.2-56.3,139.9-158.5,140.9-151.7,1.3-304,.2-456.2.2h0Z"
      />
      <path
        class="st3"
        d="M942.6,2265.8c147.9-18,193-90.9,140.9-226.9,155.8,81.8,270.6,63.6,396.6-62.4s128.2-130.2,194.3-193.3,140.2-64.6,198.8-6.7,57.4,133.2-4.8,198.8c-83.3,85.9-164.7,172.3-252.6,252.1-187.8,170.3-488,185.3-673.2,38.5h0Z"
      />
      <path
        class="st1"
        d="M1110.6,785.6c89.4-101.4,185.1-197,286.7-286.2,218.9,67.9,347.5,246.9,494,402.6,47.8,50.9,28.5,131.2-26.3,177.7-51.8,46.9-131.4,44.5-180.3-5.3-64.4-56.5-125-117.1-181.6-181.3-107.7-127.7-236.4-162.3-392.4-107.4h0Z"
      />
    </svg>
    <p class="social-name">LeetCode</p>
  </a>
</template>

<script setup>
const leetcodeUrl = 'https://leetcode.com/u/IvanZaycev0717/'
</script>

<style scoped>
.leetcode-link {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  color: var(--text-color);
  gap: 4px;
  transition: color 0.2s ease;
}

.leetcode-link:hover {
  color: var(--leetcode-hover);
}

.leetcode-icon {
  width: 1.5em;
  height: 1.5em;
  color: inherit;
}

.social-name {
  margin: 0;
  font-size: clamp(0.5rem, 1.5vw, 0.9rem);
  font-weight: bold;
  line-height: 1;
}

/* CSS Variables for LeetCode colors */
:root {
  --leetcode-dark: #070706;
  --leetcode-gray: #b4b2b1;
  --leetcode-orange: #eaa340;
  --leetcode-orange-light: #eaa240;
  --leetcode-hover: #ffa722;
}

/* Медиа-запросы для адаптивности */
@media (min-width: 480px) {
  .leetcode-link {
    gap: 6px;
  }
  .leetcode-icon {
    width: 1.8em;
    height: 1.8em;
  }
  .social-name {
    font-size: clamp(0.6rem, 1.8vw, 1rem);
  }
}

@media (min-width: 768px) {
  .leetcode-link {
    gap: 8px;
  }
  .leetcode-icon {
    width: 2em;
    height: 2em;
  }
  .social-name {
    font-size: clamp(0.7rem, 2vw, 1.1rem);
  }
}

@media (min-width: 1024px) {
  .leetcode-link {
    gap: 10px;
  }
  .leetcode-icon {
    width: 2.2em;
    height: 2.2em;
  }
  .social-name {
    font-size: clamp(0.8rem, 2.2vw, 1.2rem);
  }
}

.st0 {
  fill: #b4b2b1;
}

.st1 {
  fill: #eaa340;
}

.st2 {
  fill: #070706;
}

.st3 {
  fill: #eaa240;
}
</style>
