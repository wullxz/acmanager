import { createApp } from 'vue';
import BootstrapVue from 'bootstrap-vue';
import App from './App.vue';
import router from './router';
import 'bootstrap/dist/css/bootstrap.css';

createApp(App).use(BootstrapVue).use(router).mount('#app');
