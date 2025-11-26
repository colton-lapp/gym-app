import { defineStore } from "pinia";
import { api } from "src/boot/axios";

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

interface AuthState {
  user: User | null;
  loading: boolean;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    user: null,
    loading: false,
  }),

  actions: {
    async fetchMe() {
  try {
    const { data } = await api.get<User>("/auth/me/");
    this.user = data;
    return true;
  } catch {
    this.user = null;
    return false;
  }
},

async login(email: string, password: string) {
  await api.post("/auth/login/", { email, password });
  await this.fetchMe();
},

async signup(email: string, password: string, access_code: string, first_name: string, last_name:string) {
  await api.post("/auth/signup/", { email, password, access_code, first_name, last_name });
  await this.fetchMe();
},

async logout() {
  await api.post("/auth/logout/");
  this.user = null;
}
  },
});