<script lang="ts" setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import type { ExerciseCompletionSummary
 } from "src/types/types";



const props = defineProps<{
  completions: ExerciseCompletionSummary[] | null | undefined;
  loading?: boolean;
}>();

const router = useRouter();

const sortedCompletions = computed<ExerciseCompletionSummary[]>(() => {
  if (!props.completions) return [];
  return [...props.completions].sort((a, b) => {
    const aKey = getSortKey(a);
    const bKey = getSortKey(b);
    return bKey - aKey;
  });
});

function getSortKey(c: ExerciseCompletionSummary): number {
  const source = c.updated_at || c.created_at;
  const d = new Date(source);
  return d.getTime() || 0;
}

function totalEvents(c: ExerciseCompletionSummary): number {
  return Array.isArray(c.events) ? c.events.length : 0;
}

function formatTimeAgo(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";

  const diffMs = Date.now() - d.getTime();
  const diffMinutes = Math.round(diffMs / 1000 / 60);

  if (diffMinutes < 1) return "just now";
  if (diffMinutes < 60) return `${diffMinutes} min${diffMinutes === 1 ? "" : "s"} ago`;

  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours} hr${diffHours === 1 ? "" : "s"} ago`;

  const diffDays = Math.round(diffHours / 24);
  return `${diffDays} day${diffDays === 1 ? "" : "s"} ago`;
}

async function goToCompletion(id: number): Promise<void> {
  await router.push(`/exercise-completion/${id}`);
}
</script>

<template>
  <div>
    <div class="row items-center justify-between q-mb-sm">
      <div class="text-subtitle2">Exercises in this session</div>
      <q-spinner v-if="loading" size="sm" />
    </div>

    <div v-if="!sortedCompletions.length" class="text-caption text-grey">
      No exercises have been logged in this session yet.
    </div>

    <q-list
      v-else
      bordered
      separator
      class="rounded-borders"
    >
      <q-item
      v-for="c in sortedCompletions"
      :key="c.id"
      clickable
      @click="goToCompletion(c.id)"
    >

      <!-- ICONS HERE -->
      <q-item-section side class="q-pr-sm">
        <div class="column items-center" style="min-width:36px;">
          <q-icon
            v-for="mg in (c.exercise.muscle_groups || []).slice(0,2)"
            :key="'mg-'+mg.id"
            :name="mg.icon"
            size="sm"
            class="q-mb-xs text-primary"
          />
        </div>
      </q-item-section>

      <q-item-section>
        <q-item-label class="text-body1">
          {{ c.exercise?.name || "Exercise" }}
        </q-item-label>

        <q-item-label caption>
          Last updated: {{ formatTimeAgo(c.updated_at || c.created_at) }}
          · Sets: {{ totalEvents(c) }}
        </q-item-label>

        <q-item-label v-if="c.note" caption class="ellipsis">
          “{{ c.note }}”
        </q-item-label>
      </q-item-section>

      <q-item-section side>
        <q-icon name="chevron_right" />
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