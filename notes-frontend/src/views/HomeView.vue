<template>
  <div class="home-container">
    <h1>Welcome!</h1>
    <button @click="handleLogout">Logout</button>
    <button @click="handleGetUserInfo">Get User Info</button>
      <div v-if="userInfo">
        <p>User ID: {{ userInfo.user_id }}</p>
        <p>Username: {{ userInfo.username }}</p>
        <p>Email: {{ userInfo.email }}</p>
      </div>
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import useAuth from '@/composables/useAuth';

export default {
  setup() {
    const { logout, error, getUser } = useAuth();
    const userInfo = ref(null); //Для хранения информации о пользователе


    const handleLogout = async () => {
      await logout();
    };

    const handleGetUserInfo = async () => {
      try {
        userInfo.value = await getUser();
      } catch (e) {
        console.error(e);
      }
    }

    onMounted(async ()  => {
      try {
        userInfo.value = await getUser(); //Автоматически получаем информацию о пользователе при загрузке компонента
      } catch (e) {
        console.error(e)
      }
    })


    return {
      handleLogout,
      error,
      userInfo,
      handleGetUserInfo
    };
  },
};
</script>
