<template>
  <div class="note-item">
    <h3>{{ note.title }}</h3>
    <p>{{ note.content }}</p>
  </div>
</template>

<script>
export default {
  props: {
    note: {
      type: Object,
      required: true,
    },
  },
};
</script>
