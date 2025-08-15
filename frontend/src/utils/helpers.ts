import { Match, MatchParticipant, NextMatch } from '../types';

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
  if (!userBracket || userBracket.length === 0) {
    return null;
  }

  for (let roundIndex = 0; roundIndex < userBracket.length; roundIndex++) {
    const round = userBracket[roundIndex];

    for (let matchIndex = 0; matchIndex < round.length; matchIndex++) {
      const match = round[matchIndex];

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

  return null;
};

export const getMatchParticipants = (
  match: Match,
  prompts: string[],
  responses: string[],
  models: string[]
): {
  participant1: MatchParticipant | null;
  participant2: MatchParticipant | null;
} => {
  const getParticipant = (index: number | null): MatchParticipant | null => {
    if (index === null || index === -1 || index >= prompts.length) {
      return null;
    }
    return {
      index,
      prompt: prompts[index] || 'N/A',
      response: responses[index] || 'N/A',
      model: models[index] || 'N/A',
    };
  };

  return {
    participant1: getParticipant(match.participant1),
    participant2: getParticipant(match.participant2),
  };
};

export const getCurrentMatchFromState = (
  nextMatch: [number, number] | null,
  userBracket: Match[][],
  prompts: string[],
  responses: string[],
  models: string[]
): NextMatch | null => {
  if (!nextMatch) return null;

  const [round, match] = nextMatch;
  if (round >= userBracket.length || match >= userBracket[round].length) {
    return null;
  }

  const matchData = userBracket[round][match];
  const participants = getMatchParticipants(
    matchData,
    prompts,
    responses,
    models
  );

  return {
    round,
    match,
    participant1: participants.participant1,
    participant2: participants.participant2,
  };
};
