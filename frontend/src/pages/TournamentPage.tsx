import { useCallback, useEffect, useState, useMemo } from 'react';
import { VoteRequest } from '../types';
import { findNextVotableMatch, getCurrentMatchFromState } from '../utils';
import { useParams } from 'react-router-dom';
import {
  TournamentResultsSection,
  TournamentBracket,
  VotingModal,
  Loader,
  TournamentHeader,
  EmptyState,
} from '../components';
import { useTournament, useRecordVote } from '../hooks';

export const TournamentPage = () => {
  const { id } = useParams<{ id: string }>();
  const tournamentId = parseInt(id || '0');

  const [isVotingModalOpen, setIsVotingModalOpen] = useState(false);
  const [userWantsToVote, setUserWantsToVote] = useState(false);

  const {
    data: tournament,
    isLoading,
    isError,
    refetch: refetchTournament,
  } = useTournament(tournamentId, true);

  const { mutate: recordVote, isPending: isVoting } =
    useRecordVote(tournamentId);

  const currentMatch = useMemo(() => {
    if (!tournament) return null;

    if (tournament.user_state.next_match) {
      const match = getCurrentMatchFromState(
        tournament.user_state.next_match,
        tournament.user_bracket,
        tournament.prompts,
        tournament.responses,
        tournament.models
      );

      if (match) {
        return match;
      }
    }

    const nextVotableMatch = findNextVotableMatch(tournament.user_bracket);

    if (nextVotableMatch) {
      const match = getCurrentMatchFromState(
        [nextVotableMatch.round, nextVotableMatch.match],
        tournament.user_bracket,
        tournament.prompts,
        tournament.responses,
        tournament.models
      );

      return match;
    }

    return null;
  }, [tournament]);

  useEffect(() => {
    if (
      tournament?.user_state &&
      !tournament.user_state.completed &&
      !isVoting &&
      userWantsToVote &&
      currentMatch &&
      !isVotingModalOpen
    ) {
      setIsVotingModalOpen(true);
    }
  }, [tournament, isVoting, isVotingModalOpen, userWantsToVote, currentMatch]);

  const handleCloseVotingModal = useCallback(() => {
    setIsVotingModalOpen(false);
    setUserWantsToVote(false);
  }, []);

  const handleOpenVotingModal = useCallback(() => {
    if (
      !tournament?.user_state ||
      tournament.user_state.completed ||
      !currentMatch
    ) {
      return;
    }

    setUserWantsToVote(true);
    setIsVotingModalOpen(true);
  }, [tournament, currentMatch]);

  const handleVote = useCallback(
    (winnerIndex: number) => {
      if (!tournament || isVoting || !currentMatch) {
        return;
      }

      const voteRequest: VoteRequest = {
        round: currentMatch.round,
        match: currentMatch.match,
        winner: winnerIndex,
      };

      recordVote(voteRequest, {
        onSuccess: () => {
          refetchTournament();
          setIsVotingModalOpen(false);
        },
        onError: (error) => {
          console.error('Error recording vote:', error);
          setIsVotingModalOpen(false);
        },
      });
    },
    [tournament, recordVote, isVoting, currentMatch, refetchTournament]
  );

  if (isLoading) {
    return <Loader text="Loading tournament..." />;
  }

  if (!tournamentId || isNaN(tournamentId) || !tournament || isError) {
    return (
      <EmptyState
        title="Tournament not found"
        description="We couldn't locate a tournament with that ID. It may have been deleted, the link is incorrect, or something went wrong."
      />
    );
  }

  return (
    <>
      <TournamentHeader
        tournament={tournament}
        onContinueVoting={handleOpenVotingModal}
      />

      {tournament.user_state?.completed &&
        tournament.rankings &&
        tournament.stats && (
          <TournamentResultsSection
            results={{ rankings: tournament.rankings, stats: tournament.stats }}
          />
        )}

      <TournamentBracket tournament={tournament} />

      {isVotingModalOpen && currentMatch && (
        <VotingModal
          tournament={tournament}
          currentMatchData={currentMatch}
          onVote={handleVote}
          onClose={handleCloseVotingModal}
        />
      )}

      {isVoting && <Loader text="Recording your vote..." />}
    </>
  );
};
