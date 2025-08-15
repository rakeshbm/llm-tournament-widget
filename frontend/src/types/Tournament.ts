export interface Tournament {
  id: number;
  question: string;
  prompts: string[];
  responses: string[];
  models: string[];
  bracket_template: Match[][];
  user_bracket: Match[][];
  user_state: UserTournamentState;
  rankings?: PromptRankings[];
  stats?: TournamentStats;
}

export interface UserTournamentState {
  completed: boolean;
  winner_prompt_index: number | null;
  next_match: [number, number] | null;
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
  rankings: PromptRankings[];
  stats: TournamentStats;
}

export interface PromptRankings {
  prompt: string;
  prompt_index: number;
  model: string;
  win_count: number;
  total_participants: number;
  win_percentage: number;
}

export interface TournamentStats {
  total_participants: number;
  completed_participants: number;
  completion_rate: number;
}

export interface CreateTournamentRequest {
  question: string;
  prompts: PromptWithModel[];
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

export interface AvailableModels {
  models: Record<string, string>;
}

export interface PromptWithModel {
  text: string;
  model: string;
}

export interface MatchParticipant {
  index: number;
  prompt: string;
  response: string;
  model: string;
}

export interface NextMatch {
  round: number;
  match: number;
  participant1: MatchParticipant | null;
  participant2: MatchParticipant | null;
}
