import { memo } from 'react';
import * as Styled from '../styles';
import { Match } from '../types';
import { MatchParticipant } from './MatchParticipant';

interface BracketMatchProps {
  match: Match;
  getPromptResponse: (index: number) => {
    prompt: string;
    response: string;
    model: string;
  };
}

export const BracketMatch = memo<BracketMatchProps>(
  ({ match, getPromptResponse }) => {
    const participant1Data =
      match.participant1 !== null && match.participant1 !== -1
        ? getPromptResponse(match.participant1)
        : null;

    const participant2Data =
      match.participant2 !== null && match.participant2 !== -1
        ? getPromptResponse(match.participant2)
        : null;

    const totalVotes =
      (match.participant1_votes || 0) + (match.participant2_votes || 0);

    return (
      <Styled.CompetitionMatch>
        <Styled.MatchContainer>
          {participant1Data ? (
            <MatchParticipant
              prompt={participant1Data.prompt}
              response={participant1Data.response}
              model={participant1Data.model}
              votes={match.participant1_votes || 0}
              totalVotes={totalVotes}
              isWinner={match.winner === match.participant1}
              isUserChoice={match.winner === match.participant1}
            />
          ) : (
            <MatchParticipant
              prompt=""
              response=""
              model=""
              votes={0}
              totalVotes={0}
              isWinner={false}
              isBye={true}
            />
          )}

          {participant2Data ? (
            <MatchParticipant
              prompt={participant2Data.prompt}
              response={participant2Data.response}
              model={participant2Data.model}
              votes={match.participant2_votes || 0}
              totalVotes={totalVotes}
              isWinner={match.winner === match.participant2}
              isUserChoice={match.winner === match.participant2}
            />
          ) : (
            <MatchParticipant
              prompt=""
              response=""
              model=""
              votes={0}
              totalVotes={0}
              isWinner={false}
              isBye={true}
            />
          )}
        </Styled.MatchContainer>
      </Styled.CompetitionMatch>
    );
  }
);

BracketMatch.displayName = 'BracketMatch';
