<script lang="ts" setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "src/boot/axios";

interface Exercise {
  id: number;
  name: string;
}

interface ExerciseCompletionResponse {
  id: number;
  session: number;
}

interface OptionItem {
  id: number;
  name: string;
}

const route = useRoute();
const router = useRouter();

const newExerciseName = ref("");
const saving = ref(false);
const saveError = ref<string | null>(null);

// metric flags
const trackReps = ref(true);
const trackWeight = ref(false);
const trackDistance = ref(false);
const trackDuration = ref(false);
const trackResistance = ref(false);
const trackNotes = ref(false);

// tag / muscle-group options
const muscleGroupOptions = ref<OptionItem[]>([]);
const tagOptions = ref<OptionItem[]>([]);
const selectedMuscleGroupIds = ref<number[]>([]);
const selectedTagIds = ref<number[]>([]);

const sessionId = computed<number | null>(() => {
  const raw = route.query.sessionId;
  if (Array.isArray(raw)) return Number(raw[0]);
  if (raw == null) return null;
  const parsed = Number(raw);
  return Number.isNaN(parsed) ? null : parsed;
});

onMounted(async () => {
  await Promise.all([fetchMuscleGroups(), fetchTags()]);
});

async function fetchMuscleGroups(): Promise<void> {
  try {
    const res = await api.get<OptionItem[]>("muscle-groups/");
    muscleGroupOptions.value = res.data;
  } catch (err) {
    console.error("Failed to load muscle groups", err);
  }
}

async function fetchTags(): Promise<void> {
  try {
    const res = await api.get<OptionItem[]>("tags/");
    tagOptions.value = res.data;
  } catch (err) {
    console.error("Failed to load tags", err);
  }
}

function buildExercisePayload() {
  return {
    name: newExerciseName.value.trim(),
    track_reps: trackReps.value,
    track_weight: trackWeight.value,
    track_distance: trackDistance.value,
    track_duration: trackDuration.value,
    track_resistance: trackResistance.value,
    track_notes: trackNotes.value,
    muscle_group_ids: selectedMuscleGroupIds.value,
    tag_ids: selectedTagIds.value,
  };
}

async function createExerciseOnly(): Promise<void> {
  if (!newExerciseName.value.trim()) {
    saveError.value = "Exercise name cannot be empty.";
    return;
  }

  saving.value = true;
  saveError.value = null;

  try {
    await api.post<Exercise>("exercises/", buildExercisePayload());

    if (sessionId.value) {
      await router.push({
        path: "/exercises",
        query: { sessionId: String(sessionId.value) },
      });
    } else {
      await router.push("/exercises");
    }
  } catch (err) {
    console.error(err);
    saveError.value = "Failed to create exercise.";
  } finally {
    saving.value = false;
  }
}

async function createExerciseAndAttach(): Promise<void> {
  if (!sessionId.value) return;
  if (!newExerciseName.value.trim()) {
    saveError.value = "Exercise name cannot be empty.";
    return;
  }

  saving.value = true;
  saveError.value = null;

  try {
    const res = await api.post<Exercise>("exercises/", buildExercisePayload());
    const exercise = res.data;

    const compRes = await api.post<ExerciseCompletionResponse>(
      "exercise-completions/",
      {
        session: sessionId.value,
        exercise_id: exercise.id,
      }
    );

    const completionId = compRes.data.id;
    await router.push(`/exercise-completion/${completionId}`);
  } catch (err) {
    console.error(err);
    saveError.value = "Failed to create and attach exercise.";
  } finally {
    saving.value = false;
  }
}

async function cancel(): Promise<void> {
  if (sessionId.value) {
    await router.push({
      path: "/exercises",
      query: { sessionId: String(sessionId.value) },
    });
  } else {
    await router.push("/exercises");
  }
}
</script>

<template>
  <q-page padding>
    <div class="column q-gutter-md">
      <q-card flat bordered>
        <q-card-section class="row items-center justify-between">
          <div>
            <div class="text-h6">
              Create Exercise
            </div>
            <div class="text-caption text-grey-7">
              Define a new exercise to use in your workouts.
              <span v-if="sessionId">
                It can also be added to your current session after creation.
              </span>
            </div>
          </div>

          <q-btn
            flat
            round
            dense
            icon="close"
            @click="cancel"
          />
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md">
          <q-input
            v-model="newExerciseName"
            outlined
            label="Exercise name"
            :disable="saving"
            autofocus
          />

          <div class="text-subtitle2 q-mt-md">
            Metrics to track per set / split
          </div>

          <div class="row q-col-gutter-md">
            <div class="col-12 col-sm-6">
              <q-checkbox
                v-model="trackReps"
                :disable="saving"
                label="Reps"
              />
              <q-checkbox
                v-model="trackWeight"
                :disable="saving"
                label="Weight"
              />
              <q-checkbox
                v-model="trackDistance"
                :disable="saving"
                label="Distance"
              />
            </div>
            <div class="col-12 col-sm-6">
              <q-checkbox
                v-model="trackDuration"
                :disable="saving"
                label="Duration"
              />
              <q-checkbox
                v-model="trackResistance"
                :disable="saving"
                label="Resistance"
              />
              <q-checkbox
                v-model="trackNotes"
                :disable="saving"
                label="Per-set note"
              />
            </div>
          </div>

          <div class="text-subtitle2 q-mt-md">
            Muscle groups and tags
          </div>

          <div class="row q-col-gutter-md">
            <div class="col-12 col-sm-6">
              <q-select
                v-model="selectedMuscleGroupIds"
                :options="muscleGroupOptions"
                option-value="id"
                option-label="name"
                emit-value
                map-options
                multiple
                use-chips
                dense
                outlined
                label="Muscle groups"
                :disable="saving"
              />
            </div>

            <div class="col-12 col-sm-6">
              <q-select
                v-model="selectedTagIds"
                :options="tagOptions"
                option-value="id"
                option-label="name"
                emit-value
                map-options
                multiple
                use-chips
                dense
                outlined
                label="Tags"
                :disable="saving"
              />
            </div>
          </div>

          <div class="text-caption text-grey-7">
            Defaults like “push”, “pull”, “cardio”, “machine” and standard muscle groups
            are available here. You can add more later.
          </div>

          <div
            v-if="saveError"
            class="text-negative text-caption"
          >
            {{ saveError }}
          </div>
        </q-card-section>

        <q-card-actions align="right" class="q-gutter-sm">
          <q-btn
            flat
            label="Cancel"
            @click="cancel"
            :disable="saving"
          />

          <q-btn
            color="primary"
            label="Create"
            :loading="saving"
            @click="createExerciseOnly"
          />

          <q-btn
            v-if="sessionId"
            color="positive"
            label="Create + Add to Session"
            :loading="saving"
            @click="createExerciseAndAttach"
          />
        </q-card-actions>
      </q-card>
    </div>
  </q-page>
</template>