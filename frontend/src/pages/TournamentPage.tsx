import { useCallback, useEffect, useState, useMemo } from 'react';
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
    refetch: refetchTournament,
  } = useTournament(tournamentId);

  const { data: results, refetch: refetchResults } = useTournamentResults(
    tournamentId,
    Boolean(tournament?.user_state?.completed)
  );

  const { mutate: recordVote, isPending: isVoting } =
    useRecordVote(tournamentId);

  const currentMatch = useMemo(() => {
    return tournament?.user_bracket
      ? findNextVotableMatch(tournament.user_bracket)
      : null;
  }, [tournament?.user_bracket]);

  const currentMatchData = useMemo(() => {
    if (!currentMatch || !tournament) return null;

    return {
      round: currentMatch.round,
      match: currentMatch.match,
      ...getMatchParticipants(
        tournament.user_bracket[currentMatch.round][currentMatch.match],
        tournament.prompts,
        tournament.responses
      ),
    };
  }, [currentMatch, tournament]);

  // Only open if user wants to vote
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
      tournament?.user_state &&
      !tournament.user_state.completed &&
      currentMatch
    ) {
      setUserWantsToVote(true);
      setIsVotingModalOpen(true);
    }
  }, [tournament, currentMatch]);

  const handleVote = useCallback(
    (winnerIndex: number) => {
      if (!tournament || isVoting || !currentMatch) return;

      const voteRequest: VoteRequest = {
        round: currentMatch.round,
        match: currentMatch.match,
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
    [
      tournament,
      recordVote,
      isVoting,
      currentMatch,
      refetchTournament,
      refetchResults,
    ]
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
