<template>
  <div class="min-h-screen">
    <!-- Health Status Bar -->
    <div class="fixed top-0 left-0 right-0 z-50 bg-black/80 text-white text-xs p-2 flex justify-center space-x-4">
      <div class="flex items-center space-x-1">
        <div :class="healthStatus.notes ? 'bg-green-500' : 'bg-red-500'" class="w-2 h-2 rounded-full"></div>
        <span>Notes Service</span>
      </div>
      <div class="flex items-center space-x-1">
        <div :class="healthStatus.users ? 'bg-green-500' : 'bg-red-500'" class="w-2 h-2 rounded-full"></div>
        <span>Users Service</span>
      </div>
    </div>

    <!-- Login/Register View -->
    <transition name="fade">
      <div v-if="currentView === 'login'" class="fixed inset-0 flex items-center justify-center p-4 pt-12">
        <div class="glass rounded-3xl p-8 w-full max-w-md shadow-glow bounce">
          <div class="text-center mb-8">
            <h1 class="text-4xl font-black gradient-text mb-2">
              <i class="fas fa-sticky-note mr-2"></i>NotesCloud
            </h1>
            <p class="text-gray-300">Ваши заметки в облаке</p>
          </div>

          <div class="flex mb-6 bg-gray-800 rounded-2xl p-1">
            <button @click="forms.showRegister = false" 
                    :class="!forms.showRegister ? 'bg-gray-700 shadow-md text-white' : 'text-gray-300'"
                    class="flex-1 py-3 px-4 rounded-xl font-semibold text-sm transition">
              <i class="fas fa-sign-in-alt mr-2"></i>Вход
            </button>
            <button @click="forms.showRegister = true" 
                    :class="forms.showRegister ? 'bg-gray-700 shadow-md text-white' : 'text-gray-300'"
                    class="flex-1 py-3 px-4 rounded-xl font-semibold text-sm transition">
              <i class="fas fa-user-plus mr-2"></i>Регистрация
            </button>
          </div>

          <!-- Login Form -->
          <form v-if="!forms.showRegister" @submit.prevent="login" class="space-y-4">
            <div class="relative">
              <i class="fas fa-user absolute left-4 top-4 text-gray-300"></i>
              <input v-model="forms.login.username" type="text" placeholder="Имя пользователя" required
                     class="w-full pl-12 pr-4 py-4 rounded-2xl bg-gray-800 text-white border-0 outline-none focus:ring-2 focus:ring-cyan-400 transition placeholder-gray-400">
            </div>
            <div class="relative">
              <i class="fas fa-lock absolute left-4 top-4 text-gray-300"></i>
              <input v-model="forms.login.password" type="password" placeholder="Пароль" required
                     class="w-full pl-12 pr-4 py-4 rounded-2xl bg-gray-800 text-white border-0 outline-none focus:ring-2 focus:ring-cyan-400 transition placeholder-gray-400">
            </div>
            <button type="submit" :disabled="loading || !isHealthy"
                    class="w-full bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-bold py-4 rounded-2xl transition hover:shadow-lg disabled:opacity-50">
              <i class="fas fa-spinner fa-spin mr-2" v-if="loading"></i>
              {{ loading ? 'Вход...' : 'Войти' }}
            </button>
          </form>

          <!-- Register Form -->
          <form v-else @submit.prevent="register" class="space-y-4">
            <div class="relative">
              <i class="fas fa-user absolute left-4 top-4 text-gray-300"></i>
              <input v-model="forms.register.username" type="text" placeholder="Имя пользователя (3-64 символа)" required
                     minlength="3" maxlength="64"
                     class="w-full pl-12 pr-4 py-4 rounded-2xl bg-gray-800 text-white border-0 outline-none focus:ring-2 focus:ring-purple-400 transition placeholder-gray-400">
            </div>
            <div class="relative">
              <i class="fas fa-envelope absolute left-4 top-4 text-gray-300"></i>
              <input v-model="forms.register.email" type="email" placeholder="Email" required
                     class="w-full pl-12 pr-4 py-4 rounded-2xl bg-gray-800 text-white border-0 outline-none focus:ring-2 focus:ring-purple-400 transition placeholder-gray-400">
            </div>
            <div class="relative">
              <i class="fas fa-image absolute left-4 top-4 text-gray-300"></i>
              <input v-model="forms.register.profile" type="url" placeholder="Ссылка на фото профиля (опционально)"
                     class="w-full pl-12 pr-4 py-4 rounded-2xl bg-gray-800 text-white border-0 outline-none focus:ring-2 focus:ring-purple-400 transition placeholder-gray-400">
            </div>
            <div class="relative">
              <i class="fas fa-lock absolute left-4 top-4 text-gray-300"></i>
              <input v-model="forms.register.password" type="password" placeholder="Пароль (минимум 8 символов)" required
                     minlength="8"
                     class="w-full pl-12 pr-4 py-4 rounded-2xl bg-gray-800 text-white border-0 outline-none focus:ring-2 focus:ring-purple-400 transition placeholder-gray-400">
            </div>
            <button type="submit" :disabled="loading || !isHealthy"
                    class="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold py-4 rounded-2xl transition hover:shadow-lg disabled:opacity-50">
              <i class="fas fa-spinner fa-spin mr-2" v-if="loading"></i>
              {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
            </button>
          </form>

          <div v-if="!isHealthy" class="mt-4 p-3 bg-red-100 text-red-700 rounded-xl text-sm text-center">
            <i class="fas fa-exclamation-triangle mr-2"></i>
            Сервисы недоступны. Проверьте подключение.
          </div>
        </div>
      </div>
    </transition>

    <!-- Dashboard View -->
    <transition name="slide">
      <div v-if="currentView === 'dashboard'" class="flex h-screen pt-8">
        <!-- Sidebar -->
        <div :class="sidebarOpen ? 'w-80' : 'w-20'" class="glass-dark text-white transition-all duration-300 flex flex-col">
          <div class="p-4 border-b border-white/20">
            <button @click="sidebarOpen = !sidebarOpen" class="w-full text-left pl-4">
              <i class="fas fa-bars text-xl"></i>
              <span v-if="sidebarOpen" class="ml-4 font-bold">NotesCloud</span>
            </button>
          </div>

          <nav class="flex-1 p-4 space-y-2">
            <button @click="loadNotes" class="w-full flex items-center p-3 rounded-xl hover:bg-white/10 transition">
              <i class="fas fa-home text-xl" :class="!sidebarOpen ? 'mx-auto' : ''"></i>
              <span v-if="sidebarOpen" class="ml-4">Главная</span>
            </button>
            <button @click="modals.createNote = true" class="w-full flex items-center p-3 rounded-xl hover:bg-white/10 transition">
              <i class="fas fa-plus text-xl" :class="!sidebarOpen ? 'mx-auto' : ''"></i>
              <span v-if="sidebarOpen" class="ml-4">Создать заметку</span>
            </button>
            <button @click="modals.profile = true" class="w-full flex items-center p-3 rounded-xl hover:bg-white/10 transition">
              <i class="fas fa-user text-xl" :class="!sidebarOpen ? 'mx-auto' : ''"></i>
              <span v-if="sidebarOpen" class="ml-4">Профиль</span>
            </button>
          </nav>

          <div class="p-4 border-t border-white/20">
            <button @click="logout" class="w-full flex items-center p-3 rounded-xl hover:bg-red-500/20 transition text-red-300">
              <i class="fas fa-sign-out-alt text-xl" :class="!sidebarOpen ? 'mx-auto' : ''"></i>
              <span v-if="sidebarOpen" class="ml-4">Выйти</span>
            </button>
          </div>
        </div>

        <!-- Main Content -->
        <div class="flex-1 overflow-auto p-8">
          <div class="max-w-6xl mx-auto">
            <div class="flex justify-between items-center mb-8">
              <h1 class="text-4xl font-black text-white">
                <i class="fas fa-sticky-note mr-3"></i>Мои заметки
              </h1>
              <div class="bg-gradient-to-r from-cyan-400 to-purple-500 text-white px-6 py-3 rounded-2xl font-bold">
                {{ user?.username || 'Пользователь' }}
              </div>
            </div>

            <!-- Notes Grid -->
            <div v-if="loading" class="text-center py-12">
              <i class="fas fa-spinner fa-spin text-4xl text-white mb-4"></i>
              <p class="text-white/70">Загрузка заметок...</p>
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <transition-group name="fade">
                <div v-for="note in notes" :key="note.id" 
                     @click="viewNote(note.id)"
                     class="glass rounded-3xl p-6 hover:shadow-glow transition-all duration-300 group cursor-pointer">
                  <div class="flex justify-between items-start mb-4">
                    <h3 class="text-xl font-bold text-white truncate">{{ note.title }}</h3>
                    <button @click.stop="deleteNote(note.id)" 
                            class="opacity-0 group-hover:opacity-100 bg-red-100 hover:bg-red-500 text-red-500 hover:text-white p-2 rounded-full transition-all">
                      <i class="fas fa-trash text-sm"></i>
                    </button>
                  </div>
                  
                  <p class="text-gray-300 mb-4 line-clamp-3">{{ note.content }}</p>

                  <div class="text-xs text-gray-400 border-t border-gray-600 pt-3">
                    ID: {{ note.id }}
                  </div>
                </div>
              </transition-group>
            </div>

            <div v-if="!loading && notes.length === 0" class="text-center py-12">
              <i class="fas fa-sticky-note text-6xl text-white/30 mb-4"></i>
              <p class="text-white/70 text-xl">Заметок пока нет</p>
              <button @click="modals.createNote = true" 
                      class="mt-4 bg-gradient-to-r from-cyan-400 to-purple-500 text-white px-6 py-3 rounded-2xl font-bold">
                Создать первую заметку
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'

const API = "http://127.0.0.1:8080"

export default {
  name: 'App',
  setup() {
    const currentView = ref('login')
    const user = ref(null)
    const notes = ref([])
    const loading = ref(false)
    const sidebarOpen = ref(false)
    
    const modals = reactive({
      profile: false,
      createNote: false,
      showNoteDetail: false,
      noteDetail: null,
      confirmDelete: false,
      deleteNoteId: null
    })

    const forms = reactive({
      login: { username: '', password: '' },
      register: { username: '', email: '', password: '', profile: '', showRegister: false },
      note: { title: '', content: '' }
    })

    const files = reactive({
      video_files: [],
      image_files: [],
      audio_files: []
    })

    const healthStatus = reactive({
      notes: false,
      users: false
    })

    const showNotification = (message, type = 'info') => {
      const notification = document.createElement('div')
      notification.className = `fixed top-4 right-4 z-[100] p-4 rounded-lg shadow-lg max-w-sm transition-all duration-300 transform translate-x-full`
      
      const colors = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        warning: 'bg-yellow-500 text-black',
        info: 'bg-blue-500 text-white'
      }
      
      notification.className += ` ${colors[type]}`
      notification.innerHTML = `
        <div class="flex items-center space-x-2">
          <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : type === 'warning' ? 'exclamation-circle' : 'info-circle'}"></i>
          <span>${message}</span>
        </div>
      `
      
      document.body.appendChild(notification)
      
      setTimeout(() => {
        notification.style.transform = 'translateX(0)'
      }, 100)
      
      setTimeout(() => {
        notification.style.transform = 'translateX(100%)'
        setTimeout(() => document.body.removeChild(notification), 300)
      }, 3000)
    }

    const checkHealth = async () => {
      try {
        const [notesRes, usersRes] = await Promise.all([
          fetch(`${API}/notes_service/health_check/`),
          fetch(`${API}/users_service/health_check/`)
        ])
        healthStatus.notes = notesRes.ok
        healthStatus.users = usersRes.ok
      } catch (error) {
        console.error('Health check failed:', error)
      }
    }

    const login = async () => {
      loading.value = true
      try {
        const formData = new FormData()
        formData.append("grant_type", "password")
        formData.append("username", forms.login.username)
        formData.append("password", forms.login.password)

        const res = await fetch(`${API}/user/login/`, {
          method: 'POST',
          body: formData
        })

        if (res.ok) {
          const data = await res.json()
          localStorage.clear()
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)
          
          await getUserInfo()
          currentView.value = 'dashboard'
          await loadNotes()
        } else {
          showNotification('Ошибка входа', 'error')
        }
      } catch (error) {
        showNotification('Ошибка сети', 'error')
      } finally {
        loading.value = false
      }
    }

    const register = async () => {
      loading.value = true
      try {
        const payload = {
          username: forms.register.username,
          email: forms.register.email,
          password: forms.register.password
        }
        
        if (forms.register.profile) {
          payload.profile = { avatar_url: forms.register.profile }
        }

        const res = await fetch(`${API}/user/register/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })

        if (res.ok) {
          showNotification('Регистрация успешна!', 'success')
          forms.login.username = forms.register.username
          forms.login.password = forms.register.password
          await login()
        } else {
          const error = await res.json()
          showNotification(error.detail || 'Ошибка регистрации', 'error')
        }
      } catch (error) {
        showNotification('Ошибка сети', 'error')
      } finally {
        loading.value = false
      }
    }

    const logout = async () => {
      try {
        const token = localStorage.getItem('access_token')
        await fetch(`${API}/user/logout/`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        localStorage.clear()
        user.value = null
        notes.value = []
        currentView.value = 'login'
        showNotification('Вы успешно вышли из системы', 'success')
      } catch (error) {
        console.error('Logout error:', error)
        localStorage.clear()
        user.value = null
        notes.value = []
        currentView.value = 'login'
      }
    }

    const getUserInfo = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const res = await fetch(`${API}/user/self_info/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (res.ok) {
          user.value = await res.json()
        }
      } catch (error) {
        console.error('Failed to get user info:', error)
      }
    }

    const loadNotes = async () => {
      loading.value = true
      try {
        const token = localStorage.getItem('access_token')
        const res = await fetch(`${API}/notes/get_all_notes`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (res.ok) {
          const data = await res.json()
          notes.value = data.data || []
        }
      } catch (error) {
        console.error('Failed to load notes:', error)
      } finally {
        loading.value = false
      }
    }

    const deleteNote = (id) => {
      modals.deleteNoteId = id
      modals.confirmDelete = true
    }

    const confirmDeleteNote = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const res = await fetch(`${API}/notes/delete/${modals.deleteNoteId}/`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (res.ok) {
          await loadNotes()
          showNotification('Заметка удалена', 'success')
        } else {
          showNotification('Ошибка удаления', 'error')
        }
      } catch (error) {
        showNotification('Ошибка сети', 'error')
      } finally {
        modals.confirmDelete = false
        modals.deleteNoteId = null
      }
    }

    const viewNote = async (id) => {
      try {
        const token = localStorage.getItem('access_token')
        const res = await fetch(`${API}/notes/get_note/${id}/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (res.ok) {
          const data = await res.json()
          modals.noteDetail = data.data || data
          modals.showNoteDetail = true
        } else {
          console.error('Failed to fetch note details')
        }
      } catch (error) {
        console.error('Failed to load note:', error)
      }
    }

    onMounted(async () => {
      await checkHealth()
      
      const token = localStorage.getItem('access_token')
      if (token) {
        await getUserInfo()
        if (user.value) {
          currentView.value = 'dashboard'
          await loadNotes()
        }
      }
    })

    const isHealthy = computed(() => healthStatus.notes && healthStatus.users)

    return {
      currentView, user, notes, loading, sidebarOpen, modals, forms, files, healthStatus, isHealthy,
      login, register, logout, loadNotes, deleteNote, confirmDeleteNote, viewNote
    }
  }
}
</script>

<style>
body { 
  background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.glass { 
  backdrop-filter: blur(20px); 
  background: rgba(15, 15, 35, 0.85); 
  border: 1px solid rgba(0, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 255, 255, 0.1);
}

.glass-dark { 
  backdrop-filter: blur(20px); 
  background: rgba(15, 15, 35, 0.95); 
  border: 1px solid rgba(0, 255, 255, 0.15);
}

.modal-backdrop {
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(8px);
}

.gradient-text { 
  background: linear-gradient(135deg, #00ffff, #ff00ff); 
  -webkit-background-clip: text; 
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.shadow-glow { 
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.3); 
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bounce {
  animation: bounce 0.5s ease-in-out;
}

@keyframes bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.fade-enter-active, .fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from, .slide-leave-to {
  transform: translateX(-100%);
}
</style>