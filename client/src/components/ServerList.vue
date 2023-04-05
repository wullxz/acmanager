<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Servers</h1>
        <hr><br><br>
        <router-link to="/server/" custom v-slot="{ navigate }">
          <button type="button" class="btn btn-success btn-sm"
                  @click="navigate" role="link">Add Server</button>
        </router-link>
        <br><br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Name</th>
              <th scope="col">Track</th>
              <th scope="col">Cars</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(instance, index) in instances" :key="index">
              <td>{{ instance.server.SERVER.name }}</td>
              <td>{{ instance.server.SERVER.track }}</td>
              <td>{{ instance.server.SERVER.max_clients }}</td>
              <td>
                <div class="btn-group" role="group">
                  <router-link :to="`/server/${instance.srvnum}`" custom v-slot="{ navigate }">
                    <button type="button" class="btn btn-warning btn-sm"
                            @click="navigate" role="link">Edit</button>
                  </router-link>
                  <button type="button" class="btn btn-danger btn-sm">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      instances: [],
    };
  },
  methods: {
    getServers() {
      const path = '/api/server';
      axios.get(path)
        .then((res) => {
          console.log(res.data);
          this.instances = res.data.servers;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getServers();
  },
};
</script>
