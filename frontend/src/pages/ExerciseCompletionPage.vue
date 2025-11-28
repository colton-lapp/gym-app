<script lang="ts" setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "src/boot/axios";
import NoteEditor from "src/components/NoteEditor.vue";
import ExerciseEventList from "src/components/ExerciseEventList.vue";
import LastExerciseCompletionSummary from "src/components/LastExerciseCompletionSummary.vue";

interface ExerciseEvent {
  id: number;
  order_index: number;
  reps: number | null;
  duration_seconds: number | null;
  weight: string | null;
  distance: string | null;
  resistance: string | null;
  note: string;
  created_at: string;
  updated_at: string;
}

interface Exercise {
  id: number;
  name: string;
  exercise_type?: string;
  track_reps?: boolean;
  track_weight?: boolean;
  track_distance?: boolean;
  track_duration?: boolean;
  track_resistance?: boolean;
  track_notes?: boolean;
}

interface ExerciseCompletionDetail {
  id: number;
  session: number;
  exercise: Exercise;
  note: string;
  created_at: string;
  updated_at: string;
  events: ExerciseEvent[];
}

interface ExerciseEventPayload {
  completion: number;
  order_index: number;
  reps: number | null;
  weight: number | null;
  distance: number | null;
  duration_seconds: number | null;
  resistance: number | null;
  note: string;
}

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const loadError = ref<string | null>(null);

const completion = ref<ExerciseCompletionDetail | null>(null);

// note editor state
const completionNote = ref<string>("");

// event dialog state
const eventDialogOpen = ref(false);
const eventDialogMode = ref<"create" | "edit">("create");
const activeEvent = ref<ExerciseEvent | null>(null);
const eventError = ref<string | null>(null);
const savingEvent = ref(false);

// event form fields (strings for numeric inputs)
const formReps = ref<string>("");
const formWeight = ref<string>("");
const formDistance = ref<string>("");
const formDurationSeconds = ref<string>("");
const formResistance = ref<string>("");
const formNote = ref<string>("");

// delete dialog state
const deleteDialogOpen = ref(false);
const eventToDelete = ref<ExerciseEvent | null>(null);
const deletingEvent = ref(false);
const deleteError = ref<string | null>(null);

const lastCompletion = ref<ExerciseCompletionDetail | null>(null);
const lastCompletionLoading = ref(false);
const lastCompletionError = ref<string | null>(null);

const showRepsField = computed<boolean>(() =>
  completion.value?.exercise.track_reps ?? true
);
const showWeightField = computed<boolean>(() =>
  completion.value?.exercise.track_weight ?? false
);
const showDistanceField = computed<boolean>(() =>
  completion.value?.exercise.track_distance ?? false
);
const showDurationField = computed<boolean>(() =>
  completion.value?.exercise.track_duration ?? false
);
const showResistanceField = computed<boolean>(() =>
  completion.value?.exercise.track_resistance ?? false
);
const showNoteField = computed<boolean>(() =>
  completion.value?.exercise.track_notes ?? false
);

// derived
const completionId = computed<number>(() => Number(route.params.id));

const exerciseName = computed<string>(() => {
  if (!completion.value?.exercise) return "Exercise";
  return completion.value.exercise.name;
});

const totalEvents = computed<number>(() =>
  completion.value?.events ? completion.value.events.length : 0
);

const createdAt = computed<Date | null>(() =>
  completion.value ? new Date(completion.value.created_at) : null
);

const updatedAt = computed<Date | null>(() =>
  completion.value ? new Date(completion.value.updated_at) : null
);

// initial load
onMounted(async () => {
  await fetchCompletion();
  loading.value = false;
});

async function fetchCompletion(): Promise<void> {
  loadError.value = null;
  try {
    const res = await api.get<ExerciseCompletionDetail>(
      `exercise-completions/${completionId.value}/`
    );
    completion.value = res.data;

    // after we know which exercise this completion is for:
    await fetchLastCompletion(res.data.exercise.id);
  } catch (err) {
    console.error(err);
    loadError.value = "Failed to load exercise completion.";
  }
}

async function fetchLastCompletion(exerciseId: number): Promise<void> {
  lastCompletionLoading.value = true;
  lastCompletionError.value = null;

  try {
    const res = await api.get<ExerciseCompletionDetail>(
      `exercises/${exerciseId}/last_completion/`
    );
    console.log(res.data)
    // If the "last completion" is actually this one, treat as "no prior"
    if (res.data.id === completionId.value) {
      lastCompletion.value = null;
    } else {
      lastCompletion.value = res.data;
    }
  } catch (err: unknown) {
    const axiosErr = err as { response?: { status?: number } };
    if (axiosErr.response?.status === 404) {
      // no completions yet for this exercise
      lastCompletion.value = null;
    } else {
      console.error(err);
      lastCompletionError.value = "Failed to load last completion.";
    }
  } finally {
    lastCompletionLoading.value = false;
  }
}

// sync note with loaded completion
watch(
  completion,
  (val) => {
    completionNote.value = val?.note ?? "";
  },
  { immediate: true }
);

// note save / clear
async function saveCompletionNote(): Promise<void> {
  if (!completion.value) return;
  loadError.value = null;

  try {
    const res = await api.patch<ExerciseCompletionDetail>(
      `exercise-completions/${completion.value.id}/`,
      { note: completionNote.value }
    );
    completion.value = res.data;
  } catch (err) {
    console.error(err);
    loadError.value = "Failed to save exercise note.";
  }
}

async function clearCompletionNote(): Promise<void> {
  completionNote.value = "";
  await saveCompletionNote();
}

// navigation
async function goBackToSession(): Promise<void> {
  if (!completion.value?.session) return;
  // For now, just go home; you can later route to /session/:id
  await router.push(`/`);
}

// helpers for event form
function resetEventForm(): void {
  formReps.value = "";
  formWeight.value = "";
  formDistance.value = "";
  formDurationSeconds.value = "";
  formResistance.value = "";
  formNote.value = "";
  eventError.value = null;
}

function parseNumberOrNull(v: string): number | null {
  if (v === "" || v == null) return null;
  const num = Number(v);
  return Number.isNaN(num) ? null : num;
}

// open dialog to add set/split (with prefill from last_values)
async function onAddEventClick(): Promise<void> {
  if (!completion.value) return;

  eventDialogMode.value = "create";
  activeEvent.value = null;
  resetEventForm();

  try {
    const res = await api.get<{
      reps?: number | null;
      weight?: string | number | null;
      distance?: string | number | null;
      duration_seconds?: number | null;
      resistance?: string | number | null;
    }>(`exercise-completions/${completion.value.id}/last_values/`);

    const data = res.data;

    if (showRepsField.value && data.reps != null) {
      formReps.value = String(data.reps);
    }
    if (showWeightField.value && data.weight != null) {
      formWeight.value = String(data.weight);
    }
    if (showDistanceField.value && data.distance != null) {
      formDistance.value = String(data.distance);
    }
    if (showDurationField.value && data.duration_seconds != null) {
      formDurationSeconds.value = String(data.duration_seconds);
    }
    if (showResistanceField.value && data.resistance != null) {
      formResistance.value = String(data.resistance);
    }
  } catch (err) {
    console.log("last_values prefill error (ignored)", err);
  }

  eventDialogOpen.value = true;
}

// open dialog to edit an existing event
function openEditEventDialog(event: ExerciseEvent): void {
  eventDialogMode.value = "edit";
  activeEvent.value = event;
  eventError.value = null;

  formReps.value =
    event.reps != null ? String(event.reps) : "";
  formWeight.value =
    event.weight != null ? String(event.weight) : "";
  formDistance.value =
    event.distance != null ? String(event.distance) : "";
  formDurationSeconds.value =
    event.duration_seconds != null ? String(event.duration_seconds) : "";
  formResistance.value =
    event.resistance != null ? String(event.resistance) : "";
  formNote.value = event.note || "";

  eventDialogOpen.value = true;
}

// open delete confirmation
function openDeleteEventDialog(event: ExerciseEvent): void {
  eventToDelete.value = event;
  deleteError.value = null;
  deleteDialogOpen.value = true;
}

// submit create/edit event
async function submitEvent(): Promise<void> {
  if (!completion.value) return;

  savingEvent.value = true;
  eventError.value = null;

  const payload: ExerciseEventPayload = {
    completion: completion.value.id,
    order_index:
      activeEvent.value?.order_index ??
      ((completion.value.events?.length || 0) + 1),

    reps: null,
    weight: null,
    distance: null,
    duration_seconds: null,
    resistance: null,
    note: "",
  };

  payload.reps = showRepsField.value ? parseNumberOrNull(formReps.value) : null;
  payload.weight = showWeightField.value ? parseNumberOrNull(formWeight.value) : null;
  payload.distance = showDistanceField.value ? parseNumberOrNull(formDistance.value) : null;
  payload.duration_seconds = showDurationField.value
    ? parseNumberOrNull(formDurationSeconds.value)
    : null;
  payload.resistance = showResistanceField.value
    ? parseNumberOrNull(formResistance.value)
    : null;
  payload.note = showNoteField.value ? formNote.value.trim() : "";

  try {
    if (eventDialogMode.value === "create") {
      await api.post("events/", payload);
    } else if (activeEvent.value) {
      await api.patch(`events/${activeEvent.value.id}/`, payload);
    }

    eventDialogOpen.value = false;
    activeEvent.value = null;
    await fetchCompletion();
  } catch (err) {
    console.error(err);
    eventError.value = "Failed to save set / split.";
  } finally {
    savingEvent.value = false;
  }
}

// delete confirmed event
async function confirmDeleteEvent(): Promise<void> {
  if (!eventToDelete.value) return;

  deletingEvent.value = true;
  deleteError.value = null;

  try {
    await api.delete(`events/${eventToDelete.value.id}/`);
    deleteDialogOpen.value = false;
    eventToDelete.value = null;
    await fetchCompletion();
  } catch (err) {
    console.error(err);
    deleteError.value = "Failed to delete set / split.";
  } finally {
    deletingEvent.value = false;
  }
}
</script>

<template>
  <q-page padding>
    <!-- Error banner -->
    <q-banner
      v-if="loadError"
      dense
      class="bg-red-2 text-red-10 q-mb-md"
    >
      {{ loadError }}
    </q-banner>

    <!-- Loading state -->
    <div v-if="loading" class="q-mt-md">
      <q-spinner size="lg" />
    </div>

    <div v-else-if="completion" class="column q-gutter-md">
      <q-card flat bordered>

        <!-- Header: back + title -->
        <q-card-section class="row items-center justify-between">
          <div class="row items-center q-gutter-sm">
            <q-btn
              flat
              round
              dense
              icon="arrow_back"
              @click="goBackToSession"
            />
            <div>
              <div class="text-h6">
                {{ exerciseName }}
              </div>
              <div class="text-caption text-grey-7">
                Exercise completion #{{ completion.id }}
              </div>
            </div>
          </div>

          <div class="column items-end">
            <div class="text-caption">
              Sets: {{ totalEvents }}
            </div>
            <div v-if="createdAt" class="text-caption">
              Created:
              {{ createdAt.toLocaleDateString() }}
              {{ createdAt.toLocaleTimeString() }}
            </div>
            <div v-if="updatedAt" class="text-caption">
              Updated:
              {{ updatedAt.toLocaleDateString() }}
              {{ updatedAt.toLocaleTimeString() }}
            </div>
          </div>
        </q-card-section>

        <!-- last completion stats -->
        <q-card-section>
          <LastExerciseCompletionSummary
            :exercise="completion.exercise"
            :last-completion="lastCompletion"
            :loading="lastCompletionLoading"
            :error="lastCompletionError"
          />
        </q-card-section>

        <!-- Current sets / splits -->
        <q-card-section>
          <ExerciseEventList
            :events="completion.events"
            :loading="false"
            @edit="openEditEventDialog"
            @delete="openDeleteEventDialog"
          />
        </q-card-section>

        <!-- Actions -->
        <q-card-actions align="right" class="q-gutter-sm">
          <q-btn
            color="primary"
            label="Add Set / Split"
            @click="onAddEventClick"
          />
        </q-card-actions>

        <!-- Note editor for this completion -->
        <q-card-section>
          <NoteEditor
            v-model="completionNote"
            label="Exercise Note"
            placeholder="Add notes about how this exercise felt today..."
            @save="saveCompletionNote"
            @clear="clearCompletionNote"
          />
        </q-card-section>
      </q-card>
    </div>

    <div v-else class="q-mt-md text-caption text-grey">
      Exercise completion not found.
    </div>

    <!-- Event create/edit dialog -->
  <q-dialog v-model="eventDialogOpen">
    <q-card style="min-width: 360px">
      <q-card-section>
        <div class="text-h6">
          {{ eventDialogMode === "create" ? "Add Set / Split" : "Edit Set / Split" }}
        </div>
      </q-card-section>

      <q-card-section class="q-gutter-md">
        <div class="row q-col-gutter-md">
          <q-input
            v-if="showRepsField"
            v-model="formReps"
            type="number"
            outlined
            label="Reps"
            class="col"
            :disable="savingEvent"
          />
          <q-input
            v-if="showWeightField"
            v-model="formWeight"
            type="number"
            outlined
            label="Weight"
            class="col"
            :disable="savingEvent"
          />
        </div>

        <div class="row q-col-gutter-md">
          <q-input
            v-if="showDistanceField"
            v-model="formDistance"
            type="number"
            outlined
            label="Distance"
            class="col"
            :disable="savingEvent"
          />
          <q-input
            v-if="showDurationField"
            v-model="formDurationSeconds"
            type="number"
            outlined
            label="Duration (sec)"
            class="col"
            :disable="savingEvent"
          />
        </div>

        <q-input
          v-if="showResistanceField"
          v-model="formResistance"
          type="number"
          outlined
          label="Resistance"
          :disable="savingEvent"
        />

        <q-input
          v-if="showNoteField"
          v-model="formNote"
          outlined
          type="textarea"
          autogrow
          label="Per-set note"
          :disable="savingEvent"
        />

        <div
          v-if="eventError"
          class="text-negative text-caption"
        >
          {{ eventError }}
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn
          flat
          label="Cancel"
          v-close-popup
          :disable="savingEvent"
        />
        <q-btn
          color="primary"
          :label="eventDialogMode === 'create' ? 'Add' : 'Save'"
          :loading="savingEvent"
          @click="submitEvent"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

    <!-- Delete confirmation dialog -->
    <q-dialog v-model="deleteDialogOpen">
      <q-card style="min-width: 320px">
        <q-card-section>
          <div class="text-h6">Delete set / split?</div>
        </q-card-section>

        <q-card-section>
          <div
            v-if="deleteError"
            class="text-negative text-caption q-mt-sm"
          >
            {{ deleteError }}
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancel"
            v-close-popup
            :disable="deletingEvent"
          />
          <q-btn
            color="negative"
            label="Delete"
            :loading="deletingEvent"
            @click="confirmDeleteEvent"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>