<script setup lang="ts">
import { useAuthStore } from "src/stores/auth";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

async function logout() {
  await auth.logout();
  await router.push("/login");
}

async function goHome() {
  await router.push("/");
}
</script>

<template>
  <q-page padding>
    <h4>Account</h4>
    <div><strong>Name:</strong> {{ auth.user?.first_name}} {{ auth.user?.last_name}}</div>
    <div><strong>Email:</strong> {{ auth.user?.email }}</div>
    <div><strong>Account ID:</strong>{{ auth.user?.id}}</div>

    <q-btn
      class="q-mt-md"
      label="Logout"
      color="negative"
      @click="logout"
    />

    <q-btn
      class="q-mt-md"
      label="Home"
      @click="goHome"
    />

  </q-page>
</template>