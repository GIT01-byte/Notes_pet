<template>
  <div class="login-container">
    <h1>Login</h1>
    <input type="text" v-model="username" placeholder="Username">
    <input type="password" v-model="password" placeholder="Password">
    <button @click="handleLogin">Login</button> <!-- ИСПРАВЛЕНО: вызываем handleLogin -->
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<script>
import { ref } from 'vue';
import useAuth from '@/composables/useAuth';

export default {
  setup() {
    const { login, error } = useAuth();
    const username = ref('');
    const password = ref('');  //ИСПРАВЛЕНО: явно передаём username.value и password.value
const handleLogin = async () => {
  await login(username.value, password.value);
};

return {
  username,
  password,
  handleLogin, // ИСПРАВЛЕНО: возвращаем handleLogin, а не login
  error,
};

              },
};
</script>
