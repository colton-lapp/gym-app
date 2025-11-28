import { boot } from "quasar/wrappers";
import axios from "axios";
import type  { AxiosInstance } from "axios";
// import { getCookie } from "src/utils/csrf";

declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
  }
}

const api = axios.create({
   baseURL: import.meta.env.VITE_API_BASE_URL ||  "http://localhost:8000/api/",
  withCredentials: true,  // REQUIRED for Django session auth
});

export default boot(({ app }) => {
  app.config.globalProperties.$axios = api;
});

export { api };

// Don't need this after using session cookies in settings.py
// api.interceptors.request.use((config) => {
//   const csrftoken = getCookie("csrftoken");
//   if (csrftoken) {
//     config.headers["X-CSRFToken"] = csrftoken;
//   }
//   return config;
// });