<script lang="ts" setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "src/boot/axios";
import ExerciseList, {
} from "src/components/ExerciseList.vue";
import type {ExerciseSummary} from "src/types/types";

interface ExerciseCompletionResponse {
  id: number;
  session: number;
  // other fields not strictly required here
}

const route = useRoute();
const router = useRouter();

const exercises = ref<ExerciseSummary[] | null>(null);
const loading = ref(true);
const loadError = ref<string | null>(null);

const creating = ref(false);
const createError = ref<string | null>(null);

const sessionId = computed<number | null>(() => {
  const raw = route.query.sessionId;
  if (Array.isArray(raw)) return Number(raw[0]);
  if (raw == null) return null;
  const parsed = Number(raw);
  return Number.isNaN(parsed) ? null : parsed;
});

onMounted(async () => {
  await fetchExercises();
});

async function fetchExercises(): Promise<void> {
  loading.value = true;
  loadError.value = null;

  try {
    // for now, simplest: no filters; backend orders by name via Meta.ordering
    const res = await api.get<ExerciseSummary[]>("exercises/");
    exercises.value = res.data;
  } catch (err) {
    console.error(err);
    loadError.value = "Failed to load exercises.";
  } finally {
    loading.value = false;
  }
}

async function handleSelectExercise(exercise: ExerciseSummary): Promise<void> {
  if (!sessionId.value) {
    createError.value = "No session specified for this exercise.";
    return;
  }

  creating.value = true;
  createError.value = null;

  try {
    const payload = {
      session: sessionId.value,
      exercise_id: exercise.id,
    };

    const res = await api.post<ExerciseCompletionResponse>(
      "exercise-completions/",
      payload
    );

    const completionId = res.data.id;
    await router.push(`/exercise-completion/${completionId}`);
  } catch (err) {
    console.error(err);
    createError.value = "Failed to add exercise to this session.";
  } finally {
    creating.value = false;
  }
}

async function goBackToSession(): Promise<void> {
    await router.push(`/`);
}

async function goToCreateExercise (): Promise<void> {
  const q = route.query.sessionId
    ? { sessionId: String(route.query.sessionId) }
    : {};

  await router.push({
    path: "/exercises/new",
    query: q,
  });
};

</script>

<template>
  <q-page padding>
    <div class="column q-gutter-md">
      <q-banner
        v-if="loadError || createError"
        dense
        class="bg-red-2 text-red-10"
      >
        {{ loadError || createError }}
      </q-banner>

      <q-card flat bordered>
        <q-card-section class="row items-center justify-between">
          <div>
            <div class="text-h6">
              Choose an exercise
            </div>
            <div class="text-caption text-grey-7">
              Tap an exercise to attach it to this session.
            </div>
            <div
              v-if="!sessionId"
              class="text-caption text-negative q-mt-xs"
            >
              No sessionId provided in the URL. Use the “Add Exercise to Session” button from an active session.
            </div>
          </div>

          <div class="row items-center q-gutter-sm">
            <q-btn
              flat
              round
              dense
              icon="arrow_back"
              @click="goBackToSession"
            />
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <ExerciseList
            :exercises="exercises"
            :loading="loading || creating"
            @select="handleSelectExercise"
          />
        </q-card-section>

        <q-card-section v-if="creating">
          <div class="text-caption text-grey-7">
            Creating exercise completion for this session...
          </div>
        </q-card-section>

        <q-card-section>
            <q-btn
              color="primary"
              dense
              icon="add"
              label="Create New Exercise"
              @click="goToCreateExercise"
            />
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>