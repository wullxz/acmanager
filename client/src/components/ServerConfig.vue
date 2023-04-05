<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-12">
        <h1>Server Configuration</h1>
        <hr><br>
        <FormulateInput
          type="text"
          label="Server Name:"
          v-model="server.SERVER.name"
          validation="required" /><br>
        <FormulateInput
          type="password"
          label="Server Password:"
          v-model="server.SERVER.password"/><br>
        <FormulateInput
          type="password"
          label="Admin Password:"
          v-model="server.SERVER.admin_password"/><br>
        <FormulateInput
          type="vue-select"
          v-model="selectedTrack"
          :options="trackNames"
          placeholder="Select Track!"
          label="Select Track:"
          validation="required" /><br>
        <FormulateInput
          type="vue-select"
          v-model="selectedLayout"
          :options="availableLayouts"
          placeholder="Select Layout!"
          label="Select Layout:"
          validation="required"
          :key="selectedLayout">
        </FormulateInput><br>
        <div class="content-divider">
          <div class="divider-left">
            <FormulateInput
              type="vue-select"
              :options="availableCars"
              placeholder="Select Cars!"
              label="Select Cars:"
              v-model="currentCar"
            />
            <FormulateInput
              type="number"
              name="addCarCount"
              label="add how many?"
              v-model="carCount"
              min="1"
            />
            <button
              type="button"
              class="btn btn-success"
              @click="addCar"
              label-class="btn btn-success btn-sm">Add this car</button>
          </div>
          <div class="divider-right" height="10em">
            <table class="table table-hover info-table">
              <tr>
                <td>Name:</td><td>{{ currentCarProps?.name }}</td>
              </tr>
              <tr>
                <td>Brand:</td><td>{{ currentCarProps?.brand }}</td>
              </tr>
              <tr>
                <td>Tags:</td><td>{{ currentCarProps?.tags.join(' ') }}</td>
              </tr>
              <tr>
                <td>bhp:</td><td>{{ currentCarProps?.specs?.bhp }}</td>
              </tr>
              <tr>
                <td>Weight:</td><td>{{ currentCarProps?.specs?.weight }}</td>
              </tr>
              <tr>
                <td>Top-Speed:</td><td>{{ currentCarProps?.specs?.topspeed }}</td>
              </tr>
              <tr>
                <td>Acceleration:</td><td>{{ currentCarProps?.specs?.acceleration }}</td>
              </tr>
              <tr>
                <td>Description:</td>
                <td><div class="line-restrictor" v-html="currentCarProps?.description">
                </div></td>
              </tr>
            </table>
          </div>
          <br style="clear:both;"/>
        </div>
        <div>
          <span class="align-bottom">
            Selected Cars: {{ selectedCarCount }} / {{ availablePitBoxes }}
          </span>
        </div>
        <div>
          <table class="table table-hover">
            <thead>
              <tr>
                <th scope="col">Count</th>
                <th scope="col">Car</th>
                <th scope="col">Brand</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(car, name) in selectedCars" :key="name">
                <td>{{ car.count }}</td>
                <td>{{ car.name }}</td>
                <td>{{ car.brand }}</td>
                <td>
                  <div class="btn-group" role="group">
                    <button
                      type="button"
                      @click="removeCar(name)"
                      class="btn btn-danger btn-sm">
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div>
            <button
              type="button"
              class="btn btn-success"
              @click="saveServerCfg"
              label-class="btn btn-success btn-sm">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Vue from 'vue';

export default {
  data() {
    return {
      server: { SERVER: {} },
      entries: {},
      tracks: { dummy: { layouts: [] } },
      cars: {},
      trackNames: [],
      availableLayouts: [],
      availableCars: [],
      selectedTrack: '',
      selectedLayout: '',
      selectedCars: {},
      currentCar: '',
      carCount: 2,
    };
  },
  watch: {
    selectedTrack(newtrack) {
      this.server.SERVER.track = newtrack;
      this.availableLayouts = this.trackLayoutNames();
      [this.selectedLayout] = this.availableLayouts;
    },
    selectedLayout(newlayout) {
      this.server.SERVER.config_track = newlayout;
    },
  },
  computed: {
    currentCarProps() {
      return this.cars[this.currentCar];
    },
    selectedCarCount() {
      return Object.values(this.selectedCars).reduce((count, car) => count + car.count, 0);
    },
    availablePitBoxes() {
      const track = this.tracks[this.selectedTrack];
      const layout = track?.layouts[this.selectedLayout];
      return layout?.pitboxes || 0;
    },
  },
  methods: {
    getServerConfig() {
      if (!this.$route.params.srv_number) {
        return;
      }

      const path = `/api/server/${this.$route.params.srv_number}`;
      axios.get(path)
        .then((res) => {
          // fill server config
          this.server = res.data.server;
          this.selectedTrack = this.server.SERVER.track;
          this.selectedLayout = this.server.SERVER.config_track;
          this.entries = res.data.entries;

          // fill selected cars
          this.entries = res.data.entries;
          Object.keys(this.entries).forEach((entryKey) => {
            const entry = this.entries[entryKey];
            this.addCar(null, entry.model, 1);
          });
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    getAvailableTracks() {
      const path = '/api/tracks';
      return axios.get(path)
        .then((res) => {
          this.trackNames = Object.keys(res.data);
          this.tracks = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    trackLayoutNames() {
      return Object.keys(this.tracks[this.selectedTrack].layouts);
    },
    getAvailableCars() {
      const path = '/api/cars';
      return axios.get(path)
        .then((res) => {
          this.availableCars = Object.keys(res.data);
          this.cars = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    addCar(event, addedCar, carCount) {
      // allow this method to be called elsewhere and default to input fields
      const car = addedCar || this.currentCar;
      const ccount = carCount || this.carCount;
      const carProp = this.cars[car];

      // check if the car is already selected
      if (Object.prototype.hasOwnProperty.call(this.selectedCars, car)) {
        this.selectedCars[car].count += parseInt(ccount, 10);
        return;
      }

      // add the car to the selected cars list
      Vue.set(this.selectedCars, car, {
        count: parseInt(ccount, 10),
        name: carProp.name,
        brand: carProp.brand,
      });
    },
    removeCar(carName) {
      Vue.delete(this.selectedCars, carName);
    },
    saveServerCfg() {
      const srvnum = (this.$route.params.srv_number) ? this.$route.params.srv_number : '';
      const servercfg = this.server.SERVER;
      let carlist = [];
      Object.keys(this.selectedCars).forEach((car) => {
        carlist = carlist.concat(Array(this.selectedCars[car].count).fill(car));
      });
      axios.post(`/api/server/${srvnum}`, {
        server: servercfg,
        cars: carlist,
      });
    },
  },
  created() {
    const dataPromises = [];
    dataPromises.push(this.getAvailableTracks());
    dataPromises.push(this.getAvailableCars());
    Promise.all(dataPromises)
      .then(() => {
        this.getServerConfig();
      });
  },
};
</script>

<style>
.info-table td {
  vertical-align: top;
}

.info-table > tr > td:last-child {
  width: 100%;
  padding-left: 4px;
}

.content-divider > div {
  width: 50%;
}

.content-divider > .divider-left {
  float: left;
  padding-right: 2px;
}

.content-divider > .divider-right {
  float: right;
}

.line-restrictor {
  -webkit-line-clamp: 4;
  line-clamp: 4;
  overflow-y: scroll;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-box-orient: vertical;
}
</style>
