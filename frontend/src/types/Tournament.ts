export interface Tournament {
  id: number;
  question: string;
  prompts: string[];
  responses: string[];
  bracket_template: Match[][];
  user_bracket: Match[][];
  user_state: UserTournamentState;
}

export interface UserTournamentState {
  current_round: number;
  current_match: number;
  completed: boolean;
  winner_prompt_index: number | null;
}

export interface Match {
  participant1: number | null;
  participant2: number | null;
  winner: number | null;
  participant1_votes?: number;
  participant2_votes?: number;
  total_votes?: number;
}

export interface TournamentSummary {
  id: number;
  question: string;
  num_prompts: number;
  created_at: string;
  total_participants: number;
  completed_participants: number;
  completion_rate: number;
}

export interface TournamentResults {
  results: PromptResult[];
  stats: TournamentStats;
}

export interface PromptResult {
  prompt: string;
  prompt_index: number;
  win_count: number;
  total_participants: number;
  win_percentage: number;
}

export interface TournamentStats {
  total_participants: number;
  completed_participants: number;
  completion_rate: number;
}

export interface UserTournamentStatus {
  participated: boolean;
  completed: boolean;
  current_round: number;
  current_match: number;
  winner_prompt_index: number | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface CreateTournamentRequest {
  question: string;
  prompts: string[];
}

export interface VoteRequest {
  round: number;
  match: number;
  winner: number;
}

export interface VoteResponse {
  user_bracket: Match[][];
  completed: boolean;
  winner_prompt_index: number | null;
  user_id: string;
}
