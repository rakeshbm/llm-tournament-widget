import { useQuery } from '@tanstack/react-query';
import { tournamentApi } from '../services';
import { Tournament } from '../types';

export const useTournament = (
  tournamentId: number,
  includeResults: boolean = false
) => {
  return useQuery<Tournament>({
    queryKey: ['tournament', tournamentId, includeResults],
    queryFn: () => tournamentApi.loadTournament(tournamentId, includeResults),
    staleTime: 0, // Always fetch fresh data for voting updates
    refetchOnWindowFocus: true,
    enabled: !!tournamentId,
  });
};
