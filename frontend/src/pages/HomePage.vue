<script lang="ts" setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "src/stores/auth";
import NoteEditor from "src/components/NoteEditor.vue";
import SessionExerciseList, {
  type ExerciseCompletionSummary,
} from "src/components/SessionExerciseList.vue";
import { api } from "src/boot/axios";

interface GymSession {
  id: number;
  start_time: string;
  end_time: string | null;
  is_open: boolean;
  location: string;
  note: string;
  exercise_completions: ExerciseCompletionSummary[];
  created_at: string;
  updated_at: string;
}

const router = useRouter();
const auth = useAuthStore();

// state
const loading = ref(true);
const currentSession = ref<GymSession | null>(null);
const hasNoCurrentSession = ref(false);
const loadError = ref<string | null>(null);

// last closed session
const lastSession = ref<GymSession | null>(null);

// note editor state for current session
const sessionNote = ref<string>("");

// helpers
function parseIsoToDate(value: string | null | undefined): Date | null {
  if (!value) return null;
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return null;
  return d;
}

// initial load
onMounted(async () => {
  await fetchCurrentSession();
  if (hasNoCurrentSession.value) {
    await fetchLastSession();
  }
  loading.value = false;
});

async function fetchCurrentSession(): Promise<void> {
  loadError.value = null;
  hasNoCurrentSession.value = false;

  try {
    const res = await api.get<GymSession>("sessions/current/");
    currentSession.value = res.data;
  } catch (err: unknown) {
    const axiosErr = err as { response?: { status?: number } };
    console.log(err);

    if (axiosErr.response?.status === 404) {
      hasNoCurrentSession.value = true;
      currentSession.value = null;
    } else {
      loadError.value = "Failed to load session information.";
    }
  }
}

// load most recent closed session (for "last session" summary)
async function fetchLastSession(): Promise<void> {
  try {
    const res = await api.get<GymSession[]>("sessions/");
    const sessions = res.data;
    const closed = sessions.find((session) => session.end_time !== null);
    if (closed) {
      lastSession.value = closed;
    }
  } catch {
    // non-fatal; ignore
  }
}

// create new session
async function startSession(): Promise<void> {
  loadError.value = null;

  try {
    await api.post("sessions/");
    await fetchCurrentSession();
    if (hasNoCurrentSession.value) {
      await fetchLastSession();
    }
  } catch (err: unknown) {
    loadError.value = "Failed to start a new session.";
    console.error(err);
  }
}

// end current session
async function endSession(): Promise<void> {
  const session = currentSession.value;
  if (!session) return;

  loadError.value = null;

  const url = `sessions/${session.id}/close/`;
  console.log("Closing session with data:", session);
  console.log("Request URL:", url);

  try {
    const res = await api.post<GymSession>(url);
    lastSession.value = res.data;
    currentSession.value = null;
    hasNoCurrentSession.value = true;
    sessionNote.value = "";
  } catch (err: unknown) {
    console.log("Close session error:", err);
    loadError.value = "Failed to end the current session.";
  }
}

// reopen last session
async function reopenLastSession(): Promise<void> {
  if (!lastSession.value) return;

  loadError.value = null;

  try {
    const res = await api.post<GymSession>(
      `sessions/${lastSession.value.id}/reopen/`
    );
    currentSession.value = res.data;
    hasNoCurrentSession.value = false;
    sessionNote.value = currentSession.value.note ?? "";
  } catch (err: unknown) {
    loadError.value = "Failed to reopen the last session.";
    console.log(err);
  }
}

// keep local note editor in sync with current session
watch(
  currentSession,
  (session) => {
    sessionNote.value = session?.note ?? "";
  },
  { immediate: true }
);

// save / clear note on session
async function saveSessionNote(): Promise<void> {
  const session = currentSession.value;
  if (!session) return;

  loadError.value = null;

  const url = `sessions/${session.id}/`;
  console.log("Saving note for session:", session);
  console.log("Request URL:", url, "payload:", { note: sessionNote.value });

  try {
    const res = await api.patch<GymSession>(url, { note: sessionNote.value });
    currentSession.value = res.data;
  } catch (err: unknown) {
    console.log("Save note error:", err);
    loadError.value = "Failed to save session note.";
  }
}

async function clearSessionNote(): Promise<void> {
  sessionNote.value = "";
  await saveSessionNote();
}

// derived values
const sessionStartDate = computed<Date | null>(() =>
  currentSession.value ? parseIsoToDate(currentSession.value.start_time) : null
);

const durationMinutes = computed<number | null>(() => {
  const start = sessionStartDate.value;
  if (!start) return null;
  const diffMs = Date.now() - start.getTime();
  const diffMinutes = diffMs / 1000 / 60;
  return Math.max(0, Math.round(diffMinutes));
});

const completedExerciseCount = computed<number>(() => {
  const session = currentSession.value;
  if (!session || !Array.isArray(session.exercise_completions)) return 0;
  return session.exercise_completions.length;
});

const lastSessionStartDate = computed<Date | null>(() =>
  lastSession.value ? parseIsoToDate(lastSession.value.start_time) : null
);

const lastSessionEndDate = computed<Date | null>(() =>
  lastSession.value ? parseIsoToDate(lastSession.value.end_time) : null
);

const lastSessionRelativeText = computed<string>(() => {
  if (!lastSessionEndDate.value) return "You have no previous sessions yet.";

  const end = lastSessionEndDate.value;
  const diffMs = Date.now() - end.getTime();
  const diffMinutes = Math.round(diffMs / 1000 / 60);

  if (diffMinutes < 1) return "Last session was just now.";
  if (diffMinutes < 60) return `Last session was ${diffMinutes} minutes ago.`;

  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours < 24) return `Last session was about ${diffHours} hours ago.`;

  const diffDays = Math.round(diffHours / 24);
  return `Last session was ${diffDays} day${diffDays === 1 ? "" : "s"} ago.`;
});

console.log(router);

async function goToExercisePicker(): Promise<void> {
  const session = currentSession.value;
  if (!session) return;

  // Route: /exercises?sessionId=<id>
  await router.push({
    path: "/exercises",
    query: { sessionId: String(session.id) },
  });
}
</script>

<template>
  <q-page class="q-pa-lg">

    <!-- Top welcome line -->
    <h2 class="text-h4 q-mb-md">
      Welcome {{ auth.user?.first_name }}
    </h2>

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

    <!-- Active session present -->
    <div v-else-if="currentSession" class="column q-gutter-md">

      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6 q-mb-xs">Active Session</div>

          <div v-if="sessionStartDate">
            Started:
            {{ sessionStartDate.toLocaleDateString() }}
            {{ sessionStartDate.toLocaleTimeString() }}
          </div>

          <div v-if="durationMinutes !== null">
            Time elapsed: {{ durationMinutes }} minutes
          </div>

          <div class="q-mt-xs">
            Location:
            <span v-if="currentSession.location">
              {{ currentSession.location }}
            </span>
            <span v-else class="text-grey">
              not set
            </span>
          </div>

          <div class="q-mt-xs">
            Exercises so far: {{ completedExerciseCount }}
          </div>
        </q-card-section>

        <!-- exercise list -->
        <q-card-section>
          <SessionExerciseList
            :completions="currentSession.exercise_completions"
            :loading="loading"
          />
        </q-card-section>

        <q-card-actions align="between" class="q-gutter-sm">
          <div>
            <q-btn
              color="primary"
              label="Add Exercise to Session"
              @click="goToExercisePicker"
            />
          </div>
        </q-card-actions>
        <!-- Note editor -->
        <q-card-section>
          <NoteEditor
            v-model="sessionNote"
            label="Session Note"
            placeholder="Add a note about this session..."
            @save="saveSessionNote"
            @clear="clearSessionNote"
          />
        </q-card-section>
        
          <div>
            <q-btn
              label="End Session"
              color="negative"
              flat
              @click="endSession"
            />
          </div>
          
      </q-card>
    </div>

    <!-- No active session -->
    <div v-else-if="hasNoCurrentSession" class="column q-gutter-md">

      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6 q-mb-xs">No active session</div>

          <div class="text-body2 q-mb-sm">
            Start a new session to begin logging your workout, or reopen a previous one.
          </div>

          <div class="text-caption">
            {{ lastSessionRelativeText }}
          </div>

          <div v-if="lastSessionStartDate" class="text-caption q-mt-xs">
            Last session started:
            {{ lastSessionStartDate.toLocaleDateString() }}
            {{ lastSessionStartDate.toLocaleTimeString() }}
          </div>

          <div v-if="lastSession?.location" class="text-caption q-mt-xs">
            Location: {{ lastSession.location }}
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            color="positive"
            label="Start Session"
            @click="startSession"
          />
          <q-btn
            color="secondary"
            outline
            label="Reopen Previous"
            :disable="!lastSession"
            @click="reopenLastSession"
          />
        </q-card-actions>
      </q-card>

    </div>

  </q-page>
</template>