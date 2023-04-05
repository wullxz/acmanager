import Vue from 'vue';
import Router from 'vue-router';
import ServerList from '../components/ServerList.vue';
import ServerConfig from '../components/ServerConfig.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
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
    {
      path: '/server/:srv_number?',
      name: 'ServerConfig',
      component: ServerConfig,
    },
  ],
});
