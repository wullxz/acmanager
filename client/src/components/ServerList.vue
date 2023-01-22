<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Servers</h1>
        <hr><br><br>
        <button type="button" class="btn btn-success btn-sm">Add Server</button>
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
            <tr v-for="(server, index) in servers" :key="index">
              <td>{{ server.SERVER.name }}</td>
              <td>{{ server.SERVER.track }}</td>
              <td>{{ server.SERVER.max_clients }}</td>
              <td>
                <div class="btn-group" role="group">
                  <button type="button" class="btn btn-warning btn-sm">Update</button>
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
      servers: [],
    };
  },
  methods: {
    getServers() {
      const path = 'http://192.168.178.211:5000/api/server';
      axios.get(path)
        .then((res) => {
          this.servers = res.data.servers;
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
