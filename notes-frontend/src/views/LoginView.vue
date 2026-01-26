<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1>Login</h1>

      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" v-model="username" placeholder="Enter username" />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" placeholder="Enter password" />
      </div>

      <button @click="handleLogin" :disabled="loading">
        <span v-if="loading">Logging In...</span>
        <span v-else>Login</span>
      </button>

      <p v-if="error" class="error-message">{{ error }}</p>

      <p class="auth-link">
        Don't have an account? <router-link to="/register">Register here</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import useAuth from '@/composables/useAuth';

export default {
  setup() {
    const { login, error, loading } = useAuth();
    const username = ref('');
    const password = ref('');

    const handleLogin = async () => {
      await login(username.value, password.value);
    };

    return {
      username,
      password,
      handleLogin,
      error,
      loading,
    };
  },
};
</script>

<style scoped>

</style>
