import { TournamentSummary, CreateTournamentRequest, Tournament, VoteRequest } from "../types";

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:5000/api';

export const tournamentApi = {
  fetchTournaments: async (): Promise<TournamentSummary[]> => {
    const response = await fetch(`${API_BASE}/tournaments`);
    if (!response.ok) {
      throw new Error('Failed to fetch tournaments');
    }
    return response.json();
  },

  createTournament: async (data: CreateTournamentRequest): Promise<Tournament> => {
    const response = await fetch(`${API_BASE}/tournaments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to create tournament');
    }
    return response.json();
  },

  loadTournament: async (id: number): Promise<Tournament> => {
    const response = await fetch(`${API_BASE}/tournaments/${id}`);
    if (!response.ok) {
      throw new Error('Failed to load tournament');
    }
    return response.json();
  },

  vote: async (tournamentId: number, voteData: VoteRequest) => {
    const response = await fetch(`${API_BASE}/tournaments/${tournamentId}/vote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(voteData)
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to record vote');
    }
    return response.json();
  }
};
