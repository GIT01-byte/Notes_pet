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
      <div class="flex items-center space-x-1">
        <div :class="healthStatus.media ? 'bg-green-500' : 'bg-red-500'" class="w-2 h-2 rounded-full"></div>
        <span>Media Service</span>
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
              <i class="fas fa-lock absolute left-4 top-4 text-gray-300"></i>
              <input v-model="forms.register.password" type="password" placeholder="Пароль (минимум 8 символов)" required
                     minlength="8"
                     class="w-full pl-12 pr-4 py-4 rounded-2xl bg-gray-800 text-white border-0 outline-none focus:ring-2 focus:ring-purple-400 transition placeholder-gray-400">
            </div>
            <div class="relative">
              <button type="button" @click="modals.avatarUpload = true" class="w-full flex items-center justify-between p-4 rounded-2xl bg-gray-800 text-white border-0 outline-none hover:ring-2 hover:ring-purple-400 transition">
                <div class="flex items-center space-x-3">
                  <i class="fas fa-image text-gray-300"></i>
                  <span class="text-gray-300">{{ forms.register.avatarFile ? forms.register.avatarFile.name : 'Загрузить аватар (опционально)' }}</span>
                </div>
                <i class="fas fa-upload text-purple-400"></i>
              </button>
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
      <div v-if="currentView === 'dashboard'" class="flex flex-col md:flex-row h-screen pt-8">
        <!-- Mobile Header -->
        <div class="md:hidden bg-gray-900/95 backdrop-blur-sm p-4 flex justify-between items-center border-b border-gray-700">
          <button @click="sidebarOpen = !sidebarOpen" class="text-white p-2">
            <i class="fas fa-bars text-xl"></i>
          </button>
          <h1 class="text-lg font-bold text-white">NotesCloud</h1>
          <div class="flex items-center space-x-2">
            <button @click="modals.createNote = true" class="bg-gradient-to-r from-cyan-400 to-purple-500 text-white px-3 py-1.5 rounded-lg font-medium text-sm">
              <i class="fas fa-plus mr-1"></i>Создать
            </button>
            <button @click="modals.profile = true" class="w-8 h-8 rounded-full flex items-center justify-center overflow-hidden">
              <img v-if="user?.profile?.avatar_url" :src="user.profile.avatar_url" class="w-full h-full object-cover" :alt="user.username">
              <div v-else class="w-full h-full bg-gradient-to-r from-cyan-400 to-purple-500 flex items-center justify-center text-white text-sm font-bold">
                {{ user?.username?.charAt(0)?.toUpperCase() || 'U' }}
              </div>
            </button>
          </div>
        </div>

        <!-- Sidebar -->
        <div :class="[sidebarOpen ? 'translate-x-0' : '-translate-x-full', 'md:translate-x-0', sidebarOpen ? 'w-64 md:w-80' : 'md:w-20', 'fixed md:relative z-40 md:z-auto h-full md:h-auto']" class="glass-dark text-white transition-all duration-300 flex flex-col">
          <!-- Overlay for mobile -->
          <div v-if="sidebarOpen" @click="sidebarOpen = false" class="fixed inset-0 bg-black/50 md:hidden z-[-1]"></div>
          
          <div class="p-4 border-b border-white/20 hidden md:block">
            <button @click="sidebarOpen = !sidebarOpen" class="w-full text-left pl-4">
              <i class="fas fa-bars text-xl"></i>
              <span v-if="sidebarOpen" class="ml-4 font-bold">NotesCloud</span>
            </button>
          </div>

          <nav class="flex-1 p-4 space-y-2">
            <button @click="loadNotes(); sidebarOpen = false" class="w-full flex items-center p-3 rounded-xl hover:bg-white/10 transition">
              <i class="fas fa-home text-xl" :class="!sidebarOpen ? 'mx-auto md:mx-0' : ''"></i>
              <span v-if="sidebarOpen" class="ml-4 block md:block">Главная</span>
            </button>
            <button @click="modals.createNote = true; sidebarOpen = false" class="w-full flex items-center p-3 rounded-xl hover:bg-white/10 transition">
              <i class="fas fa-plus text-xl" :class="!sidebarOpen ? 'mx-auto md:mx-0' : ''"></i>
              <span v-if="sidebarOpen" class="ml-4 block md:block">Создать заметку</span>
            </button>
          </nav>

          <div class="p-4 border-t border-white/20 hidden md:block">
            <button @click="modals.profile = true; sidebarOpen = false" class="w-full flex items-center p-3 rounded-xl hover:bg-white/10 transition">
              <i class="fas fa-user text-xl" :class="!sidebarOpen ? 'mx-auto md:mx-0' : ''"></i>
              <span v-if="sidebarOpen" class="ml-4 block md:block">Профиль</span>
            </button>
          </div>
        </div>

        <!-- Main Content -->
        <div class="flex-1 overflow-auto p-4 md:p-8">
          <div class="max-w-6xl mx-auto">
            <div class="hidden md:flex justify-between items-center mb-8">
              <h1 class="text-4xl font-black text-white">
                <i class="fas fa-sticky-note mr-3"></i>Мои заметки
              </h1>
              <div class="flex items-center space-x-4">
                <button @click="modals.createNote = true" class="bg-gradient-to-r from-cyan-400 to-purple-500 text-white px-6 py-3 rounded-2xl font-bold hover:shadow-lg transition">
                  <i class="fas fa-plus mr-2"></i>Создать заметку
                </button>
                <button @click="modals.profile = true" class="w-12 h-12 rounded-full flex items-center justify-center overflow-hidden hover:shadow-lg transition">
                  <img v-if="user?.profile?.avatar_url" :src="user.profile.avatar_url" class="w-full h-full object-cover" :alt="user.username">
                  <div v-else class="w-full h-full bg-gradient-to-r from-cyan-400 to-purple-500 flex items-center justify-center text-white text-lg font-bold">
                    {{ user?.username?.charAt(0)?.toUpperCase() || 'U' }}
                  </div>
                </button>
              </div>
            </div>

            <!-- Mobile Title -->
            <div class="md:hidden mb-6">
              <h1 class="text-2xl font-black text-white">
                <i class="fas fa-sticky-note mr-2"></i>Мои заметки
              </h1>
            </div>

            <!-- Notes Grid -->
            <div v-if="loading" class="text-center py-12">
              <i class="fas fa-spinner fa-spin text-4xl text-white mb-4"></i>
              <p class="text-white/70">Загрузка заметок...</p>
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
              <transition-group name="fade">
                <div v-for="note in notes" :key="note.id" 
                     @click="viewNote(note.id)"
                     class="glass rounded-2xl md:rounded-3xl p-4 md:p-6 hover:shadow-glow transition-all duration-300 group cursor-pointer">
                  <div class="flex justify-between items-start mb-3 md:mb-4">
                    <h3 class="text-lg md:text-xl font-bold text-white truncate pr-2">{{ note.title }}</h3>
                    <button @click.stop="deleteNote(note.id)" 
                            class="opacity-0 group-hover:opacity-100 bg-red-100 hover:bg-red-500 text-red-500 hover:text-white p-2 rounded-full transition-all flex-shrink-0">
                      <i class="fas fa-trash text-sm"></i>
                    </button>
                  </div>
                  
                  <p class="text-gray-300 mb-3 md:mb-4 line-clamp-3 text-sm md:text-base">{{ note.content }}</p>

                  <!-- Media Summary -->
                  <div v-if="note.image_files?.length || note.video_files?.length || note.audio_files?.length" class="mb-3 md:mb-4 flex flex-wrap gap-1 md:gap-2">
                    <div v-if="note.image_files?.length" class="flex items-center bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-medium">
                      <i class="fas fa-image mr-1"></i>
                      {{ note.image_files.length }} фото
                    </div>
                    <div v-if="note.video_files?.length" class="flex items-center bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs font-medium">
                      <i class="fas fa-video mr-1"></i>
                      {{ note.video_files.length }} видео
                    </div>
                    <div v-if="note.audio_files?.length" class="flex items-center bg-purple-100 text-purple-700 px-2 py-1 rounded-full text-xs font-medium">
                      <i class="fas fa-music mr-1"></i>
                      {{ note.audio_files.length }} аудио
                    </div>
                  </div>

                  <div class="text-xs text-gray-400 border-t border-gray-600 pt-2 md:pt-3">
                    ID: {{ note.id }}
                  </div>
                </div>
              </transition-group>
            </div>

            <div v-if="!loading && notes.length === 0" class="text-center py-12">
              <i class="fas fa-sticky-note text-4xl md:text-6xl text-white/30 mb-4"></i>
              <p class="text-white/70 text-lg md:text-xl mb-4">Заметок пока нет</p>
              <button @click="modals.createNote = true" 
                      class="bg-gradient-to-r from-cyan-400 to-purple-500 text-white px-6 py-3 rounded-2xl font-bold">
                Создать первую заметку
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Modals -->
    <!-- Create Note Modal -->
    <div v-if="modals.createNote" class="fixed inset-0 modal-backdrop flex items-center justify-center p-2 md:p-4 z-50" @click="modals.createNote = false">
      <div @click.stop class="glass rounded-2xl md:rounded-3xl w-full max-w-6xl max-h-[95vh] overflow-auto shadow-2xl">
        <div class="sticky top-0 glass rounded-t-2xl md:rounded-t-3xl p-4 md:p-6 border-b border-gray-200/50 flex justify-between items-center">
          <div class="flex items-center space-x-2 md:space-x-3">
            <div class="w-8 h-8 md:w-10 md:h-10 bg-gradient-to-r from-cyan-400 to-purple-500 rounded-lg md:rounded-xl flex items-center justify-center">
              <i class="fas fa-plus text-white text-sm md:text-lg"></i>
            </div>
            <div>
              <h2 class="text-lg md:text-2xl font-bold text-white">Создать заметку</h2>
              <p class="text-xs md:text-sm text-gray-300">Добавьте текст и медиафайлы</p>
            </div>
          </div>
          <button @click="modals.createNote = false" class="w-8 h-8 md:w-10 md:h-10 rounded-lg md:rounded-xl bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition">
            <i class="fas fa-times text-gray-600 text-sm md:text-base"></i>
          </button>
        </div>
        <form @submit.prevent="createNote" class="p-4 md:p-6 space-y-6 md:space-y-8">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-gray-300">
                <i class="fas fa-heading mr-2 text-cyan-400"></i>Заголовок
              </label>
              <input v-model="forms.note.title" type="text" placeholder="Введите заголовок заметки..." required class="w-full p-3 md:p-4 rounded-xl md:rounded-2xl bg-gray-800 text-white border-2 border-transparent outline-none focus:border-cyan-400 transition font-medium placeholder-gray-400 text-sm md:text-base">
            </div>
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-gray-300">
                <i class="fas fa-align-left mr-2 text-purple-400"></i>Описание
              </label>
              <textarea v-model="forms.note.content" placeholder="Добавьте описание заметки..." required rows="3" class="w-full p-3 md:p-4 rounded-xl md:rounded-2xl bg-gray-800 text-white border-2 border-transparent outline-none focus:border-purple-400 transition font-medium resize-none placeholder-gray-400 text-sm md:text-base"></textarea>
            </div>
          </div>
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
            <div class="space-y-3 md:space-y-4">
              <div class="flex items-center space-x-2">
                <div class="w-6 h-6 md:w-8 md:h-8 bg-blue-100 rounded-md md:rounded-lg flex items-center justify-center">
                  <i class="fas fa-video text-blue-600 text-sm md:text-base"></i>
                </div>
                <div>
                  <h4 class="font-semibold text-white text-sm md:text-base">Видео</h4>
                  <p class="text-xs text-gray-300">MP4, AVI, WebM</p>
                </div>
              </div>
              <div @click="$refs.videoInput.click()" @dragover.prevent @drop="dropFiles($event, 'video_files')" @dragenter="$event.target.classList.add('active')" @dragleave="$event.target.classList.remove('active')" class="drop-zone rounded-xl md:rounded-2xl p-6 md:p-8 text-center cursor-pointer min-h-[100px] md:min-h-[120px] flex flex-col items-center justify-center">
                <i class="fas fa-cloud-upload-alt text-2xl md:text-3xl text-gray-400 mb-2 md:mb-3"></i>
                <p class="text-xs md:text-sm font-medium text-gray-300">Загрузить видео</p>
                <p class="text-xs text-gray-400 mt-1">или перетащите сюда</p>
              </div>
              <input ref="videoInput" @change="addFiles($event, 'video_files')" type="file" multiple accept=".mp4,.avi,.webm" class="hidden">
              <div v-if="files.video_files.length" class="space-y-2 max-h-24 md:max-h-32 overflow-y-auto">
                <div v-for="(file, i) in files.video_files" :key="i" class="file-item flex items-center justify-between p-2 md:p-3 rounded-lg md:rounded-xl">
                  <div class="flex items-center space-x-2 md:space-x-3 flex-1 min-w-0">
                    <i class="fas fa-file-video text-blue-500 flex-shrink-0 text-sm md:text-base"></i>
                    <span class="text-xs md:text-sm font-medium truncate text-white" :title="file.name">{{ file.name }}</span>
                  </div>
                  <button @click="removeFile('video_files', i)" type="button" class="w-5 h-5 md:w-6 md:h-6 rounded-full bg-red-100 hover:bg-red-200 flex items-center justify-center transition flex-shrink-0 ml-2">
                    <i class="fas fa-times text-red-500 text-xs"></i>
                  </button>
                </div>
              </div>
            </div>
            <div class="space-y-3 md:space-y-4">
              <div class="flex items-center space-x-2">
                <div class="w-6 h-6 md:w-8 md:h-8 bg-green-100 rounded-md md:rounded-lg flex items-center justify-center">
                  <i class="fas fa-image text-green-600 text-sm md:text-base"></i>
                </div>
                <div>
                  <h4 class="font-semibold text-white text-sm md:text-base">Изображения</h4>
                  <p class="text-xs text-gray-300">JPEG, PNG, WebP</p>
                </div>
              </div>
              <div @click="$refs.imageInput.click()" @dragover.prevent @drop="dropFiles($event, 'image_files')" @dragenter="$event.target.classList.add('active')" @dragleave="$event.target.classList.remove('active')" class="drop-zone rounded-xl md:rounded-2xl p-6 md:p-8 text-center cursor-pointer min-h-[100px] md:min-h-[120px] flex flex-col items-center justify-center">
                <i class="fas fa-cloud-upload-alt text-2xl md:text-3xl text-gray-400 mb-2 md:mb-3"></i>
                <p class="text-xs md:text-sm font-medium text-gray-300">Загрузить фото</p>
                <p class="text-xs text-gray-400 mt-1">или перетащите сюда</p>
              </div>
              <input ref="imageInput" @change="addFiles($event, 'image_files')" type="file" multiple accept=".jpeg,.jpg,.png,.webp" class="hidden">
              <div v-if="files.image_files.length" class="space-y-2 max-h-24 md:max-h-32 overflow-y-auto">
                <div v-for="(file, i) in files.image_files" :key="i" class="file-item flex items-center justify-between p-2 md:p-3 rounded-lg md:rounded-xl">
                  <div class="flex items-center space-x-2 md:space-x-3 flex-1 min-w-0">
                    <i class="fas fa-file-image text-green-500 flex-shrink-0 text-sm md:text-base"></i>
                    <span class="text-xs md:text-sm font-medium truncate text-white" :title="file.name">{{ file.name }}</span>
                  </div>
                  <button @click="removeFile('image_files', i)" type="button" class="w-5 h-5 md:w-6 md:h-6 rounded-full bg-red-100 hover:bg-red-200 flex items-center justify-center transition flex-shrink-0 ml-2">
                    <i class="fas fa-times text-red-500 text-xs"></i>
                  </button>
                </div>
              </div>
            </div>
            <div class="space-y-3 md:space-y-4">
              <div class="flex items-center space-x-2">
                <div class="w-6 h-6 md:w-8 md:h-8 bg-purple-100 rounded-md md:rounded-lg flex items-center justify-center">
                  <i class="fas fa-music text-purple-600 text-sm md:text-base"></i>
                </div>
                <div>
                  <h4 class="font-semibold text-white text-sm md:text-base">Аудио</h4>
                  <p class="text-xs text-gray-300">MP3, OGG, WAV</p>
                </div>
              </div>
              <div @click="$refs.audioInput.click()" @dragover.prevent @drop="dropFiles($event, 'audio_files')" @dragenter="$event.target.classList.add('active')" @dragleave="$event.target.classList.remove('active')" class="drop-zone rounded-xl md:rounded-2xl p-6 md:p-8 text-center cursor-pointer min-h-[100px] md:min-h-[120px] flex flex-col items-center justify-center">
                <i class="fas fa-cloud-upload-alt text-2xl md:text-3xl text-gray-400 mb-2 md:mb-3"></i>
                <p class="text-xs md:text-sm font-medium text-gray-300">Загрузить аудио</p>
                <p class="text-xs text-gray-400 mt-1">или перетащите сюда</p>
              </div>
              <input ref="audioInput" @change="addFiles($event, 'audio_files')" type="file" multiple accept=".mp3,.ogg,.wav" class="hidden">
              <div v-if="files.audio_files.length" class="space-y-2 max-h-24 md:max-h-32 overflow-y-auto">
                <div v-for="(file, i) in files.audio_files" :key="i" class="file-item flex items-center justify-between p-2 md:p-3 rounded-lg md:rounded-xl">
                  <div class="flex items-center space-x-2 md:space-x-3 flex-1 min-w-0">
                    <i class="fas fa-file-audio text-purple-500 flex-shrink-0 text-sm md:text-base"></i>
                    <span class="text-xs md:text-sm font-medium truncate text-white" :title="file.name">{{ file.name }}</span>
                  </div>
                  <button @click="removeFile('audio_files', i)" type="button" class="w-5 h-5 md:w-6 md:h-6 rounded-full bg-red-100 hover:bg-red-200 flex items-center justify-center transition flex-shrink-0 ml-2">
                    <i class="fas fa-times text-red-500 text-xs"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="sticky bottom-0 glass rounded-b-2xl md:rounded-b-3xl p-4 md:p-6 border-t border-gray-200/50 flex flex-col md:flex-row space-y-3 md:space-y-0 md:space-x-4">
            <button type="button" @click="modals.createNote = false" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 md:py-4 rounded-xl md:rounded-2xl transition text-sm md:text-base">
              <i class="fas fa-times mr-2"></i>Отмена
            </button>
            <button type="submit" :disabled="loading" class="flex-1 bg-gradient-to-r from-cyan-400 to-purple-500 hover:from-cyan-500 hover:to-purple-600 text-white font-bold py-3 md:py-4 rounded-xl md:rounded-2xl transition shadow-lg disabled:opacity-50 text-sm md:text-base">
              <i class="fas fa-spinner fa-spin mr-2" v-if="loading"></i>
              <i class="fas fa-save mr-2" v-else></i>
              {{ loading ? 'Создание...' : 'Создать заметку' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Profile Modal -->
    <div v-if="modals.profile" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" @click="modals.profile = false">
      <div @click.stop class="glass rounded-3xl p-8 w-full max-w-md">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-white">
            <i class="fas fa-user mr-2"></i>Профиль
          </h2>
          <button @click="modals.profile = false" class="text-gray-300 hover:text-white">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>
        <div v-if="user" class="text-center">
          <div class="w-24 h-24 rounded-full mx-auto mb-4 flex items-center justify-center overflow-hidden border-4 border-cyan-400">
            <img v-if="user?.profile?.avatar_url" :src="user.profile.avatar_url" class="w-full h-full object-cover" :alt="user.username">
            <div v-else class="w-full h-full bg-gradient-to-r from-cyan-400 to-purple-500 flex items-center justify-center text-white text-3xl font-bold">
              {{ user.username.charAt(0).toUpperCase() }}
            </div>
          </div>
          <h3 class="text-xl font-bold mb-2 text-white">{{ user.username }}</h3>
          <p class="text-gray-300 mb-4">{{ user.email }}</p>
          <div class="bg-gray-800 rounded-2xl p-4 text-left space-y-2">
            <div class="flex justify-between">
              <span class="text-gray-300">ID:</span>
              <span class="font-mono text-white">{{ user.user_id }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-300">Статус:</span>
              <span :class="user.is_active ? 'text-green-400' : 'text-red-400'">
                {{ user.is_active ? 'Активен' : 'Неактивен' }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-300">Роль:</span>
              <span class="font-bold text-white">{{ user.role }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-300">Заметок:</span>
              <span class="font-bold text-white">{{ notes.length }}</span>
            </div>
          </div>
          <button @click="logout(); modals.profile = false" class="w-full mt-4 bg-red-500 hover:bg-red-600 text-white py-3 rounded-xl font-bold transition">
            <i class="fas fa-sign-out-alt mr-2"></i>Выйти
          </button>
        </div>
      </div>
    </div>

    <!-- Note Detail Modal -->
    <div v-if="modals.showNoteDetail" class="fixed inset-0 modal-backdrop flex items-center justify-center p-2 md:p-4 z-50" @click="modals.showNoteDetail = false" @wheel.stop>
      <div @click.stop class="glass rounded-2xl md:rounded-3xl w-full max-w-6xl max-h-[95vh] overflow-auto shadow-2xl">
        <div class="sticky top-0 glass rounded-t-2xl md:rounded-t-3xl p-4 md:p-6 border-b border-gray-200/50 flex justify-between items-center">
          <div class="flex items-center space-x-2 md:space-x-3 flex-1 min-w-0 pr-2 md:pr-4">
            <div class="w-8 h-8 md:w-10 md:h-10 bg-gradient-to-r from-green-400 to-teal-400 rounded-lg md:rounded-xl flex items-center justify-center">
              <i class="fas fa-eye text-white text-sm md:text-lg"></i>
            </div>
            <div class="min-w-0 flex-1 mr-2 md:mr-4">
              <h2 class="text-lg md:text-2xl font-bold text-white truncate">{{ modals.noteDetail?.title || 'Заметка' }}</h2>
              <p class="text-xs md:text-sm text-gray-300">Просмотр заметки</p>
            </div>
          </div>
          <button @click="modals.showNoteDetail = false" class="w-8 h-8 md:w-10 md:h-10 rounded-lg md:rounded-xl bg-red-500 hover:bg-red-600 flex items-center justify-center transition">
            <i class="fas fa-times text-white text-sm md:text-base"></i>
          </button>
        </div>
        <div v-if="modals.noteDetail" class="p-4 md:p-6 space-y-6 md:space-y-8">
          <div class="space-y-4 md:space-y-6">
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-gray-300">
                <i class="fas fa-heading mr-2 text-cyan-400"></i>Заголовок
              </label>
              <div class="w-full p-3 md:p-4 rounded-xl md:rounded-2xl bg-gray-800 border-2 border-transparent font-medium text-white break-words text-sm md:text-base">
                {{ modals.noteDetail.title || 'Без заголовка' }}
              </div>
            </div>
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-gray-300">
                <i class="fas fa-align-left mr-2 text-purple-400"></i>Описание
              </label>
              <div class="w-full p-3 md:p-4 rounded-xl md:rounded-2xl bg-gray-800 border-2 border-transparent font-medium text-white whitespace-pre-wrap break-words text-sm md:text-base">
                {{ modals.noteDetail.content || 'Нет содержимого' }}
              </div>
            </div>
          </div>
          <div class="space-y-4 md:space-y-6">
            <!-- Медиафайлы -->
            <div v-if="(modals.noteDetail.video_files && modals.noteDetail.video_files.length) || (modals.noteDetail.image_files && modals.noteDetail.image_files.length) || (modals.noteDetail.audio_files && modals.noteDetail.audio_files.length)" class="space-y-3">
              <h3 class="text-lg font-semibold text-white flex items-center">
                <i class="fas fa-photo-video mr-2 text-cyan-400"></i>Медиафайлы
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <button v-if="modals.noteDetail.video_files && modals.noteDetail.video_files.length" @click="openMediaViewer('video', modals.noteDetail.video_files.map(f => f.s3_url), 'Видео')" class="flex items-center justify-between p-4 rounded-xl bg-blue-100/10 hover:bg-blue-100/20 transition border border-blue-500/20">
                  <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <i class="fas fa-video text-blue-600"></i>
                    </div>
                    <div class="text-left">
                      <h4 class="font-semibold text-white">Видео</h4>
                      <p class="text-xs text-gray-300">{{ modals.noteDetail.video_files.length }} файл(ов)</p>
                    </div>
                  </div>
                  <i class="fas fa-chevron-right text-white"></i>
                </button>
                <button v-if="modals.noteDetail.image_files && modals.noteDetail.image_files.length" @click="openMediaViewer('image', modals.noteDetail.image_files.map(f => f.s3_url), 'Изображения')" class="flex items-center justify-between p-4 rounded-xl bg-green-100/10 hover:bg-green-100/20 transition border border-green-500/20">
                  <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <i class="fas fa-image text-green-600"></i>
                    </div>
                    <div class="text-left">
                      <h4 class="font-semibold text-white">Изображения</h4>
                      <p class="text-xs text-gray-300">{{ modals.noteDetail.image_files.length }} файл(ов)</p>
                    </div>
                  </div>
                  <i class="fas fa-chevron-right text-white"></i>
                </button>
                <button v-if="modals.noteDetail.audio_files && modals.noteDetail.audio_files.length" @click="openMediaViewer('audio', modals.noteDetail.audio_files.map(f => f.s3_url), 'Аудио')" class="flex items-center justify-between p-4 rounded-xl bg-purple-100/10 hover:bg-purple-100/20 transition border border-purple-500/20">
                  <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <i class="fas fa-music text-purple-600"></i>
                    </div>
                    <div class="text-left">
                      <h4 class="font-semibold text-white">Аудио</h4>
                      <p class="text-xs text-gray-300">{{ modals.noteDetail.audio_files.length }} файл(ов)</p>
                    </div>
                  </div>
                  <i class="fas fa-chevron-right text-white"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="p-4 md:p-6">
          <p class="text-gray-300 text-sm md:text-base">Загрузка данных...</p>
        </div>
      </div>
    </div>



    <!-- Улучшенный зум с фишками из старого фронтенда -->
    <div v-if="zoom.show" @click="zoom.show = false" class="fixed inset-0 bg-black/95 z-[80] flex items-center justify-center"
         @wheel="handleZoomWheel" @mousedown="startDrag" @mousemove="drag" @mouseup="endDrag" @mouseleave="endDrag">
      <button @click="zoom.show = false" class="absolute top-6 right-6 w-12 h-12 bg-black/70 hover:bg-black/90 text-white rounded-full flex items-center justify-center z-10">
        <i class="fas fa-times text-xl"></i>
      </button>
      <div class="absolute top-6 left-6 bg-black/70 text-white px-4 py-2 rounded-full text-sm z-10">
        {{ Math.round(zoom.scale * 100) }}%
      </div>
      <div class="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex space-x-2 z-10">
        <button @click.stop="zoomOut" class="w-12 h-12 bg-black/70 hover:bg-black/90 text-white rounded-full flex items-center justify-center">
          <i class="fas fa-minus"></i>
        </button>
        <button @click.stop="zoom.scale = 1; zoom.translateX = 0; zoom.translateY = 0" class="w-12 h-12 bg-black/70 hover:bg-black/90 text-white rounded-full flex items-center justify-center">
          <i class="fas fa-home"></i>
        </button>
        <button @click.stop="zoomIn" class="w-12 h-12 bg-black/70 hover:bg-black/90 text-white rounded-full flex items-center justify-center">
          <i class="fas fa-plus"></i>
        </button>
      </div>
      <img :src="zoom.url" 
           :style="{ 
             transform: `scale(${zoom.scale}) translate(${zoom.translateX}px, ${zoom.translateY}px)`,
             cursor: zoom.isDragging ? 'grabbing' : (zoom.scale > 1 ? 'grab' : 'zoom-in')
           }"
           class="max-w-full max-h-full w-auto h-auto object-contain" 
           @click.stop @dragstart.prevent>
    </div>

    <!-- Media Viewer Modal -->
    <div v-if="modals.mediaViewer.show" class="fixed inset-0 bg-black/95 flex flex-col z-[70]" @wheel.stop>
      <div class="flex justify-between items-center p-4 border-b border-gray-700">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-gradient-to-r from-cyan-400 to-purple-500 rounded-lg flex items-center justify-center">
            <i :class="modals.mediaViewer.type === 'video' ? 'fas fa-video' : modals.mediaViewer.type === 'image' ? 'fas fa-image' : 'fas fa-music'" class="text-white"></i>
          </div>
          <div>
            <h2 class="text-xl font-bold text-white">{{ modals.mediaViewer.title }}</h2>
            <p class="text-sm text-gray-300">{{ modals.mediaViewer.files.length }} файл(ов)</p>
          </div>
        </div>
        <button @click="modals.mediaViewer.show = false" class="w-10 h-10 bg-red-500 hover:bg-red-600 rounded-lg flex items-center justify-center transition">
          <i class="fas fa-times text-white"></i>
        </button>
      </div>
      <div class="flex-1 overflow-auto p-4">
        <div v-if="modals.mediaViewer.type === 'video'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div v-for="(url, index) in modals.mediaViewer.files" :key="url" class="space-y-2">
            <video :src="url" controls class="w-full rounded-xl shadow-2xl" @play="pauseOtherMedia($event)"></video>
            <p class="text-white text-center text-sm">Видео {{ index + 1 }}</p>
          </div>
        </div>
        <div v-else-if="modals.mediaViewer.type === 'image'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="(url, index) in modals.mediaViewer.files" :key="url" class="relative group">
            <img :src="url" class="w-full h-64 object-cover rounded-xl hover:opacity-80 transition shadow-lg">
            <button @click="openZoom(url)" class="absolute top-2 right-2 w-8 h-8 bg-black/70 hover:bg-black/90 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
              <i class="fas fa-search-plus text-sm"></i>
            </button>
            <div class="absolute bottom-2 left-2 bg-black/70 text-white px-2 py-1 rounded text-xs">
              Изображение {{ index + 1 }}
            </div>
          </div>
        </div>
        <div v-else-if="modals.mediaViewer.type === 'audio'" class="space-y-4 max-w-2xl mx-auto">
          <div v-for="(url, index) in modals.mediaViewer.files" :key="url" class="bg-gray-800 rounded-xl p-4">
            <h3 class="text-white font-medium mb-2">Аудио {{ index + 1 }}</h3>
            <audio :src="url" controls class="w-full" @play="pauseOtherMedia($event)"></audio>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirm Delete Modal -->
    <div v-if="modals.confirmDelete" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" @click="modals.confirmDelete = false">
      <div @click.stop class="glass rounded-3xl p-8 w-full max-w-md">
        <div class="text-center">
          <div class="w-16 h-16 bg-red-100 rounded-full mx-auto mb-4 flex items-center justify-center">
            <i class="fas fa-exclamation-triangle text-red-500 text-2xl"></i>
          </div>
          <h2 class="text-2xl font-bold text-white mb-2">Удалить заметку?</h2>
          <p class="text-gray-300 mb-6">Это действие нельзя отменить</p>
          <div class="flex space-x-4">
            <button @click="modals.confirmDelete = false" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 rounded-xl transition">
              Отмена
            </button>
            <button @click="confirmDeleteNote" class="flex-1 bg-red-500 hover:bg-red-600 text-white font-bold py-3 rounded-xl transition">
              Удалить
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Avatar Upload Modal -->
    <div v-if="modals.avatarUpload" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" @click="modals.avatarUpload = false">
      <div @click.stop class="glass rounded-3xl p-8 w-full max-w-md">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-white">
            <i class="fas fa-image mr-2"></i>Загрузить аватар
          </h2>
          <button @click="modals.avatarUpload = false" class="text-gray-300 hover:text-white">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>
        
        <div class="space-y-4">
          <!-- Preview -->
          <div v-if="avatarPreview" class="flex justify-center">
            <div class="relative">
              <img :src="avatarPreview" class="w-32 h-32 rounded-full object-cover border-4 border-purple-400">
              <button @click="removeAvatar" class="absolute top-0 right-0 w-8 h-8 bg-red-500 hover:bg-red-600 rounded-full flex items-center justify-center text-white">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>

          <!-- Upload Zone -->
          <div @click="$refs.avatarInput.click()" 
               @dragover.prevent 
               @drop="dropAvatar" 
               class="drop-zone rounded-2xl p-8 text-center cursor-pointer min-h-[150px] flex flex-col items-center justify-center">
            <i class="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-3"></i>
            <p class="text-sm font-medium text-gray-300">Нажмите или перетащите файл</p>
            <p class="text-xs text-gray-400 mt-1">PNG, JPG, WebP (макс 5MB)</p>
          </div>
          <input ref="avatarInput" @change="selectAvatar" type="file" accept="image/*" class="hidden">

          <!-- Actions -->
          <div class="flex space-x-4">
            <button @click="modals.avatarUpload = false" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 rounded-xl transition">
              Отмена
            </button>
            <button @click="confirmAvatar" :disabled="!forms.register.avatarFile" class="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold py-3 rounded-xl transition disabled:opacity-50">
              Подтвердить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'

const API = "http://178.72.155.75:80/api-gateway"

export default {
  name: 'App',
  setup() {
    const currentView = ref('login')
    const user = ref(null)
    const notes = ref([])
    const loading = ref(false)
    const sidebarOpen = ref(false)
    
    // Mobile sidebar auto-close
    const isMobile = () => window.innerWidth < 768
    
    // Auto-close sidebar on mobile after navigation
    const closeMobileSidebar = () => {
      if (isMobile()) {
        sidebarOpen.value = false
      }
    }
    
    // Улучшенный зум с фишками из старого фронтенда
    const zoom = reactive({
      show: false,
      url: '',
      scale: 1,
      translateX: 0,
      translateY: 0,
      isDragging: false,
      dragStartX: 0,
      dragStartY: 0
    })
    
    const modals = reactive({
      profile: false,
      createNote: false,
      lightbox: false,
      lightboxUrl: '',
      showNoteDetail: false,
      noteDetail: null,
      confirmDelete: false,
      deleteNoteId: null,
      avatarUpload: false,
      mediaViewer: {
        show: false,
        type: '',
        files: [],
        title: ''
      }
    })

    const forms = reactive({
      login: { username: '', password: '' },
      register: { username: '', email: '', password: '', profile: '', avatarFile: null, showRegister: false },
      note: { title: '', content: '' }
    })

    const avatarPreview = ref(null)

    const files = reactive({
      video_files: [],
      image_files: [],
      audio_files: []
    })

    const healthStatus = reactive({
      notes: false,
      users: false,
      media: false
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
        setTimeout(() => {
          if (document.body.contains(notification)) {
            document.body.removeChild(notification)
          }
        }, 300)
      }, 3000)
    }

    const checkHealth = async () => {
      try {
        const [notesRes, usersRes, mediaRes] = await Promise.all([
          fetch(`${API}/notes_service/health_check/`),
          fetch(`${API}/users_service/health_check/`),
          fetch(`${API}/media_service/health_check/`)
        ])
        healthStatus.notes = notesRes.ok
        healthStatus.users = usersRes.ok
        healthStatus.media = mediaRes.ok
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
          localStorage.setItem('access_expire', data.access_expire)
          
          setupTokenRefresh()
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
        const formData = new FormData()
        formData.append('username', forms.register.username)
        formData.append('email', forms.register.email)
        formData.append('password', forms.register.password)
        
        if (forms.register.avatarFile) {
          formData.append('avatar_file', forms.register.avatarFile)
        }

        const res = await fetch(`${API}/user/register/`, {
          method: 'POST',
          body: formData
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

    const refreshToken = async () => {
      try {
        const refresh = localStorage.getItem('refresh_token')
        if (!refresh) return false

        const res = await fetch(`${API}/user/refresh_tokens/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refresh })
        })

        if (res.ok) {
          const data = await res.json()
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)
          localStorage.setItem('access_expire', data.access_expire)
          setupTokenRefresh()
          return true
        }
      } catch (error) {
        console.error('Token refresh failed:', error)
      }
      return false
    }

    const setupTokenRefresh = () => {
      const expireTime = localStorage.getItem('access_expire')
      if (!expireTime) return

      const expireTimestamp = parseInt(expireTime) * 1000
      const now = Date.now()
      const timeUntilExpire = expireTimestamp - now
      const refreshTime = Math.max(0, timeUntilExpire - 60000) // 1 минута до истечения или сразу если меньше

      if (timeUntilExpire > 0) {
        setTimeout(async () => {
          const success = await refreshToken()
          if (!success) {
            logout()
          }
        }, refreshTime)
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
          const data = await res.json()
          user.value = {
            user_id: data.user_db.id,
            username: data.user_db.username,
            email: data.user_db.email,
            is_active: data.user_db.is_active,
            role: data.user_db.role,
            profile: {
              avatar_url: data.user_db.avatar?.[0]?.s3_url || null
            },
            jti: data.jwt_payload.jti
          }
        }
      } catch (error) {
        console.error('Failed to get user info:', error)
      }
    }

    const loadNotes = async () => {
      loading.value = true
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          currentView.value = 'login'
          return
        }
        
        const res = await fetch(`${API}/notes/get_all_notes/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (res.ok) {
          const data = await res.json()
          notes.value = data.data || []
        } else if (res.status === 401) {
          localStorage.clear()
          currentView.value = 'login'
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

    const createNote = async () => {
      loading.value = true
      try {
        const url = new URL(`${API}/notes/create`)
        url.searchParams.append("title", forms.note.title)
        url.searchParams.append("content", forms.note.content)

        const formData = new FormData()
        files.video_files.forEach(f => formData.append('video_files', f))
        files.image_files.forEach(f => formData.append('image_files', f))
        files.audio_files.forEach(f => formData.append('audio_files', f))

        const token = localStorage.getItem('access_token')
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        })

        if (res.ok) {
          forms.note.title = ''
          forms.note.content = ''
          files.video_files = []
          files.image_files = []
          files.audio_files = []
          modals.createNote = false
          await loadNotes()
          showNotification('Заметка создана', 'success')
        } else {
          showNotification('Ошибка создания', 'error')
        }
      } catch (error) {
        showNotification('Ошибка сети', 'error')
      } finally {
        loading.value = false
      }
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

    const addFiles = (event, type) => {
      const selectedFiles = Array.from(event.target.files)
      const validFiles = selectedFiles.filter(file => {
        if (type === 'video_files') return file.type.startsWith('video/')
        if (type === 'image_files') return file.type.startsWith('image/')
        if (type === 'audio_files') return file.type.startsWith('audio/')
        return false
      })
      files[type].push(...validFiles)
      event.target.value = ''
    }

    const dropFiles = (event, type) => {
      event.preventDefault()
      const droppedFiles = Array.from(event.dataTransfer.files)
      const validFiles = droppedFiles.filter(file => {
        if (type === 'video_files') return file.type.startsWith('video/')
        if (type === 'image_files') return file.type.startsWith('image/')
        if (type === 'audio_files') return file.type.startsWith('audio/')
        return false
      })
      files[type].push(...validFiles)
      event.target.classList.remove('active')
    }

    const removeFile = (type, index) => {
      files[type].splice(index, 1)
    }

    const openLightbox = (url) => {
      modals.lightboxUrl = url
      modals.lightbox = true
    }

    const openMediaViewer = (type, files, title) => {
      modals.mediaViewer.type = type
      modals.mediaViewer.files = files
      modals.mediaViewer.title = title
      modals.mediaViewer.show = true
    }

    const openZoom = (url) => {
      zoom.show = true
      zoom.url = url
      zoom.scale = 1
      zoom.translateX = 0
      zoom.translateY = 0
    }

    const zoomIn = () => {
      zoom.scale = Math.min(3, zoom.scale + 0.3)
    }

    const zoomOut = () => {
      zoom.scale = Math.max(0.5, zoom.scale - 0.3)
    }

    const handleZoomWheel = (event) => {
      event.preventDefault()
      const delta = event.deltaY > 0 ? -0.1 : 0.1
      zoom.scale = Math.max(0.5, Math.min(3, zoom.scale + delta))
    }

    const startDrag = (event) => {
      if (zoom.scale > 1) {
        zoom.isDragging = true
        zoom.dragStartX = event.clientX - zoom.translateX
        zoom.dragStartY = event.clientY - zoom.translateY
      }
    }

    const drag = (event) => {
      if (zoom.isDragging && zoom.scale > 1) {
        zoom.translateX = event.clientX - zoom.dragStartX
        zoom.translateY = event.clientY - zoom.dragStartY
      }
    }

    const endDrag = () => {
      zoom.isDragging = false
    }

    const pauseOtherMedia = (event) => {
      const audios = document.querySelectorAll('audio')
      const videos = document.querySelectorAll('video')
      audios.forEach(audio => {
        if (audio !== event.target) {
          audio.pause()
        }
      })
      videos.forEach(video => {
        if (video !== event.target) {
          video.pause()
        }
      })
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

    const testTokenRefresh = async () => {
      const success = await refreshToken()
      showNotification(success ? 'Токен обновлен' : 'Ошибка обновления токена', success ? 'success' : 'error')
    }

    const selectAvatar = (event) => {
      const file = event.target.files[0]
      if (file && file.size <= 5 * 1024 * 1024) {
        forms.register.avatarFile = file
        avatarPreview.value = URL.createObjectURL(file)
      } else {
        showNotification('Файл слишком большой (макс 5MB)', 'error')
      }
    }

    const dropAvatar = (event) => {
      event.preventDefault()
      const file = event.dataTransfer.files[0]
      if (file && file.type.startsWith('image/') && file.size <= 5 * 1024 * 1024) {
        forms.register.avatarFile = file
        avatarPreview.value = URL.createObjectURL(file)
      } else {
        showNotification('Неверный формат или размер файла', 'error')
      }
    }

    const removeAvatar = () => {
      forms.register.avatarFile = null
      avatarPreview.value = null
    }

    const confirmAvatar = () => {
      modals.avatarUpload = false
    }

    onMounted(async () => {
      await checkHealth()
      
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          setupTokenRefresh()
          await getUserInfo()
          if (user.value) {
            currentView.value = 'dashboard'
            await loadNotes()
          }
        } catch (error) {
          console.error('Failed to initialize user:', error)
          localStorage.clear()
        }
      }
    })

    const isHealthy = computed(() => healthStatus.notes && healthStatus.users && healthStatus.media)

    return {
      currentView, user, notes, loading, sidebarOpen, modals, forms, files, healthStatus, isHealthy, zoom, avatarPreview,
      login, register, logout, loadNotes, deleteNote, confirmDeleteNote, viewNote, createNote,
      addFiles, dropFiles, removeFile, openLightbox, openMediaViewer, closeMobileSidebar, 
      openZoom, zoomIn, zoomOut, handleZoomWheel, startDrag, drag, endDrag, pauseOtherMedia, testTokenRefresh,
      selectAvatar, dropAvatar, removeAvatar, confirmAvatar
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

.drop-zone {
  border: 2px dashed rgba(156, 163, 175, 0.5);
  background: rgba(31, 41, 55, 0.5);
  transition: all 0.3s ease;
}

.drop-zone:hover,
.drop-zone.active {
  border-color: rgba(34, 197, 94, 0.8);
  background: rgba(34, 197, 94, 0.1);
}

.file-item {
  background: rgba(31, 41, 55, 0.8);
  border: 1px solid rgba(75, 85, 99, 0.5);
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