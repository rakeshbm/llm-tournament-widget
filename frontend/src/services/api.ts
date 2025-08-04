import {
  TournamentSummary,
  CreateTournamentRequest,
  Tournament,
  VoteRequest,
  VoteResponse,
  TournamentResults,
  UserTournamentStatus,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';

export const tournamentApi = {
  fetchTournaments: async (): Promise<TournamentSummary[]> => {
    const response = await fetch(`${API_BASE}/tournaments`, {
      credentials: 'include',
    });
    if (!response.ok) {
      throw new Error('Failed to fetch tournaments');
    }
    return response.json();
  },

  createTournament: async (
    data: CreateTournamentRequest
  ): Promise<Tournament> => {
    const response = await fetch(`${API_BASE}/tournaments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'include',
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to create tournament');
    }
    return response.json();
  },

  loadTournament: async (id: number): Promise<Tournament> => {
    const response = await fetch(`${API_BASE}/tournaments/${id}`, {
      credentials: 'include',
    });
    if (!response.ok) {
      throw new Error('Failed to load tournament');
    }
    return response.json();
  },

  getTournamentStatus: async (id: number): Promise<UserTournamentStatus> => {
    const response = await fetch(`${API_BASE}/tournaments/${id}/status`, {
      credentials: 'include',
    });
    if (!response.ok) {
      throw new Error('Failed to get tournament status');
    }
    return response.json();
  },

  getTournamentResults: async (id: number): Promise<TournamentResults> => {
    const response = await fetch(`${API_BASE}/tournaments/${id}/results`, {
      credentials: 'include',
    });
    if (!response.ok) {
      throw new Error('Failed to get tournament results');
    }
    return response.json();
  },

  recordVote: async (
    tournamentId: number,
    voteData: VoteRequest
  ): Promise<VoteResponse> => {
    const response = await fetch(
      `${API_BASE}/tournaments/${tournamentId}/vote`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(voteData),
        credentials: 'include',
      }
    );
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to record vote');
    }
    return response.json();
  },
};
