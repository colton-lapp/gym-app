<script lang="ts" setup>
import { ref, computed, watch } from "vue";
import { api } from "src/boot/axios";
import type { UserLocation } from "src/types/types";

interface Props {
  sessionId: number;
  initialLocation: UserLocation | null ;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: "updated", location: UserLocation | null): void;
}>();

const locations = ref<UserLocation[]>([]);
const locationsLoading = ref(false);
const locationsError = ref<string | null>(null);

const dialogOpen = ref(false);
const saving = ref(false);
const saveError = ref<string | null>(null);

// selection
const selectedLocationId = ref<number | null>(null);

// new-location mode
const newLocationMode = ref(false);
const newName = ref("");
const newAddress = ref("");
const newLatitude = ref<string>("");
const newLongitude = ref<string>("");

const currentLocation = ref<UserLocation | null>(props.initialLocation);

watch(
  () => props.initialLocation,
  (val) => {
    currentLocation.value = val;
  }
);

const hasLocations = computed<boolean>(() => locations.value.length > 0);

async function loadLocations(): Promise<void> {
  locationsLoading.value = true;
  locationsError.value = null;

  try {
    const res = await api.get<UserLocation[]>("locations/");
    locations.value = res.data;

        if (!newLocationMode.value) {
        if (currentLocation.value?.id) {
            selectedLocationId.value = currentLocation.value.id;
        } else if (locations.value.length > 0) {
            selectedLocationId.value = locations.value[0]?.id ?? null;
        } else {
            selectedLocationId.value = null;
        }
        }
  } catch (err) {
    console.error(err);
    locationsError.value = "Failed to load locations.";
  } finally {
    locationsLoading.value = false;
  }
}

function openDialog(): void {
  dialogOpen.value = true;
  newLocationMode.value = false;
  newName.value = "";
  newAddress.value = "";
  newLatitude.value = "";
  newLongitude.value = "";
  saveError.value = null;
  void loadLocations();
}

function startNewLocation(): void {
  newLocationMode.value = true;
  selectedLocationId.value = null;
  saveError.value = null;
}

function cancelNewLocation(): void {
  newLocationMode.value = false;
  newName.value = "";
  newAddress.value = "";
  newLatitude.value = "";
  newLongitude.value = "";

  // restore selection based on current location or most recent
    if (currentLocation.value?.id) {
    selectedLocationId.value = currentLocation.value.id;
    } else if (locations.value.length > 0) {
    selectedLocationId.value = locations.value[0]?.id ?? null;
    } else {
    selectedLocationId.value = null;
    }
}

async function saveSelection(): Promise<void> {
  saveError.value = null;
  saving.value = true;

  try {
    let locationIdToUse: number | null = selectedLocationId.value;

    if (newLocationMode.value) {
      if (!newName.value.trim()) {
        saveError.value = "Name is required.";
        saving.value = false;
        return;
      }

      const payload: {
        name: string;
        address: string;
        latitude: string | null;
        longitude: string | null;
      } = {
        name: newName.value.trim(),
        address: newAddress.value.trim(),
        latitude: newLatitude.value.trim() || null,
        longitude: newLongitude.value.trim() || null,
      };

      const res = await api.post<UserLocation>("locations/", payload);
      const created = res.data;
      locations.value.unshift(created);
      locationIdToUse = created.id;
      selectedLocationId.value = created.id;
    }

    if (locationIdToUse == null) {
      // no selection means clear location on session
      await api.patch(`sessions/${props.sessionId}/`, {
        location_id: null,
      });
      currentLocation.value = null;
      emit("updated", null);
      dialogOpen.value = false;
      return;
    }

    // update session with chosen location
    const sessionRes = await api.patch<{ location: UserLocation }>(
      `sessions/${props.sessionId}/`,
      {
        location_id: locationIdToUse,
      }
    );

    currentLocation.value = sessionRes.data.location;
    emit("updated", currentLocation.value);
    dialogOpen.value = false;
  } catch (err) {
    console.error(err);
    saveError.value = "Failed to save location.";
  } finally {
    saving.value = false;
  }
}

async function clearLocation(): Promise<void> {
  saveError.value = null;
  saving.value = true;

  try {
    await api.patch(`sessions/${props.sessionId}/`, {
      location_id: null,
    });
    currentLocation.value = null;
    emit("updated", null);
  } catch (err) {
    console.error(err);
    saveError.value = "Failed to clear location.";
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div class="row items-center q-gutter-sm">
    <div class="col">
      <div v-if="currentLocation">
        <div class="text-body2">
          Location: <strong>{{ currentLocation!.name }}</strong>
        </div>
        <div v-if="currentLocation.address" class="text-caption text-grey-7">
          {{ currentLocation.address }}
        </div>
      </div>
      <div v-else class="text-caption text-grey-7">
        No location set
      </div>
    </div>

    <div class="row items-center q-gutter-xs">
      <q-btn
        flat
        dense
        round
        icon="edit_location_alt"
        @click="openDialog"
      />
      <q-btn
        v-if="currentLocation"
        flat
        dense
        round
        icon="delete"
        color="negative"
        :loading="saving"
        @click="clearLocation"
      />
      <q-btn
        v-else
        flat
        dense
        round
        icon="add_location_alt"
        @click="openDialog"
      />
    </div>

    <q-dialog v-model="dialogOpen">
      <q-card style="min-width: 360px">
        <q-card-section>
          <div class="text-h6">Select location</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <div v-if="locationsError" class="text-negative text-caption">
            {{ locationsError }}
          </div>

          <!-- select existing -->
          <div v-if="!newLocationMode">
            <q-select
              v-model="selectedLocationId"
              :options="
                locations.map((loc) => ({
                  label: loc.address
                    ? `${loc.name} – ${loc.address}`
                    : loc.name,
                  value: loc.id,
                }))
              "
              emit-value
              map-options
              outlined
              label="Saved locations"
              :loading="locationsLoading"
              :clearable="hasLocations"
              hint="Most recent at top"
            />

            <q-btn
              class="q-mt-md"
              flat
              icon="add"
              label="Add new location"
              @click="startNewLocation"
            />
          </div>

          <!-- new location form -->
          <div v-else class="column q-gutter-sm">
            <q-input
              v-model="newName"
              outlined
              label="Location name"
              :disable="saving"
              autofocus
            />
            <q-input
              v-model="newAddress"
              outlined
              label="Address (optional)"
              :disable="saving"
            />
            <div class="row q-col-gutter-md">
              <q-input
                v-model="newLatitude"
                outlined
                label="Latitude (optional)"
                class="col"
                :disable="saving"
              />
              <q-input
                v-model="newLongitude"
                outlined
                label="Longitude (optional)"
                class="col"
                :disable="saving"
              />
            </div>

            <div class="row justify-between q-mt-sm">
              <q-btn
                flat
                label="Use existing location instead"
                icon="arrow_back"
                @click="cancelNewLocation"
                :disable="saving"
              />
            </div>
          </div>

          <div v-if="saveError" class="text-negative text-caption q-mt-sm">
            {{ saveError }}
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancel"
            v-close-popup
            :disable="saving"
          />
          <q-btn
            color="primary"
            label="Save"
            :loading="saving"
            @click="saveSelection"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>