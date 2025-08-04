import { useQuery } from '@tanstack/react-query';
import { tournamentApi } from '../services';
import { Tournament } from '../types';

export const useTournament = (tournamentId: number) => {
  return useQuery<Tournament>({
    queryKey: ['tournament', tournamentId],
    queryFn: () => tournamentApi.loadTournament(tournamentId),
    staleTime: 0, // Always fetch fresh data for voting updates
    refetchOnWindowFocus: true,
    enabled: !!tournamentId,
  });
};
