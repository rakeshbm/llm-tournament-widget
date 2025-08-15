import { useQuery } from '@tanstack/react-query';
import { AvailableModels } from '../types';
import { tournamentApi } from '../services';

export const useAvailableModels = () => {
  return useQuery<AvailableModels, Error>({
    queryKey: ['models'],
    queryFn: tournamentApi.fetchAvailableModels,
    staleTime: 1000 * 60 * 30, // 30 minutes
    refetchOnWindowFocus: false,
  });
};
