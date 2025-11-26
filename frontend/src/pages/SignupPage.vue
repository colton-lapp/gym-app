<script lang="ts" setup>
import { ref } from "vue";
import { useAuthStore } from "src/stores/auth";
import { useRouter } from "vue-router";
import { useQuasar } from 'quasar';
import { isAxiosError } from "src/utils/isAxiosError";

interface SignupErrorResponse {
  detail: string;
}

const loading = ref(false); // Add loading state
const email = ref("");
const password = ref("");
const access_code = ref("")
const first_name = ref("")
const last_name = ref("")

const auth = useAuthStore();
const router = useRouter();
const $q = useQuasar(); // Initialize Quasar
interface SignupErrorResponse {
  detail: string;
}

async function submit() {
  loading.value = true;

  try {
    await auth.signup(email.value, password.value, access_code.value, first_name.value, last_name.value);
    await router.push("/");
  } catch (error: unknown) {
    if (isAxiosError<SignupErrorResponse>(error)) {
      $q.notify({
        type: "negative",
        message: error.response?.data?.detail ?? "Signup failed.",
        position: "top",
      });
    } else {
      $q.notify({
        type: "negative",
        message: "Unexpected error occurred.",
        position: "top",
      });
    }
  } finally {
    loading.value = false;
  }
}
</script>


<template>
  <q-page padding>
    <q-input v-model="first_name" label="First Name" />
    <q-input v-model="last_name" label="Last Name" />
    <q-input v-model="email" label="Email" />
    <q-input v-model="password" type="password" label="Password" />
    <q-input v-model="access_code" type="text" label="Access Code" />
    <q-btn @click="submit" label="Sign Up" color="primary" class="q-mt-md" />
  </q-page>
</template>