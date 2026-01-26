import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresAuth: false },
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// navigation guard
router.beforeEach((to, from, next) => {
    const accessToken = localStorage.getItem('accessToken');
  if (to.meta.requiresAuth && !accessToken) {
    next({ name: 'login' });
  } else if ((to.name === 'login' || to.name === 'register') && accessToken) {
        next({ name: 'home' }); // Если пользователь залогинен, перенаправляем с login/register на home
    }
  else {
    next();
  }
});

export default router;
