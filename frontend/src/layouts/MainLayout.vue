<template>
  <q-layout view="lHh Lpr lFf">

    <q-header elevated>
      <q-toolbar class="flex justify-between items-center">

        <q-toolbar-title class="text-bold">
          Gym App
        </q-toolbar-title>

        <!-- If logged in, show avatar -->
        <div v-if="auth.user" class="column items-center cursor-pointer q-ma-none q-pa-none q-mt-sm" @click="goAccount">
          <q-avatar color="secondary" text-color="white">
            {{ firstInitial }}
          </q-avatar>
          <span class="text-caption q-pa">{{ auth.user?.first_name}} {{ auth.user?.last_name}} </span>
        </div>

        <!-- If not logged in, show login button -->
        <q-btn
          v-else
          dense
          flat
          label="Login"
          color="primary"
          @click="router.push('/login')"
        />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>

  </q-layout>
</template>


<script setup lang="ts">
import { computed } from "vue";
import { useAuthStore } from "src/stores/auth";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

const firstInitial = computed(() =>
  auth.user?.first_name?.charAt(0)?.toUpperCase() ??
  ""
);

async function goAccount() {
 await router.push("/auth/account");
}
</script>