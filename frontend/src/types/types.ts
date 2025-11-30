export interface ExerciseEvent {
  id: number;
  order_index: number;
  reps: number | null;
  duration_seconds: number | null;
  weight: string | null;
  distance: string | null;
  resistance_numeric: string | null;   // backend sends decimal as string
  resistance_string: string | null;
  note: string;
  created_at: string;
  updated_at: string;
}

export interface Exercise {
  id: number;
  name: string;
  track_reps?: boolean;
  track_weight?: boolean;
  track_distance?: boolean;
  track_duration?: boolean;
  track_resistance_numeric?: boolean;
  track_resistance_string?: boolean;
  track_notes?: boolean;
  muscle_groups?: MiniLabel[];
}

export interface ExerciseCompletionSummary {
  id: number;
  exercise: Exercise;
  note: string;
  created_at: string;
  updated_at: string;
  events: ExerciseEventSummary[];
}

export interface ExerciseCompletionDetail {
  id: number;
  session: number;
  exercise: Exercise;
  note: string;
  created_at: string;
  updated_at: string;
  events: ExerciseEventSummary[];
}

export 
interface ExerciseEventPayload {
  completion: number;
  order_index: number;
  reps: number | null;
  weight: number | null;
  distance: number | null;
  duration_seconds: number | null;
  resistance_numeric: number | null;
  resistance_string: string | null;
  note: string;
}



export interface UserLocation {
  id: number;
  name: string;
  address: string;
  latitude: string | null;   // DRF decimal → string
  longitude: string | null;
  created_at: string;
  updated_at: string;
}

export interface GymSession {
  id: number;
  start_time: string;
  end_time: string | null;
  is_open: boolean;
  location: UserLocation | null;  // <--- FIXED
  location_id?: number | null;    // used only when writing
  note: string;
  exercise_completions: ExerciseCompletionSummary[];
  created_at: string;
  updated_at: string;
}

export interface ExerciseEventSummary {
  id: number;
  order_index: number;
  reps: number | null;
  duration_seconds: number | null;
  weight: string | null;
  distance: string | null;
  resistance_numeric: string | null;
  resistance_string: string | null;
  note: string;
  created_at: string;
  updated_at: string;
}

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

export interface ExerciseGroup {
  key: string;
  label: string;
  type: "muscle_group" | "tag" | "other";
  icon?: string | null;
  items: ExerciseSummary[];
}


