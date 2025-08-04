import { memo } from 'react';
import * as Styled from '../styles';

interface MatchParticipantProps {
  prompt: string;
  response: string;
  votes: number;
  totalVotes: number;
  isWinner: boolean;
  isUserChoice?: boolean;
  isBye?: boolean;
}

export const MatchParticipant = memo<MatchParticipantProps>(
  ({
    prompt,
    response,
    votes,
    totalVotes,
    isWinner,
    isUserChoice = false,
    isBye = false,
  }) => {
    if (isBye) {
      return (
        <Styled.MatchParticipant isBye isWinner={false} isUserChoice={false}>
          Bye
        </Styled.MatchParticipant>
      );
    }

    return (
      <Styled.MatchParticipant isWinner={isWinner} isUserChoice={isUserChoice}>
        <Styled.ParticipantText>
          <Styled.PromptText>{prompt}</Styled.PromptText>
          <Styled.ResponseText>{response}</Styled.ResponseText>
        </Styled.ParticipantText>
        {totalVotes > 0 && (
          <Styled.VoteCount>
            {votes} votes (
            {totalVotes > 0 ? ((votes / totalVotes) * 100).toFixed(0) : 0}%)
          </Styled.VoteCount>
        )}
      </Styled.MatchParticipant>
    );
  }
);
