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

// 获取目标库列表
export const getTargetList = () => {
    return request({
        url: "/targets/list",
        method: "get",
    });
};