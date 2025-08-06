import { memo } from 'react';
import * as Styled from '../styles';
import { MatchParticipant } from './MatchParticipant';
import { Match } from '../types';

interface BracketMatchProps {
  match: Match;
  getPromptResponse: (index: number) => { prompt: string; response: string };
}

export const BracketMatch = memo<BracketMatchProps>(
  ({ match, getPromptResponse }) => {
    return (
      <Styled.CompetitionMatch>
        <Styled.MatchContainer>
          {match.participant1 !== null && match.participant1 !== -1 ? (
            <MatchParticipant
              prompt={getPromptResponse(match.participant1)['prompt']}
              response={getPromptResponse(match.participant1)['response']}
              votes={match.participant1_votes || 0}
              totalVotes={match.total_votes || 0}
              isWinner={match.winner === match.participant1}
              isUserChoice={
                match.winner === match.participant1 && match.winner !== null
              }
            />
          ) : (
            <MatchParticipant
              prompt=""
              response=""
              votes={0}
              totalVotes={0}
              isWinner={false}
              isUserChoice={false}
              isBye
            />
          )}

          {match.participant2 !== null && match.participant2 !== -1 ? (
            <MatchParticipant
              prompt={getPromptResponse(match.participant2)['prompt']}
              response={getPromptResponse(match.participant2)['response']}
              votes={match.participant2_votes || 0}
              totalVotes={match.total_votes || 0}
              isWinner={match.winner === match.participant2}
              isUserChoice={
                match.winner === match.participant2 && match.winner !== null
              }
            />
          ) : (
            <MatchParticipant
              prompt=""
              response=""
              votes={0}
              totalVotes={0}
              isWinner={false}
              isUserChoice={false}
              isBye
            />
          )}
        </Styled.MatchContainer>
      </Styled.CompetitionMatch>
    );
  }
);

BracketMatch.displayName = 'BracketMatch';
