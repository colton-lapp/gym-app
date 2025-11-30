<script lang="ts" setup>
import { computed } from "vue";

interface Props {
  modelValue: string;
  label?: string;
  placeholder?: string;
  saving?: boolean;
  canClear?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  label: "Note",
  placeholder: "Add a note...",
  saving: false,
  canClear: true,
});

const emit = defineEmits<{
  (e: "update:modelValue", value: string): void;
  (e: "save"): void;
  (e: "clear"): void;
}>();

const internalValue = computed({
  get: () => props.modelValue,
  set: (value: string) => emit("update:modelValue", value),
});

function onClear(): void {
  emit("update:modelValue", "");
  emit("clear");
}

function onSave(): void {
  emit("save");
}
</script>

<template>
  <div style="max-width:400px">
    <div class="row justify-between  q-mb-sm q-mt-md">
    <div class="text-subtitle2">
      {{ label }}
    </div>
        <div class="row justify-end">
          <q-btn
            label="Save"
            size="sm"
            color="primary"
            :loading="saving"
            @click="onSave"
          />
          <q-btn
            v-if="canClear"
            flat
            size="sm"
            label="Clear"
            color="negative"
            :disable="!internalValue"
            @click="onClear"
          />
        </div>
    </div>

    <q-input
      v-model="internalValue"
      type="textarea"
      autogrow
      outlined
      :placeholder="placeholder"

    />

  </div>
</template>