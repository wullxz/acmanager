import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import VueFormulate from '@braid/vue-formulate';
import FormulateVSelectPlugin from '@cone2875/vue-formulate-select';
import App from './App.vue';
import router from './router';
import 'bootstrap/dist/css/bootstrap.css';
import 'vue-select/dist/vue-select.css';

Vue.config.productionTip = false;

Vue.use(BootstrapVue);
Vue.use(VueFormulate, { plugins: [FormulateVSelectPlugin] });

new Vue({
  router,
  render: (h) => h(App),
}).$mount('#app');
