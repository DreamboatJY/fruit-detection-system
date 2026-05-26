import request from "./request";

export const login = (data) => request.post("/api/login", data);
export const register = (data) => request.post("/api/register", data);
export const checkUsername = (username) =>
  request.post("/api/check-username", { username });
export const checkEmail = (email) =>
  request.post("/api/check-email", { email });
