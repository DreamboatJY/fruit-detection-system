import axios from "axios";
import { ElMessage } from "element-plus";

const request = axios.create({
  baseURL: "http://localhost:8000", // 后端地址
  timeout: 10000,
});

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || "请求失败";
    ElMessage.error(message);
    return Promise.reject(error);
  },
);

export default request;
