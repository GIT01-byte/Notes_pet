import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    authToken: null,
  }),
  getters: {
    getUser: (state) => state.user,
    getIsAuthenticated: (state) => state.isAuthenticated,
  },
  actions: {
    setUser(user) {
      this.user = user;
      this.isAuthenticated = !!user; // Устанавливаем isAuthenticated в true, если есть пользователь
    },
    setAuthToken(token) {
      this.authToken = token;
    },
    clearAuthToken() {
      this.authToken = null;
    },
    logout() {
      this.user = null;
      this.isAuthenticated = false;
      this.clearAuthToken();
    },
  },
  persist: true, // Enable persistence
});
