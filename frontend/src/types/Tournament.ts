export interface Tournament {
  id: number;
  question: string;
  prompts: string[];
  responses: string[];
  bracket: Match[][];
  winner_prompt?: string;
  completed: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Match {
  participant1: number | null;
  participant2: number | null;
  winner: number | null;
}

export interface TournamentSummary {
  id: number;
  question: string;
  num_prompts: number;
  completed: boolean;
  created_at: string;
  winner_prompt?: string;
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
