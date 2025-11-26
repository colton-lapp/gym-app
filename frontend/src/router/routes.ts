import type { RouteRecordRaw } from "vue-router";

const routes: RouteRecordRaw[] = [
  {
    path: "/auth",
    component: () => import("layouts/AuthLayout.vue"),  // <--
    children: [
      { path: "login", component: () => import("pages/LoginPage.vue") },
      { path: "signup", component: () => import("pages/SignupPage.vue") },
      { path: "account", component: () => import("pages/AccountPage.vue") },
    ],
  },
  {
    path: "/",
    component: () => import("layouts/MainLayout.vue"),
    children: [
      { path: "", component: () => import("pages/HomePage.vue") },
      { path: "session/:id", component: () => import("pages/SessionPage.vue") },
      { path: "exercises", component: () => import("pages/ExerciseListPage.vue") },
      { path: "exercise-completion/:id", component: () => import("pages/ExerciseCompletionPage.vue") },
    ],
  },
];

export default routes;