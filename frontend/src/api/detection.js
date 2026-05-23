import request from "../utils/request";

// 单图检测接口
export const detectSingleImage = (data) => {
  return request({
    url: "/detection/single",
    method: "post",
    data,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

// 批量检测接口
export const detectBatchImages = (data) => {
  return request({
    url: "/detection/batch",
    method: "post",
    data,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

// 视频检测接口
export const detectVideo = (data) => {
  return request({
    url: "/detection/video",
    method: "post",
    data,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

// 获取目标库列表
export const getTargetList = () => {
  return request({
    url: "/detection/targets/list",
    method: "get",
  });
};