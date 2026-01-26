<template>
  <div class="file-item">
    {{ file.name }}
  </div>
</template>

<script>
export default {
  props: {
    file: {
      type: Object,
      required: true,
    },
  },
};
</script>
