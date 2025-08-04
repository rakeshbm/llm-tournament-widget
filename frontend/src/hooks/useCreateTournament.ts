import { useMutation, useQueryClient } from '@tanstack/react-query';
import { CreateTournamentRequest, Tournament } from '../types';
import { tournamentApi } from '../services';

export const useCreateTournament = () => {
  const queryClient = useQueryClient();

  return useMutation<Tournament, Error, CreateTournamentRequest>({
    mutationFn: (createTournamentRequest) =>
      tournamentApi.createTournament(createTournamentRequest),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tournaments'] });
    },
  });
};
