<template>
  <div class="main-layout">
    <aside class="sidebar">
      <slot name="sidebar"></slot>
    </aside>

    <div class="main-container">
      <header class="header">
        <slot name="header"></slot>
      </header>

      <main class="content">
        <slot name="content"></slot>
      </main>
    </div>
  </div>
</template>

<script setup></script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 220px;
  background-color: var(--bg-primary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.03);
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 64px;
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
}

.content {
  flex: 1;
  padding: 28px 32px;
  overflow-y: auto;
  background-color: var(--bg-secondary);
}
</style>
