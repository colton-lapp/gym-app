import { boot } from "quasar/wrappers";
import axios from "axios";
import  { type AxiosInstance } from "axios";
import { AxiosHeaders } from "axios";
import { getCookie } from "src/utils/csrf";

declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
  }
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/",
  withCredentials: true,
  headers: new AxiosHeaders(),   // ★ Important fix
});

export default boot(({ app }) => {
  app.config.globalProperties.$axios = api;
});

export { api };


// Add CSRF header for unsafe methods
declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
  }
}



api.interceptors.request.use((config) => {
  const method = (config.method || "get").toLowerCase();
  const needsCsrf = ["post", "put", "patch", "delete"].includes(method);

  if (needsCsrf) {
    const csrftoken = getCookie("csrftoken");
    if (csrftoken) {
      // ensure headers is AxiosHeaders (it now always is)
      config.headers.set("X-CSRFToken", csrftoken);
    }
  }

  return config;
});