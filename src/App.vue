<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #f5f6fa;
}

#app {
  min-height: 100vh;
}

/* 全局样式 */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}
</style>