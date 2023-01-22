<template>
  <nav>
    <router-link to="/servers">Servers</router-link> |
    <router-link to="/about">About</router-link>
  </nav>
  <router-view/>
</template>

<style>
div[data-theme='dark'] {
  --globa-bg-color: #444;
  --global-text-color: #ddd;
  --global-link-color: yellow;
  --global-link-hover: lightyellow;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>
