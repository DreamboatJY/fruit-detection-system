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
    timeout: 60000,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const getBatchStatus = (batchId) => {
  return request({
    url: `/detection/batch/${batchId}`,
    method: "get",
  });
};

export const getBatchItems = (batchId) => {
  return request({
    url: `/detection/batch/${batchId}/items`,
    method: "get",
  });
};

export const retryFailedBatch = (batchId) => {
  return request({
    url: `/detection/batch/${batchId}/retry-failed`,
    method: "post",
  });
};

export const cancelBatch = (batchId) => {
  return request({
    url: `/detection/batch/${batchId}/cancel`,
    method: "post",
  });
};

export const getBatchExportUrl = (batchId, type = "zip") => {
  const baseURL = request.defaults?.baseURL || "/api";
  return `${baseURL}/detection/batch/${batchId}/export/${type}`;
};

export const exportBatch = (batchId, type = "zip") => {
  return request({
    url: `/detection/batch/${batchId}/export/${type}`,
    method: "get",
    responseType: "blob",
  });
};

// 获取检测历史
export const getDetectionHistory = (params) => {
  return request({
    url: "/detection/history",
    method: "get",
    params,
  });
};

// 获取检测详情
export const getDetectionDetail = (id) => {
  return request({
    url: `/detection/detail/${id}`,
    method: "get",
  });
};

// 获取目标库列表
export const getTargetList = () => {
  return request({
    url: "/detection/targets/list",
    method: "get",
  });
};

// 删除检测记录
export const deleteDetection = (id) => {
  return request({
    url: `/detection/${id}`,
    method: "delete",
  });
};
