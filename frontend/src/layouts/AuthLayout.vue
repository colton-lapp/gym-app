<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();


async function goHome(){
  await router.push("/")
}
</script>
<template>
  <q-layout view="lHh Lpr lFf">

    <q-header elevated>
      <q-toolbar class="flex justify-between items-center">

        <q-toolbar-title class="cursor-pointer" @click="goHome">
          Get Swole, Make Graphs
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="column flex-center" padding>
        <router-view />
      </q-page>
    </q-page-container>
  </q-layout>
</template>