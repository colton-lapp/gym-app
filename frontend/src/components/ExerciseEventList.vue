<script lang="ts" setup>

import type { ExerciseEvent
 } from "src/types/types";


const props = defineProps<{
  events: ExerciseEvent[] | null | undefined;
  loading?: boolean;
}>();
console.log(props)

const emit = defineEmits<{
  (e: "edit", event: ExerciseEvent): void;
  (e: "delete", event: ExerciseEvent): void;
}>();

function formatDuration(seconds: number | null): string | null {
  if (!seconds && seconds !== 0) return null;
  const s = Number(seconds);
  const minutes = Math.floor(s / 60);
  const remaining = s % 60;
  return `${minutes}m ${remaining}s`;
}

function formatMetrics(e: ExerciseEvent): string {
  const parts: string[] = [];

  if (e.reps != null) parts.push(`${e.reps} reps`);
  if (e.weight != null) parts.push(`${e.weight} weight`);
  if (e.distance != null) parts.push(`${e.distance} distance`);

  const duration = formatDuration(e.duration_seconds);
  if (duration) parts.push(duration);

  if (e.resistance_numeric != null) parts.push(`${e.resistance_numeric} resistance`);
  if (e.resistance_string != null) parts.push(`${e.resistance_string} resistance`);

  return parts.length ? parts.join(" · ") : "No metrics recorded";
}

function onEdit(event: ExerciseEvent) {
  emit("edit", event);
}

function onDelete(event: ExerciseEvent) {
  emit("delete", event);
}

</script>

<template>
  <div>
    <div class="row items-center justify-between q-mb-sm">
      <div class="text-subtitle2">Sets / splits in this exercise</div>
      <q-spinner v-if="loading" size="sm" />
    </div>

    <div v-if="!events || !events.length" class="text-caption text-grey">
      No sets or splits logged yet for this exercise.
    </div>

    <q-list
      v-else
      bordered
      separator
      class="rounded-borders"
    >
      <q-item
        v-for="(e, index) in events"
        :key="e.id"
      >
        <q-item-section>
          <q-item-label class="text-body1">
            Set {{ index + 1 }}
          </q-item-label>
          <q-item-label caption>
            {{ formatMetrics(e) }}
          </q-item-label>
          <q-item-label
            v-if="e.note"
            caption
            class="ellipsis"
          >
            “{{ e.note }}”
          </q-item-label>
        </q-item-section>

        <q-item-section side top>
          <div class="column items-end">
            <q-item-label caption>
              {{ new Date(e.created_at).toLocaleTimeString() }}
            </q-item-label>
            <div class="row q-gutter-xs q-mt-xs">
              <q-btn
                dense
                flat
                size="sm"
                icon="edit"
                @click.stop="onEdit(e)"
              />
              <q-btn
                dense
                flat
                size="sm"
                color="negative"
                icon="delete"
                @click.stop="onDelete(e)"
              />
            </div>
          </div>
        </q-item-section>
      </q-item>
    </q-list>
  </div>
</template>

<style scoped>
.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>