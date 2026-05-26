import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    // 新增 resolve 配置
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
