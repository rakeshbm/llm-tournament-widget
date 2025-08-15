import { useMutation, useQueryClient } from '@tanstack/react-query';
import { VoteRequest, VoteResponse } from '../types';
import { tournamentApi } from '../services';

export const useRecordVote = (tournamentId: number) => {
  const queryClient = useQueryClient();

  return useMutation<VoteResponse, Error, VoteRequest>({
    mutationFn: (voteRequest) =>
      tournamentApi.recordVote(tournamentId, voteRequest),
    onSuccess: () => {
      // Invalidate tournament data to get fresh bracket state
      queryClient.invalidateQueries({ queryKey: ['tournament', tournamentId] });
      queryClient.invalidateQueries({ queryKey: ['tournaments'] });
    },
  });
};
