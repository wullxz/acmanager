import { createRouter, createWebHistory } from 'vue-router';
import ServerList from '../components/ServerList.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: ServerList,
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue'),
  },
  {
    path: '/servers',
    name: 'Servers',
    component: ServerList,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
