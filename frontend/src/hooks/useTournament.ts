import { useState, useEffect } from 'react';
import { tournamentApi } from '../services';
import { Match, Tournament, TournamentSummary } from '../types';

export const useTournament = () => {
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [tournaments, setTournaments] = useState<TournamentSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentRound, setCurrentRound] = useState(0);
  const [currentMatch, setCurrentMatch] = useState(0);
  const [voteDialog, setVoteDialog] = useState(false);

  const closeVotingModal = async () => {
    setVoteDialog(false);
  };

  const openVotingModal = async () => {
    setVoteDialog(true);
  };

  const fetchTournaments = async () => {
    try {
      const data = await tournamentApi.fetchTournaments();
      setTournaments(data);
    } catch (err) {
      console.error('Error fetching tournaments:', err);
      setError('Failed to fetch tournaments');
    }
  };

  const createTournament = async (question: string, prompts: string[]) => {
    if (!question.trim()) {
      setError('Please enter a question');
      return null;
    }

    if (prompts.length < 2) {
      setError('Please add at least 2 prompts');
      return null;
    }

    if (prompts.some((p) => !p.trim())) {
      setError('Please fill in all prompts');
      return null;
    }

    setLoading(true);
    setError('');

    try {
      const data = await tournamentApi.createTournament({
        question: question.trim(),
        prompts: prompts.filter((p) => p.trim()),
      });

      setTournament(data);
      setCurrentRound(0);
      setCurrentMatch(0);

      findNextMatch(data.bracket, 0, 0);
      await fetchTournaments();

      return data;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const loadTournament = async (id: number) => {
    try {
      setLoading(true);
      setError('');

      const data = await tournamentApi.loadTournament(id);
      setTournament(data);

      if (!data.completed) {
        findNextMatch(data.bracket, 0, 0);
      } else {
        closeVotingModal();
      }

      return data;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to load tournament';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const findNextMatch = (
    bracket: Match[][],
    startRound: number,
    startMatch: number
  ) => {
    for (let round = startRound; round < bracket.length; round++) {
      for (
        let match = round === startRound ? startMatch : 0;
        match < bracket[round].length;
        match++
      ) {
        const currentMatchData = bracket[round][match];

        if (
          currentMatchData.winner === null &&
          currentMatchData.participant1 !== null &&
          currentMatchData.participant2 !== null &&
          currentMatchData.participant1 !== -1 &&
          currentMatchData.participant2 !== -1
        ) {
          setCurrentRound(round);
          setCurrentMatch(match);
          openVotingModal();
          return;
        }
      }
    }

    closeVotingModal();
  };

  const vote = async (winnerIndex: number) => {
    if (!tournament) {
      setError('No tournament active');
      return null;
    }

    try {
      const data = await tournamentApi.vote(tournament.id, {
        round: currentRound,
        match: currentMatch,
        winner: winnerIndex,
      });

      setTournament({
        ...tournament,
        bracket: data.bracket,
        completed: data.completed,
        winner_prompt: data.winner_prompt,
      });

      closeVotingModal();

      if (data.completed) {
        await fetchTournaments();
      } else {
        setTimeout(() => {
          findNextMatch(data.bracket, currentRound, currentMatch + 1);
        }, 500);
      }

      return data;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to record vote';
      setError(errorMessage);
      return null;
    }
  };

  const resetTournament = () => {
    setTournament(null);
    setError('');
    closeVotingModal();
    setCurrentRound(0);
    setCurrentMatch(0);
  };

  const getCurrentMatchData = () => {
    if (!tournament || !tournament.bracket[currentRound]) {
      return null;
    }
    return tournament.bracket[currentRound][currentMatch];
  };

  const getTournamentProgress = () => {
    if (!tournament) return 0;

    let totalMatches = 0;
    let completedMatches = 0;

    tournament.bracket.forEach((round) => {
      round.forEach((match) => {
        totalMatches++;
        if (match.winner !== null) {
          completedMatches++;
        }
      });
    });

    return totalMatches > 0
      ? Math.round((completedMatches / totalMatches) * 100)
      : 0;
  };

  const clearError = () => {
    setError('');
  };

  useEffect(() => {
    fetchTournaments();
  }, []);

  return {
    tournament,
    tournaments,
    loading,
    error,
    currentRound,
    currentMatch,
    voteDialog,
    createTournament,
    loadTournament,
    vote,
    resetTournament,
    fetchTournaments,
    clearError,
    getCurrentMatchData,
    getTournamentProgress,
    closeVotingModal,
    openVotingModal,
  };
};
