import { useQuery } from '@tanstack/react-query';
import { tournamentApi } from '../services';
import { TournamentResults } from '../types';

export const useTournamentResults = (
  tournamentId: number,
  enabled: boolean = true
) => {
  return useQuery<TournamentResults>({
    queryKey: ['tournament-results', tournamentId],
    queryFn: () => tournamentApi.getTournamentResults(tournamentId),
    staleTime: 30 * 1000, // 30 seconds
    enabled: enabled && !!tournamentId,
  });
};
