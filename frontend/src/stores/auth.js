import { defineStore } from "pinia";
import { login as loginApi, register as registerApi, getCurrentUser } from "../api/auth";

const TOKEN_KEY = "token";
const USER_KEY = "user";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || "",
    user: JSON.parse(localStorage.getItem(USER_KEY) || "null"),
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token),
    displayName: (state) => state.user?.nickname || state.user?.username || "用户",
  },
  actions: {
    setAuth(token, user) {
      this.token = token;
      this.user = user;
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    },
    clearAuth() {
      this.token = "";
      this.user = null;
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    },
    async login(payload) {
      const response = await loginApi(payload);
      this.setAuth(response.access_token, response.user);
      return response;
    },
    async register(payload) {
      const response = await registerApi(payload);
      this.setAuth(response.access_token, response.user);
      return response;
    },
    async fetchCurrentUser() {
      const response = await getCurrentUser();
      this.user = response.user;
      localStorage.setItem(USER_KEY, JSON.stringify(response.user));
      return response.user;
    },
  },
});
