import { useUserStore } from "../store/user.js";

// 基础配置
export const config = {
  baseURL: "https://wxapi.wenxin.icu", // 基础请求地址
  header: {
    "content-type": "application/json",
  },
  timeout: 60000, // 超时时间
  withCredentials: false, // 微信小程序不支持跨域携带凭证
  responseType: "text", // 微信小程序默认响应类型
  enableHttp2: false, // 禁用 HTTP2
  enableQuic: false, // 禁用 QUIC
  enableCache: false, // 禁用缓存
  enableHttpDNS: false, // 禁用 HTTPDNS
};

// 请求拦截器
const requestInterceptor = (options) => {
  console.log("请求拦截器开始处理:", options);
  try {
    // 获取用户 access_token
    const userStore = useUserStore();
    const access_token = userStore.getAccessToken;

    // 如果有 access_token，添加到请求头
    if (access_token) {
      options.header = {
        ...options.header,
        Authorization: `Bearer ${access_token}`,
      };
      console.log("添加 token 后的请求头:", options.header);
    }
  } catch (error) {
    console.error("请求拦截器错误", error);
  }

  console.log("请求拦截器处理完成:", options);
  return options;
};

// 响应拦截器
const responseInterceptor = async (response) => {
  console.log("响应拦截器收到响应:", response);
  // uni.request 的响应结构
  const { statusCode, data } = response;

  // 请求成功
  if (statusCode >= 200 && statusCode < 300) {
    // 如果后端返回的数据结构是 { code, data, message }
    if (data && typeof data === "object") {
      const { code, data: responseData, message } = data;
      console.log("解析后的响应数据:", {
        code,
        responseData,
        message,
      });

      // 业务状态码成功
      if (code === 200) {
        return responseData;
      }

      // token 过期
      if (code === 401) {
        // 清除用户信息
        const userStore = useUserStore();
        userStore.clearUserInfo();
        // 跳转到登录页
        uni.navigateTo({
          url: "/pages/login/login",
        });
        return Promise.reject(new Error("登录已过期，请重新登录"));
      }

      // 其他业务错误
      return Promise.reject(new Error(message || "请求失败"));
    }

    // 如果直接返回数组，直接返回
    if (Array.isArray(data)) {
      return data;
    }

    // 直接返回数据
    return data;
  }

  // HTTP 错误
  if (statusCode === 401) {
    // 清除用户信息
    const userStore = useUserStore();
    userStore.clearUserInfo();
    // 跳转到登录页
    uni.navigateTo({
      url: "/pages/login/login",
    });
    return Promise.reject(new Error("登录已过期，请重新登录"));
  }

  return Promise.reject(new Error("网络请求失败"));
};

// 请求方法
const request = (options) => {
  console.log("开始请求:", options);
  // 合并配置
  options = {
    ...config,
    ...options,
    url: config.baseURL + options.url,
  };

  // 请求拦截
  options = requestInterceptor(options);
  console.log("请求拦截后的配置:", options);

  // 发起请求
  return new Promise((resolve, reject) => {
    const requestTask = uni.request({
      ...options,
      success: async (res) => {
        console.log("请求成功:", res);
        try {
          // 响应拦截
          const data = await responseInterceptor(res);
          console.log("响应拦截后的数据:", data);
          resolve(data);
        } catch (error) {
          reject(error);
        }
      },
      fail: (err) => {
        console.error("请求失败:", err);
        uni.showToast({
          title: "网络错误，请检查网络连接",
          icon: "none",
        });
        reject(err);
      },
      complete: (res) => {
        console.log("请求完成:", res);
      },
    });

    // 监听请求任务
    if (requestTask) {
      requestTask.onHeadersReceived((res) => {
        console.log("收到响应头:", res);
      });
    }
  });
};

// 常用请求方法
export const http = {
  get(url, data = {}, options = {}) {
    return request({
      url,
      data,
      method: "GET",
      ...options,
    });
  },

  post(url, data = {}, options = {}) {
    return request({
      url,
      data,
      method: "POST",
      ...options,
    });
  },
  stream(url, method, data = {}, options = {}) {
    return request({
      url,
      method,
	  data,
	  ...options,
    });
  },

  put(url, data = {}, options = {}) {
    return request({
      url,
      data,
      method: "PUT",
      ...options,
    });
  },

  delete(url, data = {}, options = {}) {
    return request({
      url,
      data,
      method: "DELETE",
      ...options,
    });
  },

  upload(url, filePath, options = {}) {
    return new Promise((resolve, reject) => {
      const userStore = useUserStore();
      const access_token = userStore.getAccessToken;

      uni.uploadFile({
        url: config.baseURL + url,
        filePath,
        name: "file",
        header: {
          Authorization: `Bearer ${access_token}`,
        },
        success: (res) => {
          try {
            const data = JSON.parse(res.data);
            if (data.code === 200) {
              resolve(data.data);
            } else {
              reject(new Error(data.message));
            }
          } catch (e) {
            reject(new Error("解析响应数据失败"));
          }
        },
        fail: (err) => {
          reject(err);
        },
      });
    });
  },
};
