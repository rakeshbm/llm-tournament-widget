import { Match } from '../types';

export const calculateTournamentProgress = (
  userBracket: Match[][],
  isCompleted: boolean
): number => {
  if (isCompleted) return 100;

  let totalMatches = 0;
  let completedMatches = 0;

  userBracket.forEach((round) => {
    round.forEach((match) => {
      // Count matches that need voting (both participants present and not -1)
      if (
        match.participant1 !== null &&
        match.participant1 !== -1 &&
        match.participant2 !== null &&
        match.participant2 !== -1
      ) {
        totalMatches++;

        // Check if this match has been voted on
        if (match.winner !== null) {
          completedMatches++;
        }
      }
    });
  });

  if (totalMatches === 0) return 0;
  return Math.round((completedMatches / totalMatches) * 100);
};

export const getRoundDisplayName = (
  roundIndex: number,
  totalRounds: number
): string => {
  if (roundIndex === totalRounds - 1) return 'Final';
  if (roundIndex === totalRounds - 2) return 'Semi-Final';
  if (roundIndex === totalRounds - 3) return 'Quarter-Final';
  return `Round ${roundIndex + 1}`;
};

export const findNextVotableMatch = (
  userBracket: Match[][]
): { round: number; match: number } | null => {
  for (let roundIndex = 0; roundIndex < userBracket.length; roundIndex++) {
    const round = userBracket[roundIndex];

    for (let matchIndex = 0; matchIndex < round.length; matchIndex++) {
      const match = round[matchIndex];

      // Check if this match needs voting
      if (
        match.participant1 !== null &&
        match.participant1 !== -1 &&
        match.participant2 !== null &&
        match.participant2 !== -1 &&
        match.winner === null
      ) {
        return { round: roundIndex, match: matchIndex };
      }
    }
  }

  return null; // No votable matches found
};

export const getMatchParticipants = (
  match: Match,
  prompts: string[],
  responses: string[]
): {
  participant1: { index: number; prompt: string; response: string } | null;
  participant2: { index: number; prompt: string; response: string } | null;
} => {
  const getParticipant = (index: number | null) => {
    if (index === null || index === -1 || index >= prompts.length) {
      return null;
    }
    return {
      index,
      prompt: prompts[index] || 'N/A',
      response: responses[index] || 'N/A',
    };
  };

  return {
    participant1: getParticipant(match.participant1),
    participant2: getParticipant(match.participant2),
  };
};
