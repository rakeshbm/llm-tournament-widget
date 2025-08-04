import { useQuery } from '@tanstack/react-query';
import { TournamentSummary } from '../types';
import { tournamentApi } from '../services';

export const useTournaments = () => {
  return useQuery<TournamentSummary[], Error>({
    queryKey: ['tournaments'],
    queryFn: () => tournamentApi.fetchTournaments(),
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchOnWindowFocus: false,
  });
};
