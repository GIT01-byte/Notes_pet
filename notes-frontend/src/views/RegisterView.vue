<template>
  <div class="register-container">
    <h1>Register</h1>
    <input type="text" v-model="username" placeholder="Username">
    <input type="email" v-model="email" placeholder="Email">
    <input type="password" v-model="password" placeholder="Password">
    <button @click="register">Register</button>
    <p v-if="error" class="error-message">{{ error }}</p>
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
      register: handleRegister,
      error,
    };
  },
};
</script>
