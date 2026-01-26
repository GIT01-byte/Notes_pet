// src/composables/useAuth.js
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

// const API_URL = 'http://localhost:8000'; // Допустим, ваш бэкенд работает на этом адресе
const API_URL = 'https://example.com/api'; // Replace with your actual backend URL

export default function useAuth() {
  const error = ref(null);
  const loading = ref(false);
  const router = useRouter();

  const getToken = () => localStorage.getItem('token'); //Получение токена из localStorage
  const setToken = (token) => localStorage.setItem('token', token);  //Сохранение токена в localStorage
  const clearToken = () => localStorage.removeItem('token'); //Очистка токена из localStorage

  // ... (ваши существующие функции register, login, logout, getUser)

  const register = async (userData) => {
    error.value = null;
    loading.value = true;
    try {
      const response = await axios.post(`${API_URL}/auth/register/`, userData);

      //Сохраняем токен после успешной регистрации:
      setToken(response.data.access);

      router.push('/home'); // Перенаправляем на домашнюю страницу
    } catch (err) {
      error.value = err.response?.data?.message || 'Ошибка регистрации';
      console.error(err);
    } finally {
      loading.value = false;
    }
  };

  const login = async (username, password) => {
    error.value = null;
    loading.value = true;
    try {
      const response = await axios.post(`${API_URL}/auth/login/`, { username, password });

      //Сохраняем токен после успешной авторизации:
      setToken(response.data.access);

      router.push('/home');
    } catch (err) {
      error.value = err.response?.data?.message || 'Ошибка входа';
      console.error(err);
    } finally {
      loading.value = false;
    }
  };


  const logout = async () => {
    error.value = null;
    loading.value = true;
    try {
        //No backend logout endpoint
        //localStorage.removeItem('user');
        clearToken();
        router.push('/login');
    } catch (err) {
        error.value = 'Ошибка выхода';
        console.error(err);
    } finally {
      loading.value = false;
    }
  };

  const getUser = async () => {
    error.value = null;
    loading.value = true;
    try {
      const token = getToken();
      if (!token) throw new Error('No token found');

      const response = await axios.get(`${API_URL}/auth/user/`, {
          headers: {
              Authorization: `Bearer ${token}`
          }
      });
      return response.data;
    } catch (err) {
        error.value = err.response?.data?.message || 'Ошибка получения информации о пользователе';
        console.error(err);
        clearToken(); //Clear token on error
        router.push('/login'); //Redirect to login
        return null;
    } finally {
        loading.value = false;
    }
  };

  // --- Методы для работы с заметками ---

  const createNote = async (title, content, video_urls, image_urls, audio_urls) => {
    error.value = null;
    loading.value = true;
    try {
      const token = getToken(); //Получаем токен
      if (!token) throw new Error('Нужен токен для создания заметки');

      const params = new URLSearchParams();
      params.append('title', title);
      params.append('content', content);

      const response = await axios.post(
        `${API_URL}/notes/create/?${params.toString()}`,
        { video_urls, image_urls, audio_urls },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json', // Важно указать Content-Type
          },
        }
      );

      return response.data; // { message: "Создание заметки '...' прошла успешно!" }
    } catch (err) {
      error.value = err.response?.data?.message || 'Ошибка при создании заметки';
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const deleteNote = async (noteId) => {
    error.value = null;
    loading.value = true;

    try {
      const token = getToken();
      if (!token) throw new Error('Нужен токен для удаления заметки');

      const response = await axios.post(
        `${API_URL}/notes/delete/${noteId}/`,
        {}, // Отправляем пустое тело запроса
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return response.data; // { message: "Заметка с ID ... успешно удалена" }
    } catch (err) {
      error.value = err.response?.data?.message || 'Ошибка при удалении заметки';
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const getNotes = async () => {
    error.value = null;
    loading.value = true;
    try {
      const token = getToken();
      if (!token) throw new Error('Нужен токен, ... ')
    } catch (err) {
      error.value = err.response?.data?.message || 'Ошибка при получении заметок';
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  return {
    // ... (ваши существующие возвращаемые значения)
    error,
    loading,
    getToken,
    register,
    login,
    logout,
    getUser,
    createNote,
    deleteNote,
    getNotes,
  };
}
