<template>
  <div class="notes-container">
    <h1>My Notes</h1>

    <div class="note-form">
      <input type="text" v-model="newNoteTitle" placeholder="Note Title" />
      <textarea v-model="newNoteContent" placeholder="Note Content"></textarea>
      <input type = "file" @change = "handleVideoUpload" accept = "video/*" multiple/>
      Видео:
      <div v-for = "(video, index) in newNoteVideoUrls" :key = "index">
        {{video}}
      </div>
      <input type = "file"  @change = "handleImageUpload" accept="image/*" multiple>
      Картинки:
      <div v-for = "(image, index) in newNoteImageUrls" :key = "index">
        {{image}}
      </div>
      <input type = "file" @change = "handleAudioUpload" accept = "audio/*" multiple/>
      Аудио:
      <div v-for = "(audio, index) in newNoteAudioUrls" :key = "index">
        {{audio}}
      </div>

      <button @click="createNote">Create Note</button>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>

    <div class="note-list" v-if="notes">
      <div class="note-item" v-for="note in notes" :key="note.id">
        <h3>{{ note.title }}</h3>
        <p>{{ note.content }}</p>
        <button @click="deleteNote(note.id)">Delete</button>
      </div>
    </div>
    <div v-else>
      <p>Загрузка...</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import useAuth from '@/composables/useAuth';

export default {
  setup() {
    const { error, createNote, deleteNote, getNotes } = useAuth();
    const notes = ref(null);
    const newNoteTitle = ref('');
    const newNoteContent = ref('');
    const newNoteVideoUrls = ref([])
    const newNoteImageUrls = ref([])
    const newNoteAudioUrls = ref([])

    const handleVideoUpload = function (event) {
      newNoteVideoUrls.value = Array.from(event.target.files).map(f => URL.createObjectURL(f))
    }

    const handleImageUpload = function (event) {
      newNoteImageUrls.value = Array.from(event.target.files).map(f => URL.createObjectURL(f))
    }

    const handleAudioUpload = function (event) {
      newNoteAudioUrls.value = Array.from(event.target.files).map(f => URL.createObjectURL(f))
    }

    const loadNotes = async () => {
      notes.value = await getNotes();
    };


    const createNoteHandler = async () => {
      if (newNoteTitle.value && newNoteContent.value) {
        const result = await createNote(
          newNoteTitle.value,
          newNoteContent.value,
          newNoteVideoUrls.value,
          newNoteImageUrls.value,
          newNoteAudioUrls.value
        );

        if (result) {
          newNoteTitle.value = '';
          newNoteContent.value = '';
          newNoteVideoUrls.value = [];
          newNoteImageUrls.value = [];
          newNoteAudioUrls.value = [];
          await loadNotes();
        }
      } else {
        error.value = 'Пожалуйста, введите заголовок и контент заметки.';
      }
    };

    const deleteNoteHandler = async (noteId) => {
      const result = await deleteNote(noteId);
      if (result) {
        await loadNotes(); // Refresh notes after deletion
      }
    };

    onMounted(loadNotes);

    return {
      notes,
      newNoteTitle,
      newNoteContent,
      newNoteVideoUrls,
      newNoteImageUrls,
      newNoteAudioUrls,
      handleVideoUpload,
      handleImageUpload,
      handleAudioUpload,
      error,
      createNote: createNoteHandler,
      deleteNote: deleteNoteHandler,
    };
  },
};
</script>

<style scoped>
.notes-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.note-form {
  margin-bottom: 20px;
}

.note-form input[type="text"],
.note-form textarea {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.note-form button {
  background-color: #28a745;
  color: white;
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.note-form button:hover {
  background-color: #218838;
}
.note-list {
  margin-top: 20px;
}

.note-item {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 10px;
}

.error-message {
  color: #dc3545;
  margin-top: 10px;
}
</style>
