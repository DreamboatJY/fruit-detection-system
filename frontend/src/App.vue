<template>
  <router-view v-if="isAuthPage" />
  <MainLayout v-else>
    <template #sidebar>
      <Sidebar />
    </template>
    <template #header>
      <Header />
    </template>
    <template #content>
      <router-view />
    </template>
  </MainLayout>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { isSessionExpired, clearSession } from "./utils/session";
import MainLayout from "./layouts/MainLayout.vue";
import Sidebar from "./components/Sidebar.vue";
import Header from "./components/Header.vue";

const route = useRoute();
const router = useRouter();

const isAuthPage = computed(() => {
  const authPaths = ["/login", "/register", "/forgot-password"];
  return authPaths.includes(route.path);
});

onMounted(() => {
  const token = localStorage.getItem("token")
  if (token && isSessionExpired()) {
    clearSession()
    router.push("/login")
  }
})
</script>

<style scoped></style>
