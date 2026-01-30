const { createApp, ref, reactive, onMounted, computed, watch } = Vue;

const API = "http://127.0.0.1:80";

createApp({
    setup() {
        // State
        const currentView = ref('login');
        const user = ref(null);
        const notes = ref([]);
        const loading = ref(false);
        const sidebarOpen = ref(false);
        
        // Image zoom state
        const imageZoomLevel = ref(1);
        const imageTranslateX = ref(0);
        const imageTranslateY = ref(0);
        const isDragging = ref(false);
        const dragStartX = ref(0);
        const dragStartY = ref(0);
        
        // Modals
        const modals = reactive({
            profile: false,
            createNote: false,
            lightbox: false,
            lightboxUrl: '',
            showNoteDetail: false,
            noteDetail: null,
            imageZoom: false,
            zoomedImageUrl: '',
            confirmDelete: false,
            deleteNoteId: null
        });

        // Forms
        const forms = reactive({
            login: { username: '', password: '' },
            register: { username: '', email: '', password: '', profile: '' },
            note: { title: '', content: '' }
        });

        // Files
        const files = reactive({
            video_files: [],
            image_files: [],
            audio_files: []
        });

        // Health checks
        const healthStatus = reactive({
            notes: false,
            users: false
        });

        // Auto token refresh
        let refreshTimer = null;

        // Notification system
        const showNotification = (message, type = 'info') => {
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 z-[100] p-4 rounded-lg shadow-lg max-w-sm transition-all duration-300 transform translate-x-full`;
            
            const colors = {
                success: 'bg-green-500 text-white',
                error: 'bg-red-500 text-white',
                warning: 'bg-yellow-500 text-black',
                info: 'bg-blue-500 text-white'
            };
            
            notification.className += ` ${colors[type]}`;
            notification.innerHTML = `
                <div class="flex items-center space-x-2">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : type === 'warning' ? 'exclamation-circle' : 'info-circle'}"></i>
                    <span>${message}</span>
                </div>
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.transform = 'translateX(0)';
            }, 100);
            
            setTimeout(() => {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => document.body.removeChild(notification), 300);
            }, 3000);
        };

        // Methods
        const checkHealth = async () => {
            try {
                const [notesRes, usersRes] = await Promise.all([
                    fetch(`${API}/notes_service/health_check/`),
                    fetch(`${API}/users_service/health_check/`)
                ]);
                healthStatus.notes = notesRes.ok;
                healthStatus.users = usersRes.ok;
            } catch (error) {
                console.error('Health check failed:', error);
            }
        };

        const login = async () => {
            loading.value = true;
            try {
                const formData = new FormData();
                formData.append("grant_type", "password");
                formData.append("username", forms.login.username);
                formData.append("password", forms.login.password);

                const res = await fetch(`${API}/user/login/`, {
                    method: 'POST',
                    body: formData
                });

                if (res.ok) {
                    const data = await res.json();
                    localStorage.clear();
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('refresh_token', data.refresh_token);
                    
                    await getUserInfo();
                    currentView.value = 'dashboard';
                    startTokenRefresh();
                    await loadNotes();
                } else {
                    alert('Ошибка входа');
                }
            } catch (error) {
                alert('Ошибка сети');
            } finally {
                loading.value = false;
            }
        };

        const register = async () => {
            loading.value = true;
            try {
                const payload = {
                    username: forms.register.username,
                    email: forms.register.email,
                    password: forms.register.password
                };
                
                if (forms.register.profile) {
                    payload.profile = { avatar_url: forms.register.profile };
                }

                const res = await fetch(`${API}/user/register/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (res.ok) {
                    alert('Регистрация успешна!');
                    forms.login.username = forms.register.username;
                    forms.login.password = forms.register.password;
                    await login();
                } else {
                    const error = await res.json();
                    alert(error.detail || 'Ошибка регистрации');
                }
            } catch (error) {
                alert('Ошибка сети');
            } finally {
                loading.value = false;
            }
        };

        const apiCall = async (url, options = {}) => {
            const token = localStorage.getItem('access_token');
            return fetch(url, {
                headers: { 'Authorization': `Bearer ${token}`, ...options.headers },
                ...options
            });
        };

        const handleError = (error, message) => {
            console.error(error);
            alert(message);
        };

        const resetForm = () => {
            forms.note.title = forms.note.content = '';
            files.video_urls = files.image_urls = files.audio_urls = [];
        };

        const logout = async () => {
            try {
                const token = localStorage.getItem('access_token');
                const res = await fetch(`${API}/user/logout/`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (res.ok) {
                    localStorage.clear();
                    user.value = null;
                    notes.value = [];
                    currentView.value = 'login';
                    if (refreshTimer) clearInterval(refreshTimer);
                    showNotification('Вы успешно вышли из системы', 'success');
                } else {
                    showNotification('Ошибка при выходе из системы', 'error');
                    // Force logout anyway
                    localStorage.clear();
                    user.value = null;
                    notes.value = [];
                    currentView.value = 'login';
                    if (refreshTimer) clearInterval(refreshTimer);
                }
            } catch (error) {
                console.error('Logout error:', error);
                showNotification('Ошибка сети при выходе', 'error');
                // Force logout anyway
                localStorage.clear();
                user.value = null;
                notes.value = [];
                currentView.value = 'login';
                if (refreshTimer) clearInterval(refreshTimer);
            }
        };

        const refreshTokens = async () => {
            try {
                const refreshToken = localStorage.getItem('refresh_token');
                const res = await fetch(`${API}/user/refresh_tokens/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: refreshToken })
                });

                if (res.ok) {
                    const data = await res.json();
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('refresh_token', data.refresh_token);
                } else {
                    logout();
                }
            } catch (error) {
                console.error('Token refresh failed:', error);
                logout();
            }
        };

        const startTokenRefresh = () => {
            refreshTimer = setInterval(refreshTokens, 10 * 60 * 1000);
        };

        const loadNotes = async () => {
            loading.value = true;
            try {
                const token = localStorage.getItem('access_token');
                const res = await fetch(`${API}/notes/get_all_notes`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (res.ok) {
                    const data = await res.json();
                    notes.value = data.data || [];
                }
            } catch (error) {
                console.error('Failed to load notes:', error);
            } finally {
                loading.value = false;
            }
        };

        const createNote = async () => {
            loading.value = true;
            try {
                const url = new URL(`${API}/notes/create`);
                url.searchParams.append("title", forms.note.title);
                url.searchParams.append("content", forms.note.content);

                const formData = new FormData();
                files.video_files.forEach(f => formData.append('video_files', f));
                files.image_files.forEach(f => formData.append('image_files', f));
                files.audio_files.forEach(f => formData.append('audio_files', f));

                const token = localStorage.getItem('access_token');
                const res = await fetch(url, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });

                if (res.ok) {
                    forms.note.title = forms.note.content = '';
                    files.video_files = files.image_files = files.audio_files = [];
                    modals.createNote = false;
                    await loadNotes();
                } else {
                    alert('Ошибка создания заметки');
                }
            } catch (error) {
                alert('Ошибка сети');
            } finally {
                loading.value = false;
            }
        };

        const deleteNote = async (id) => {
            modals.deleteNoteId = id;
            modals.confirmDelete = true;
        };

        const confirmDeleteNote = async () => {
            try {
                const token = localStorage.getItem('access_token');
                const res = await fetch(`${API}/notes/delete/${modals.deleteNoteId}/`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (res.ok) {
                    await loadNotes();
                    showNotification('Заметка удалена', 'success');
                } else {
                    showNotification('Ошибка удаления', 'error');
                }
            } catch (error) {
                showNotification('Ошибка сети', 'error');
            } finally {
                modals.confirmDelete = false;
                modals.deleteNoteId = null;
            }
        };

        const addFiles = (event, type) => {
            const selectedFiles = Array.from(event.target.files);
            const validFiles = selectedFiles.filter(file => {
                if (type === 'video_files') return file.type.startsWith('video/');
                if (type === 'image_files') return file.type.startsWith('image/');
                if (type === 'audio_files') return file.type.startsWith('audio/');
                return false;
            });
            files[type].push(...validFiles);
            event.target.value = '';
        };

        const dropFiles = (event, type) => {
            event.preventDefault();
            const droppedFiles = Array.from(event.dataTransfer.files);
            const validFiles = droppedFiles.filter(file => {
                if (type === 'video_files') return file.type.startsWith('video/');
                if (type === 'image_files') return file.type.startsWith('image/');
                if (type === 'audio_files') return file.type.startsWith('audio/');
                return false;
            });
            files[type].push(...validFiles);
            event.target.classList.remove('active');
        };

        const removeFile = (type, index) => {
            files[type].splice(index, 1);
        };

        const viewNote = async (id) => {
            try {
                const token = localStorage.getItem('access_token');
                const res = await fetch(`${API}/notes/get_note/${id}/`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (res.ok) {
                    const data = await res.json();
                    modals.noteDetail = data.data || data;
                    modals.showNoteDetail = true;
                } else {
                    console.error('Failed to fetch note details');
                }
            } catch (error) {
                console.error('Failed to load note:', error);
            }
        };

        const getUserInfo = async () => {
            try {
                const token = localStorage.getItem('access_token');
                const res = await fetch(`${API}/user/self_info/`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (res.ok) {
                    user.value = await res.json();
                }
            } catch (error) {
                console.error('Failed to get user info:', error);
            }
        };

        const openLightbox = (url) => {
            modals.lightboxUrl = url;
            modals.lightbox = true;
        };

        const openImageZoom = (url) => {
            modals.zoomedImageUrl = url;
            modals.imageZoom = true;
            // Reset zoom state
            imageZoomLevel.value = 1;
            imageTranslateX.value = 0;
            imageTranslateY.value = 0;
        };

        const handleZoomWheel = (event) => {
            event.preventDefault();
            const delta = event.deltaY > 0 ? -0.05 : 0.05;
            const newZoom = Math.max(0.5, Math.min(5, imageZoomLevel.value + delta));
            imageZoomLevel.value = newZoom;
        };

        const startDrag = (event) => {
            if (imageZoomLevel.value > 1) {
                isDragging.value = true;
                dragStartX.value = event.clientX - imageTranslateX.value;
                dragStartY.value = event.clientY - imageTranslateY.value;
            }
        };

        const drag = (event) => {
            if (isDragging.value && imageZoomLevel.value > 1) {
                imageTranslateX.value = event.clientX - dragStartX.value;
                imageTranslateY.value = event.clientY - dragStartY.value;
            }
        };

        const endDrag = () => {
            isDragging.value = false;
        };

        // Computed
        const isHealthy = computed(() => healthStatus.notes && healthStatus.users);

        // Lifecycle
        onMounted(async () => {
            await checkHealth();
            
            const token = localStorage.getItem('access_token');
            if (token) {
                await getUserInfo();
                if (user.value) {
                    currentView.value = 'dashboard';
                    startTokenRefresh();
                    await loadNotes();
                }
            }
        });

        return {
            currentView, user, notes, loading, sidebarOpen, modals, forms, files, healthStatus, isHealthy,
            login, register, logout, loadNotes, createNote, deleteNote, confirmDeleteNote,
            addFiles, dropFiles, removeFile, openLightbox, getUserInfo, viewNote, openImageZoom,
            handleZoomWheel, startDrag, drag, endDrag, imageZoomLevel, imageTranslateX, imageTranslateY, isDragging
        };
    },

    template: `
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
                            <i class="fas fa-user absolute left-4 top-4 text-gray-400"></i>
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

                                    <!-- Media Summary -->
                                    <div v-if="note.image_urls?.length || note.video_urls?.length || note.audio_urls?.length" class="mb-4 flex flex-wrap gap-2">
                                        <div v-if="note.image_urls?.length" class="flex items-center bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-medium">
                                            <i class="fas fa-image mr-1"></i>
                                            {{ note.image_urls.length }} фото
                                        </div>
                                        <div v-if="note.video_urls?.length" class="flex items-center bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-medium">
                                            <i class="fas fa-video mr-1"></i>
                                            {{ note.video_urls.length }} видео
                                        </div>
                                        <div v-if="note.audio_urls?.length" class="flex items-center bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-xs font-medium">
                                            <i class="fas fa-music mr-1"></i>
                                            {{ note.audio_urls.length }} аудио
                                        </div>
                                    </div>

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

        <!-- Create Note Modal -->
        <transition name="fade">
            <div v-if="modals.createNote" class="fixed inset-0 modal-backdrop flex items-center justify-center p-4 z-50">
                <div class="glass rounded-3xl w-full max-w-6xl max-h-[95vh] overflow-auto shadow-2xl">
                    <!-- Header -->
                    <div class="sticky top-0 glass rounded-t-3xl p-6 border-b border-gray-200/50 flex justify-between items-center">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 bg-gradient-to-r from-cyan-400 to-purple-500 rounded-xl flex items-center justify-center">
                                <i class="fas fa-plus text-white text-lg"></i>
                            </div>
                            <div>
                                <h2 class="text-2xl font-bold text-white">Создать заметку</h2>
                                <p class="text-sm text-gray-300">Добавьте текст и медиафайлы</p>
                            </div>
                        </div>
                        <button @click="modals.createNote = false" 
                                class="w-10 h-10 rounded-xl bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition">
                            <i class="fas fa-times text-gray-600"></i>
                        </button>
                    </div>

                    <form @submit.prevent="createNote" class="p-6 space-y-8">
                        <!-- Text Fields -->
                        <div class="grid md:grid-cols-2 gap-6">
                            <div class="space-y-2">
                                <label class="block text-sm font-semibold text-gray-300">
                                    <i class="fas fa-heading mr-2 text-cyan-400"></i>Заголовок
                                </label>
                                <input v-model="forms.note.title" type="text" placeholder="Введите заголовок заметки..." required
                                       class="w-full p-4 rounded-2xl bg-gray-800 text-white border-2 border-transparent outline-none focus:border-cyan-400 transition font-medium placeholder-gray-400">
                            </div>
                            <div class="space-y-2">
                                <label class="block text-sm font-semibold text-gray-300">
                                    <i class="fas fa-align-left mr-2 text-purple-400"></i>Описание
                                </label>
                                <textarea v-model="forms.note.content" placeholder="Добавьте описание заметки..." required rows="3"
                                          class="w-full p-4 rounded-2xl bg-gray-800 text-white border-2 border-transparent outline-none focus:border-purple-400 transition font-medium resize-none placeholder-gray-400"></textarea>
                            </div>
                        </div>

                        <!-- Media Upload Section -->
                        <div class="grid lg:grid-cols-3 gap-6">
                            <!-- Video Upload -->
                            <div class="space-y-4">
                                <div class="flex items-center space-x-2">
                                    <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                                        <i class="fas fa-video text-blue-600"></i>
                                    </div>
                                    <div>
                                        <h4 class="font-semibold text-white">Видео</h4>
                                        <p class="text-xs text-gray-300">MP4, AVI, WebM</p>
                                    </div>
                                </div>
                                <div @click="$refs.videoInput.click()" 
                                     @dragover.prevent @drop="dropFiles($event, 'video_files')"
                                     @dragenter="$event.target.classList.add('active')"
                                     @dragleave="$event.target.classList.remove('active')"
                                     class="drop-zone rounded-2xl p-8 text-center cursor-pointer min-h-[120px] flex flex-col items-center justify-center">
                                    <i class="fas fa-cloud-upload-alt text-3xl text-gray-400 mb-3"></i>
                                    <p class="text-sm font-medium text-gray-300">Загрузить видео</p>
                                    <p class="text-xs text-gray-400 mt-1">или перетащите сюда</p>
                                </div>
                                <input ref="videoInput" @change="addFiles($event, 'video_files')" 
                                       type="file" multiple accept=".mp4,.avi,.webm" class="hidden">
                                <div v-if="files.video_files.length" class="space-y-2 max-h-32 overflow-y-auto">
                                    <div v-for="(file, i) in files.video_files" :key="i"
                                         class="file-item flex items-center justify-between p-3 rounded-xl">
                                        <div class="flex items-center space-x-3 flex-1 min-w-0">
                                            <i class="fas fa-file-video text-blue-500 flex-shrink-0"></i>
                                            <span class="text-sm font-medium truncate" style="color: white;" :title="file.name">{{ file.name }}</span>
                                        </div>
                                        <button @click="removeFile('video_files', i)" type="button"
                                                class="w-6 h-6 rounded-full bg-red-100 hover:bg-red-200 flex items-center justify-center transition flex-shrink-0 ml-2">
                                            <i class="fas fa-times text-red-500 text-xs"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <!-- Image Upload -->
                            <div class="space-y-4">
                                <div class="flex items-center space-x-2">
                                    <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                                        <i class="fas fa-image text-green-600"></i>
                                    </div>
                                    <div>
                                        <h4 class="font-semibold text-white">Изображения</h4>
                                        <p class="text-xs text-gray-300">JPEG, PNG, WebP</p>
                                    </div>
                                </div>
                                <div @click="$refs.imageInput.click()" 
                                     @dragover.prevent @drop="dropFiles($event, 'image_files')"
                                     @dragenter="$event.target.classList.add('active')"
                                     @dragleave="$event.target.classList.remove('active')"
                                     class="drop-zone rounded-2xl p-8 text-center cursor-pointer min-h-[120px] flex flex-col items-center justify-center">
                                    <i class="fas fa-cloud-upload-alt text-3xl text-gray-400 mb-3"></i>
                                    <p class="text-sm font-medium text-gray-300">Загрузить фото</p>
                                    <p class="text-xs text-gray-400 mt-1">или перетащите сюда</p>
                                </div>
                                <input ref="imageInput" @change="addFiles($event, 'image_files')" 
                                       type="file" multiple accept=".jpeg,.jpg,.png,.webp" class="hidden">
                                <div v-if="files.image_files.length" class="space-y-2 max-h-32 overflow-y-auto">
                                    <div v-for="(file, i) in files.image_files" :key="i"
                                         class="file-item flex items-center justify-between p-3 rounded-xl">
                                        <div class="flex items-center space-x-3 flex-1 min-w-0">
                                            <i class="fas fa-file-image text-green-500 flex-shrink-0"></i>
                                            <span class="text-sm font-medium truncate" style="color: white;" :title="file.name">{{ file.name }}</span>
                                        </div>
                                        <button @click="removeFile('image_files', i)" type="button"
                                                class="w-6 h-6 rounded-full bg-red-100 hover:bg-red-200 flex items-center justify-center transition flex-shrink-0 ml-2">
                                            <i class="fas fa-times text-red-500 text-xs"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <!-- Audio Upload -->
                            <div class="space-y-4">
                                <div class="flex items-center space-x-2">
                                    <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                                        <i class="fas fa-music text-purple-600"></i>
                                    </div>
                                    <div>
                                        <h4 class="font-semibold text-white">Аудио</h4>
                                        <p class="text-xs text-gray-300">MP3, OGG, WAV</p>
                                    </div>
                                </div>
                                <div @click="$refs.audioInput.click()" 
                                     @dragover.prevent @drop="dropFiles($event, 'audio_files')"
                                     @dragenter="$event.target.classList.add('active')"
                                     @dragleave="$event.target.classList.remove('active')"
                                     class="drop-zone rounded-2xl p-8 text-center cursor-pointer min-h-[120px] flex flex-col items-center justify-center">
                                    <i class="fas fa-cloud-upload-alt text-3xl text-gray-400 mb-3"></i>
                                    <p class="text-sm font-medium text-gray-300">Загрузить аудио</p>
                                    <p class="text-xs text-gray-400 mt-1">или перетащите сюда</p>
                                </div>
                                <input ref="audioInput" @change="addFiles($event, 'audio_files')" 
                                       type="file" multiple accept=".mp3,.ogg,.wav" class="hidden">
                                <div v-if="files.audio_files.length" class="space-y-2 max-h-32 overflow-y-auto">
                                    <div v-for="(file, i) in files.audio_files" :key="i"
                                         class="file-item flex items-center justify-between p-3 rounded-xl">
                                        <div class="flex items-center space-x-3 flex-1 min-w-0">
                                            <i class="fas fa-file-audio text-purple-500 flex-shrink-0"></i>
                                            <span class="text-sm font-medium truncate" style="color: white;" :title="file.name">{{ file.name }}</span>
                                        </div>
                                        <button @click="removeFile('audio_files', i)" type="button"
                                                class="w-6 h-6 rounded-full bg-red-100 hover:bg-red-200 flex items-center justify-center transition flex-shrink-0 ml-2">
                                            <i class="fas fa-times text-red-500 text-xs"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Action Buttons -->
                        <div class="sticky bottom-0 glass rounded-b-3xl p-6 border-t border-gray-200/50 flex space-x-4">
                            <button type="button" @click="modals.createNote = false"
                                    class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-4 rounded-2xl transition">
                                <i class="fas fa-times mr-2"></i>Отмена
                            </button>
                            <button type="submit" :disabled="loading"
                                    class="flex-1 bg-gradient-to-r from-cyan-400 to-purple-500 hover:from-cyan-500 hover:to-purple-600 text-white font-bold py-4 rounded-2xl transition shadow-lg disabled:opacity-50">
                                <i class="fas fa-spinner fa-spin mr-2" v-if="loading"></i>
                                <i class="fas fa-save mr-2" v-else></i>
                                {{ loading ? 'Создание...' : 'Создать заметку' }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </transition>

        <!-- Profile Modal -->
        <transition name="fade">
            <div v-if="modals.profile" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                <div class="glass rounded-3xl p-8 w-full max-w-md">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-2xl font-bold text-white">
                            <i class="fas fa-user mr-2"></i>Профиль
                        </h2>
                        <button @click="modals.profile = false" class="text-gray-300 hover:text-white">
                            <i class="fas fa-times text-xl"></i>
                        </button>
                    </div>

                    <div v-if="user" class="text-center">
                        <div class="w-20 h-20 bg-gradient-to-r from-cyan-400 to-purple-500 rounded-full mx-auto mb-4 flex items-center justify-center text-white text-2xl font-bold">
                            {{ user.username.charAt(0).toUpperCase() }}
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
                                <span class="text-gray-300">Заметок:</span>
                                <span class="font-bold text-white">{{ notes.length }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </transition>

        <!-- Note Detail Modal -->
        <transition name="fade">
            <div v-if="modals.showNoteDetail" class="fixed inset-0 modal-backdrop flex items-center justify-center p-4 z-50">
                <div class="glass rounded-3xl w-full max-w-6xl max-h-[95vh] overflow-auto shadow-2xl">
                    <!-- Header -->
                    <div class="sticky top-0 glass rounded-t-3xl p-6 border-b border-gray-200/50 flex justify-between items-center">
                        <div class="flex items-center space-x-3 flex-1 min-w-0 pr-4">
                            <div class="w-10 h-10 bg-gradient-to-r from-green-400 to-teal-400 rounded-xl flex items-center justify-center">
                                <i class="fas fa-eye text-white text-lg"></i>
                            </div>
                            <div class="min-w-0 flex-1 mr-4">
                                <h2 class="text-2xl font-bold text-white truncate">{{ modals.noteDetail?.title || 'Заметка' }}</h2>
                                <p class="text-sm text-gray-300">Просмотр заметки</p>
                            </div>
                        </div>
                        <button @click="modals.showNoteDetail = false" 
                                class="w-10 h-10 rounded-xl bg-red-500 hover:bg-red-600 flex items-center justify-center transition">
                            <i class="fas fa-times text-white"></i>
                        </button>
                    </div>
                    
                    <div v-if="modals.noteDetail" class="p-6 space-y-8">
                        <!-- Text Content -->
                        <div class="space-y-6">
                            <div class="space-y-2">
                                <label class="block text-sm font-semibold text-gray-300">
                                    <i class="fas fa-heading mr-2 text-cyan-400"></i>Заголовок
                                </label>
                                <div class="w-full p-4 rounded-2xl bg-gray-800 border-2 border-transparent font-medium text-white break-words">
                                    {{ modals.noteDetail.title || 'Без заголовка' }}
                                </div>
                            </div>
                            <div class="space-y-2">
                                <label class="block text-sm font-semibold text-gray-300">
                                    <i class="fas fa-align-left mr-2 text-purple-400"></i>Описание
                                </label>
                                <div class="w-full p-4 rounded-2xl bg-gray-800 border-2 border-transparent font-medium text-white whitespace-pre-wrap break-words">
                                    {{ modals.noteDetail.content || 'Нет содержимого' }}
                                </div>
                            </div>
                        </div>

                        <!-- Media Content -->
                        <div class="grid lg:grid-cols-3 gap-6">
                            <!-- Videos -->
                            <div v-if="modals.noteDetail.video_urls && modals.noteDetail.video_urls.length" class="space-y-4">
                                <div class="flex items-center space-x-2">
                                    <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                                        <i class="fas fa-video text-blue-600"></i>
                                    </div>
                                    <div>
                                        <h4 class="font-semibold text-white">Видео</h4>
                                        <p class="text-xs text-gray-300">{{ modals.noteDetail.video_urls.length }} файл(ов)</p>
                                    </div>
                                </div>
                                <div class="space-y-4 max-h-64 overflow-y-auto">
                                    <video v-for="url in modals.noteDetail.video_urls" :key="url" 
                                           :src="url" controls class="w-full rounded-xl shadow-md">
                                    </video>
                                </div>
                            </div>

                            <!-- Images -->
                            <div v-if="modals.noteDetail.image_urls && modals.noteDetail.image_urls.length" class="space-y-4">
                                <div class="flex items-center space-x-2">
                                    <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                                        <i class="fas fa-image text-green-600"></i>
                                    </div>
                                    <div>
                                        <h4 class="font-semibold text-white">Изображения</h4>
                                        <p class="text-xs text-gray-300">{{ modals.noteDetail.image_urls.length }} файл(ов)</p>
                                    </div>
                                </div>
                                <div class="grid grid-cols-2 gap-4 max-h-64 overflow-y-auto">
                                    <div v-for="url in modals.noteDetail.image_urls" :key="url" class="relative group">
                                        <img :src="url" @click="openImageZoom(url)"
                                             class="w-full h-24 object-cover rounded-xl cursor-zoom-in hover:opacity-80 transition shadow-md">
                                        <div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 rounded-xl transition flex items-center justify-center pointer-events-none">
                                            <i class="fas fa-search-plus text-white opacity-0 group-hover:opacity-100 transition text-xl"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Audio -->
                            <div v-if="modals.noteDetail.audio_urls && modals.noteDetail.audio_urls.length" class="space-y-4">
                                <div class="flex items-center space-x-2">
                                    <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                                        <i class="fas fa-music text-purple-600"></i>
                                    </div>
                                    <div>
                                        <h4 class="font-semibold text-white">Аудио</h4>
                                        <p class="text-xs text-gray-300">{{ modals.noteDetail.audio_urls.length }} файл(ов)</p>
                                    </div>
                                </div>
                                <div class="space-y-3 max-h-64 overflow-y-auto">
                                    <audio v-for="url in modals.noteDetail.audio_urls" :key="url" 
                                           :src="url" controls class="w-full">
                                    </audio>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div v-else class="p-6">
                        <p class="text-gray-300">Загрузка данных...</p>
                    </div>
                </div>
            </div>
        </transition>

        <!-- Image Zoom Modal -->
        <transition name="fade">
            <div v-if="modals.imageZoom" 
                 class="fixed inset-0 bg-black/95 flex items-center justify-center z-[60]" 
                 @wheel="handleZoomWheel" 
                 @mousedown="startDrag" 
                 @mousemove="drag" 
                 @mouseup="endDrag" 
                 @mouseleave="endDrag">
                <button @click="modals.imageZoom = false" 
                        class="absolute top-6 right-6 w-12 h-12 bg-black/70 hover:bg-black/90 text-white rounded-full flex items-center justify-center transition text-xl z-10">
                    <i class="fas fa-times"></i>
                </button>
                <div class="absolute top-6 left-6 bg-black/70 text-white px-4 py-2 rounded-full text-sm z-10">
                    {{ Math.round(imageZoomLevel * 100) }}%
                </div>
                <img :src="modals.zoomedImageUrl" 
                     ref="zoomedImage"
                     :style="{ transform: 'scale(' + imageZoomLevel + ') translate(' + imageTranslateX + 'px, ' + imageTranslateY + 'px)', cursor: isDragging ? 'grabbing' : 'grab' }"
                     class="max-w-none max-h-none object-contain transition-transform duration-300"
                     @dragstart.prevent>
            </div>
        </transition>

        <!-- Confirm Delete Modal -->
        <transition name="fade">
            <div v-if="modals.confirmDelete" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                <div class="glass rounded-3xl p-6 w-full max-w-sm">
                    <div class="text-center">
                        <div class="w-16 h-16 bg-red-100 rounded-full mx-auto mb-4 flex items-center justify-center">
                            <i class="fas fa-trash text-red-500 text-2xl"></i>
                        </div>
                        <h3 class="text-xl font-bold mb-2 text-white">Удалить заметку?</h3>
                        <p class="text-gray-300 mb-6">Это действие нельзя отменить</p>
                        <div class="flex space-x-3">
                            <button @click="modals.confirmDelete = false" 
                                    class="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded-xl transition">
                                Отмена
                            </button>
                            <button @click="confirmDeleteNote" 
                                    class="flex-1 bg-red-500 hover:bg-red-600 text-white py-2 rounded-xl transition">
                                Удалить
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </transition>

        <!-- Lightbox -->
        <transition name="fade">
            <div v-if="modals.lightbox" @click="modals.lightbox = false" 
                 class="fixed inset-0 bg-black/90 flex items-center justify-center p-4 z-50 cursor-zoom-out">
                <img :src="modals.lightboxUrl" class="max-w-full max-h-full rounded-2xl shadow-2xl">
                <button @click="modals.lightbox = false" 
                        class="absolute top-6 right-6 text-white text-3xl hover:text-red-400 transition">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </transition>
    </div>
    `
}).mount('#app');
