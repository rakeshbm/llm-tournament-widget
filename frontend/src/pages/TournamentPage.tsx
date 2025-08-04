import { useCallback, useEffect, useState } from 'react';
import { VoteRequest } from '../types';
import { findNextVotableMatch, getMatchParticipants } from '../utils';
import { useParams } from 'react-router-dom';
import {
  TournamentResultsSection,
  TournamentBracket,
  VotingModal,
  Loader,
  TournamentHeader,
  EmptyState,
} from '../components';
import { useTournament, useTournamentResults, useRecordVote } from '../hooks';

export const TournamentPage = () => {
  const { id } = useParams<{ id: string }>();
  const tournamentId = parseInt(id || '0');

  const [isVotingModalOpen, setIsVotingModalOpen] = useState(false);
  const [userWantsToVote, setUserWantsToVote] = useState(false);

  const {
    data: tournament,
    isLoading,
    isError,
    error,
    refetch: refetchTournament,
  } = useTournament(tournamentId);

  const { data: results, refetch: refetchResults } = useTournamentResults(
    tournamentId,
    Boolean(tournament?.user_state?.completed)
  );

  const { mutate: recordVote, isPending: isVoting } =
    useRecordVote(tournamentId);

  // Only open if user wants to vote
  useEffect(() => {
    if (
      tournament?.user_state &&
      !tournament.user_state.completed &&
      !isVoting &&
      userWantsToVote
    ) {
      const nextMatch = findNextVotableMatch(tournament.user_bracket);
      const hasVotedBefore =
        tournament.user_state.current_round > 0 ||
        tournament.user_state.current_match > 0;

      if (nextMatch && !isVotingModalOpen && hasVotedBefore) {
        setIsVotingModalOpen(true);
      }
    }
  }, [tournament, isVoting, isVotingModalOpen, userWantsToVote]);

  const handleCloseVotingModal = useCallback(() => {
    setIsVotingModalOpen(false);
    setUserWantsToVote(false);
  }, []);

  const handleOpenVotingModal = useCallback(() => {
    if (tournament?.user_state && !tournament.user_state.completed) {
      const nextMatch = findNextVotableMatch(tournament.user_bracket);
      if (nextMatch) {
        setUserWantsToVote(true);
        setIsVotingModalOpen(true);
      }
    }
  }, [tournament]);

  const handleVote = useCallback(
    (winnerIndex: number) => {
      if (!tournament || isVoting) return;

      const nextMatch = findNextVotableMatch(tournament.user_bracket);
      if (!nextMatch) return;

      const voteRequest: VoteRequest = {
        round: nextMatch.round,
        match: nextMatch.match,
        winner: winnerIndex,
      };

      recordVote(voteRequest, {
        onSuccess: () => {
          refetchTournament();
          // Only refetch results if user completed voting
          if (tournament.user_state?.completed) {
            refetchResults();
          }
          setIsVotingModalOpen(false);
        },
        onError: (error) => {
          console.error('Error recording vote:', error);
          setIsVotingModalOpen(false);
        },
      });
    },
    [tournament, recordVote, isVoting, refetchTournament, refetchResults]
  );

  if (!tournamentId || isNaN(tournamentId) || !tournament || isError) {
    return (
      <EmptyState
        title="Tournament not found"
        description="We couldn’t locate a tournament with that ID. It may have been deleted, the link is incorrect, or something went wrong."
      />
    );
  }

  if (isLoading) {
    return <Loader text="Loading tournament..." />;
  }

  // Find current votable match
  const currentMatch = findNextVotableMatch(tournament.user_bracket);
  const currentMatchData = currentMatch
    ? {
        round: currentMatch.round,
        match: currentMatch.match,
        ...getMatchParticipants(
          tournament.user_bracket[currentMatch.round][currentMatch.match],
          tournament.prompts,
          tournament.responses
        ),
      }
    : null;

  return (
    <>
      <TournamentHeader
        tournament={tournament}
        onContinueVoting={handleOpenVotingModal}
      />

      {tournament.user_state?.completed && results && (
        <TournamentResultsSection results={results} />
      )}

      <TournamentBracket tournament={tournament} />

      {isVotingModalOpen &&
        currentMatchData &&
        currentMatchData.participant1 &&
        currentMatchData.participant2 && (
          <VotingModal
            tournament={tournament}
            currentMatchData={currentMatchData}
            onVote={handleVote}
            onClose={handleCloseVotingModal}
          />
        )}

      {isVoting && <Loader text="Recording your vote..." />}
    </>
  );
};
