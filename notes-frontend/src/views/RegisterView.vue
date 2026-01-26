<template>
  <div class="register-container">
    <div class="auth-card">
      <h1>Register</h1>
      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" v-model="username" placeholder="Enter username" />
      </div>

      <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" v-model="email" placeholder="Enter email" />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" placeholder="Enter password" />
      </div>

      <button @click="handleRegister">Register</button>
      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import useAuth from '@/composables/useAuth';

export default {
  setup() {
    const { register, error } = useAuth();
    const username = ref('');
    const email = ref('');
    const password = ref('');

    const handleRegister = async () => {
      await register({ username: username.value, email: email.value, password: password.value });
    };

    return {
      username,
      email,
      password,
      handleRegister,
      error,
    };
  },
};
</script>

<style scoped>

</style>
