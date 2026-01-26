import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { loginUser, logoutUser, registerUser, getUserInfo} from '@/api'; //Укажите  правильный  путь к api.js

export default function useAuth() {
    const router = useRouter();
    const error = ref(null);
    const loading = ref(false);

    const login = async (username, password) => {
        loading.value = true;
        error.value = null;
        try {
            await loginUser(username, password);
            await router.push('/'); // перенаправить на главную страницу после входа в систему
        } catch (err) {
            error.value = err.message || 'Ошибка входа в систему';
        } finally {
            loading.value = false;
        }
    };

    const register = async (userData) => {
        loading.value = true;
        error.value = null;
        try {
            await registerUser(userData);
            await router.push('/'); // перенаправить на главную страницу после регистрации
        } catch (err) {
            error.value = err.message || 'Ошибка регистрации';
        } finally {
            loading.value = false;
        }
    };

    const logout = async () => {
        loading.value = true;
        error.value = null;
        try {
            await logoutUser();
            await router.push('/login'); // перенаправить на страницу входа после выхода из системы
        } catch (err) {
            error.value = err.message || 'Ошибка выхода из системы';
        } finally {
            loading.value = false;
        }
    };

    const getUser = async () => {
        loading.value = true;
        error.value = null;
        try {
            const userInfo = await getUserInfo();
           //Тут  можно сохранить  информацию о пользователе в  ref или reactive переменную
            return userInfo;
        } catch (err) {
            error.value = err.message || 'Ошибка получения информации о пользователе';
        } finally {
            loading.value = false;
        }
    };


    return {
        login,
        register,
        logout,
        getUser,
        error,
        loading,
    };
}
