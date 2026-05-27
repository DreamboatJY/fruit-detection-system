import request from "../utils/request";

export const login = (data) => {
  return request({
    url: "/auth/login",
    method: "post",
    data,
  });
};

export const register = (data) => {
  return request({
    url: "/auth/register",
    method: "post",
    data,
  });
};

export const getCurrentUser = () => {
  return request({
    url: "/auth/me",
    method: "get",
  });
};

export const updateCurrentUser = (data) => {
  return request({
    url: "/auth/me",
    method: "put",
    data,
  });
};

export const changePassword = (data) => {
  return request({
    url: "/auth/password",
    method: "put",
    data,
  });
};

export const getUserStats = () => {
  return request({
    url: "/auth/me/stats",
    method: "get",
  });
};

export const uploadAvatar = (data) => {
  return request({
    url: "/auth/avatar",
    method: "post",
    data,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};
