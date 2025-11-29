<script lang="ts" setup>
import { ref } from "vue";
import { useAuthStore } from "src/stores/auth";
import { useRouter } from "vue-router";
import { useQuasar } from 'quasar';

const email = ref("");
const password = ref("");
const loading = ref(false); // Add loading state

const auth = useAuthStore();
const router = useRouter();
const $q = useQuasar(); // Initialize Quasar

async function submit() {
  loading.value = true; // Start loading

  try {
    // Await the login attempt
    await auth.login(email.value, password.value);
    // If successful, redirect
    await router.push("/");
  } catch (error) {
    // If an error occurs (e.g., wrong credentials, network issue)
    console.error("Login error:", error);

    // Display a user-friendly notification
    $q.notify({
      type: 'negative',
      message: 'Login failed. Please check your credentials or network connection.',
      position: 'top'
    });

  } finally {
    loading.value = false; // Stop loading regardless of success or failure
  }
}

async function goToSignup() {
  await router.push("/auth/signup");  
}



</script>

<template>
  <q-page padding>
    <h3> Login </h3>
    <p>You must login or create an account before use.</p>
    <q-input v-model="email" label="Email" />
    <q-input v-model="password" type="password" label="Password" />
    <div class="row q-mt-md q-mb-lg">
      <q-btn @click="submit" label="Login" color="primary" class="q-mr-sm" />
    <q-btn @click="goToSignup" label="Create an Account" color="secondary"  />
    </div>
  </q-page>
</template>