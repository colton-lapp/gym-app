<script lang="ts" setup>
import { computed, ref } from "vue";
import type { ExerciseEvent, Exercise,
  ExerciseCompletionSummary
 } from "src/types/types";


const props = defineProps<{
  exercise: Exercise;
  lastCompletion: ExerciseCompletionSummary | null;
  loading?: boolean;
  error?: string | null;
}>();

const isExpanded = ref(false);

const showReps = computed(() => props.exercise.track_reps ?? true);
const showWeight = computed(() => props.exercise.track_weight ?? false);
const showDistance = computed(() => props.exercise.track_distance ?? false);
const showDuration = computed(() => props.exercise.track_duration ?? false);
const showResistanceNumeric = computed(() => props.exercise.track_resistance_numeric ?? false);
const showResistanceString = computed(() => props.exercise.track_resistance_string ?? false);


const createdAt = computed<Date | null>(() => {
  if (!props.lastCompletion) return null;
  return new Date(props.lastCompletion.created_at);
});

const totalSets = computed(() => props.lastCompletion?.events?.length ?? 0);

const note =props.lastCompletion?.note 

const visibleEvents = computed<ExerciseEvent[]>(() => {
  const evts = props.lastCompletion?.events ?? [];
  if (isExpanded.value) return evts;
  return evts.slice(0, 3);
});

function formatDuration(seconds: number | null): string | null {
  if (seconds == null) return null;
  const total = Number(seconds);
  if (Number.isNaN(total)) return null;
  const minutes = Math.floor(total / 60);
  const secs = total % 60;
  if (!minutes) return `${secs}s`;
  if (!secs) return `${minutes}m`;
  return `${minutes}m ${secs}s`;
}

function formatMetrics(e: ExerciseEvent): string {
  const parts: string[] = [];

  if (showReps.value && e.reps != null) {
    parts.push(`${e.reps} reps`);
  }
  if (showWeight.value && e.weight != null) {
    parts.push(`${e.weight} wt`);
  }
  if (showDistance.value && e.distance != null) {
    parts.push(`${e.distance} dist`);
  }
  if (showDuration.value) {
    const duration = formatDuration(e.duration_seconds);
    if (duration) parts.push(duration);
  }
  if (showResistanceNumeric.value && e.resistance_numeric != null) {
    parts.push(`${e.resistance_numeric} res`);
  }
  if (showResistanceString.value && e.resistance_string != null) {
    parts.push(`${e.resistance_string} res`);
  }
  if (!parts.length) return "No metrics logged";

  return parts.join(" · ");
}
</script>

<template>
  <div>
    <div class="row items-center justify-between q-mb-xs">
      <div class="text-subtitle2">Last time you did this exercise</div>
      <q-spinner v-if="loading" size="sm" />
    </div>

    <div v-if="error" class="text-negative text-caption">
      {{ error }}
    </div>

    <div
      v-else-if="!lastCompletion || !lastCompletion.events || !lastCompletion.events.length"
      class="text-caption text-grey"
    >
      No previous completion found yet.
    </div>

    <div v-else>
      <div class="q-mb-xs">
        <div v-if="createdAt" class="text-caption text-grey-7">
          {{ createdAt.toLocaleDateString() }} · {{ createdAt.toLocaleTimeString() }}
        </div>

        <div v-if="note" class="text-caption text-grey-7">
          Note: <span class="text-italic">"{{ note }}"</span>
        </div>
    </div>
      <q-list
        dense
        bordered
        separator
        class="rounded-borders last-sets-list"
      >
        <q-item
          v-for="(ev, index) in visibleEvents"
          :key="ev.id"
        >
          <q-item-section>
            <q-item-label class="text-caption text-weight-medium">
              Set {{ index + 1 }}
            </q-item-label>
            <q-item-label class="text-caption text-grey-9">
              {{ formatMetrics(ev) }}
            </q-item-label>
          </q-item-section>
        </q-item>
      </q-list>

      <q-btn
        v-if="totalSets > 3"
        flat
        dense
        size="sm"
        class="q-mt-xs"
        @click="isExpanded = !isExpanded"
      >
        {{ isExpanded ? "Show fewer" : `Show all ${totalSets} sets` }}
      </q-btn>
    </div>
  </div>
</template>

<style scoped>
.last-sets-list .q-item__label {
  line-height: 1.2;
}
</style>