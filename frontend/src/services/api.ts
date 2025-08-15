import {
  Tournament,
  TournamentSummary,
  CreateTournamentRequest,
  VoteRequest,
  VoteResponse,
  AvailableModels,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';

class TournamentApi {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      credentials: 'include',
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  fetchAvailableModels = () =>
    this.request<AvailableModels>('/tournaments/models');
  fetchTournaments = () => this.request<TournamentSummary[]>('/tournaments');

  createTournament = (request: CreateTournamentRequest) =>
    this.request<Tournament>('/tournaments', {
      method: 'POST',
      body: JSON.stringify(request),
    });

  loadTournament = (tournamentId: number, includeResults = false) =>
    this.request<Tournament>(
      `/tournaments/${tournamentId}${includeResults ? '?include_results=true' : ''}`
    );

  recordVote = (tournamentId: number, voteRequest: VoteRequest) =>
    this.request<VoteResponse>(`/tournaments/${tournamentId}/vote`, {
      method: 'POST',
      body: JSON.stringify(voteRequest),
    });
}

export const tournamentApi = new TournamentApi();
