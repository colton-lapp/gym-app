<script lang="ts" setup>
import { computed, ref, watch } from "vue";

export interface MiniLabel {
  id: number;
  name: string;
  icon: string; // e.g. "humerus_alt" or "fitness_center"
}

export interface ExerciseSummary {
  id: number;
  name: string;
  image?: string | null;
  muscle_groups?: MiniLabel[];
  tags?: MiniLabel[];
  last_completed_at?: string | null;
}

type SortMode = "alpha" | "recent" | "muscle_groups" | "tags";

interface ExerciseGroup {
  key: string;
  label: string;
  type: "muscle_group" | "tag" | "other";
  icon?: string | null;
  items: ExerciseSummary[];
}

const props = defineProps<{
  exercises: ExerciseSummary[] | null | undefined;
  loading?: boolean;
}>();

const emit = defineEmits<{
  (e: "select", exercise: ExerciseSummary): void;
}>();

const search = ref("");
const sortMode = ref<SortMode>("alpha");

// Debug: see exactly what comes in
watch(
  () => props.exercises,
  (val) => {
    console.log("DEBUG — exercises:", JSON.parse(JSON.stringify(val)));
  },
  { immediate: true }
);

// Defensive mapping from raw icon string to q-icon name
function iconName(raw?: string | null): string {
  return raw && raw.trim().length > 0 ? raw.trim() : "help_outline";
}

// // From a MiniLabel
// function iconNameForLabel(label: MiniLabel | undefined): string {
//   return iconName(label?.icon);
// }

// Compute up to 2 icons for a given exercise:
// - prefer muscle groups first
// - then tags
function getIconsForExercise(ex: ExerciseSummary): string[] {
  const icons: string[] = [];

  ex.muscle_groups?.forEach((mg) => {
    if (mg.icon && icons.length < 2) {
      icons.push(mg.icon);
    }
  });

  ex.tags?.forEach((tag) => {
    if (tag.icon && icons.length < 2) {
      icons.push(tag.icon);
    }
  });

  return icons;
}

// Search across name, muscle groups, and tags; prioritize name matches
const filteredExercises = computed<ExerciseSummary[]>(() => {
  const list = props.exercises ?? [];
  const q = search.value.trim().toLowerCase();

  if (!q) return [...list];

  const scored: { exercise: ExerciseSummary; score: number }[] = [];

  for (const ex of list) {
    let score = 0;

    if (ex.name.toLowerCase().includes(q)) {
      score += 3;
    }

    ex.muscle_groups?.forEach((mg) => {
      if (mg.name.toLowerCase().includes(q)) {
        score += 1;
      }
    });

    ex.tags?.forEach((tag) => {
      if (tag.name.toLowerCase().includes(q)) {
        score += 1;
      }
    });

    if (score > 0) {
      scored.push({ exercise: ex, score });
    }
  }

  scored.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    return a.exercise.name.localeCompare(b.exercise.name);
  });

  return scored.map((s) => s.exercise);
});

const useGrouping = computed<boolean>(
  () => sortMode.value === "muscle_groups" || sortMode.value === "tags"
);

// Flat list for alpha / recent
const flatSortedExercises = computed<ExerciseSummary[]>(() => {
  const arr = [...filteredExercises.value];

  arr.sort((a, b) => {
    if (sortMode.value === "recent") {
      const aDate = a.last_completed_at ?? "";
      const bDate = b.last_completed_at ?? "";
      if (aDate && bDate && aDate !== bDate) {
        return aDate > bDate ? -1 : 1; // newest first
      }
      if (aDate && !bDate) return -1;
      if (!aDate && bDate) return 1;
    }

    return a.name.localeCompare(b.name);
  });

  return arr;
});

// Grouped view for muscle_groups / tags
const groupedExercises = computed<ExerciseGroup[]>(() => {
  if (!useGrouping.value) return [];

  const base = filteredExercises.value;
  const map = new Map<string, ExerciseGroup>();

  for (const ex of base) {
    const keys: {
      key: string;
      label: string;
      type: ExerciseGroup["type"];
      icon?: string | null;
    }[] = [];

    if (sortMode.value === "muscle_groups") {
      if (ex.muscle_groups && ex.muscle_groups.length) {
        ex.muscle_groups.forEach((mg) => {
          keys.push({
            key: `mg:${mg.id}`,
            label: mg.name,
            type: "muscle_group",
            icon: mg.icon,
          });
        });
      } else {
        keys.push({ key: "other", label: "Other", type: "other", icon: null });
      }
    } else if (sortMode.value === "tags") {
      if (ex.tags && ex.tags.length) {
        ex.tags.forEach((tag) => {
          keys.push({
            key: `tag:${tag.id}`,
            label: tag.name,
            type: "tag",
            icon: tag.icon,
          });
        });
      } else {
        keys.push({ key: "other", label: "Other", type: "other", icon: null });
      }
    }

    for (const k of keys) {
      let group = map.get(k.key);
      if (!group) {
        group = {
          key: k.key,
          label: k.label,
          type: k.type,
          icon: k.icon ?? null,
          items: [],
        };
        map.set(k.key, group);
      } else if (!group.icon && k.icon) {
        // if somehow group was created without icon, patch it
        group.icon = k.icon;
      }

      if (!group.items.includes(ex)) {
        group.items.push(ex);
      }
    }
  }

  const groups = Array.from(map.values());

  const typeOrder: Record<ExerciseGroup["type"], number> = {
    muscle_group: 0,
    tag: 1,
    other: 2,
  };

  groups.sort((a, b) => {
    if (a.type === b.type) {
      return a.label.localeCompare(b.label);
    }
    return typeOrder[a.type] - typeOrder[b.type];
  });

  groups.forEach((g) => {
    g.items.sort((a, b) => {
      if (sortMode.value === "recent") {
        const aDate = a.last_completed_at ?? "";
        const bDate = b.last_completed_at ?? "";
        if (aDate && bDate && aDate !== bDate) {
          return aDate > bDate ? -1 : 1;
        }
        if (aDate && !bDate) return -1;
        if (!aDate && bDate) return 1;
      }
      return a.name.localeCompare(b.name);
    });
  });

  return groups;
});

const hasExercises = computed<boolean>(() => filteredExercises.value.length > 0);

function onClick(exercise: ExerciseSummary): void {
  emit("select", exercise);
}

function formatLastCompleted(exercise: ExerciseSummary): string {
  if (!exercise.last_completed_at) {
    return "No history yet";
  }
  const d = new Date(exercise.last_completed_at);
  if (Number.isNaN(d.getTime())) {
    return "No history yet";
  }
  return `Last: ${d.toLocaleDateString()}`;
}

function groupCaption(type: ExerciseGroup["type"]): string {
  if (type === "muscle_group") return "Muscle group";
  if (type === "tag") return "Tag";
  return "Uncategorized";
}
</script>

<template>
  <div>
    <!-- Filter row -->
    <div class="row items-center q-gutter-sm q-mb-md">
      <q-input
        v-model="search"
        dense
        outlined
        placeholder="Search"
        class="col"
      />

      <!-- SORT OPTIONS INLINE BUTTONS -->
      <div class="row items-center q-gutter-xs">
        <q-btn
          flat
          size="sm"
          :color="sortMode === 'alpha' ? 'primary' : 'grey-7'"
          label="A–Z"
          @click="sortMode = 'alpha'"
        />
        <q-btn
          flat
          size="sm"
          :color="sortMode === 'recent' ? 'primary' : 'grey-7'"
          label="Recent"
          @click="sortMode = 'recent'"
        />
        <q-btn
          flat
          size="sm"
          :color="sortMode === 'muscle_groups' ? 'primary' : 'grey-7'"
          label="Muscles"
          @click="sortMode = 'muscle_groups'"
        />
        <q-btn
          flat
          size="sm"
          :color="sortMode === 'tags' ? 'primary' : 'grey-7'"
          label="Tags"
          @click="sortMode = 'tags'"
        />
      </div>
    </div>

    <div v-if="loading">
      <q-spinner size="lg" />
    </div>

    <div
      v-else-if="!hasExercises"
      class="text-caption text-grey"
    >
      No exercises found. Create one in the Exercises section.
    </div>

    <!-- Grouped view -->
    <div v-else-if="useGrouping" class="column q-gutter-sm">
      <q-expansion-item
        v-for="group in groupedExercises"
        :key="group.key"
        expand-separator
        default-open
      >
        <template #header>
          <div class="row items-center no-wrap">
            <!-- Icon on folder header (from the group label itself) -->
            <q-icon
              v-if="(group.type === 'muscle_group' || group.type === 'tag') && group.icon"
              :name="iconName(group.icon)"
              size="sm"
              class="q-mr-sm"
            />

            <div class="column">
              <span class="text-subtitle1">{{ group.label }}</span>
              <span class="text-caption">{{ groupCaption(group.type) }}</span>
            </div>
          </div>
        </template>

        <q-list bordered separator class="rounded-borders">
          <q-item
            v-for="exercise in group.items"
            :key="exercise.id"
            clickable
            @click="onClick(exercise)"
          >
            <q-item-section avatar v-if="exercise.image">
              <q-avatar square>
                <img :src="exercise.image" alt="" />
              </q-avatar>
            </q-item-section>

            <!-- Text-only rows inside grouped view -->
            <q-item-section>
              <div class="column">
                <q-item-label>{{ exercise.name }}</q-item-label>
                <q-item-label caption class="text-grey-7">
                  {{ formatLastCompleted(exercise) }}
                </q-item-label>
              </div>
            </q-item-section>

            <q-item-section side>
              <q-icon name="add" />
            </q-item-section>
          </q-item>
        </q-list>
      </q-expansion-item>
    </div>

    <!-- Flat view (alpha / recent): icons in own column, text in second column -->
    <q-list
      v-else
      bordered
      separator
      class="rounded-borders"
    >
      <q-item
        v-for="exercise in flatSortedExercises"
        :key="exercise.id"
        clickable
        @click="onClick(exercise)"
      >
        <!-- optional image column -->
        <q-item-section avatar v-if="exercise.image">
          <q-avatar square>
            <img :src="exercise.image" alt="" />
          </q-avatar>
        </q-item-section>

        <!-- icons column: mix muscle + tag icons (max 2) -->
        <q-item-section side class="q-pr-sm">
          <div class="column items-center justify-center" style="min-width: 36px;">
            <q-icon
              v-for="icon in getIconsForExercise(exercise)"
              :key="icon"
              :name="iconName(icon)"
              size="sm"
              class="q-mb-xs text-primary"
            />
          </div>
        </q-item-section>

        <!-- text column -->
        <q-item-section>
          <div class="column">
            <q-item-label>
              {{ exercise.name }}
            </q-item-label>

            <q-item-label caption class="text-grey-7">
              {{ formatLastCompleted(exercise) }}
            </q-item-label>
          </div>
        </q-item-section>

        <!-- action column -->
        <q-item-section side>
          <q-icon name="add" />
        </q-item-section>
      </q-item>
    </q-list>
  </div>
</template>