import { memo, useCallback } from 'react';
import * as Styled from '../styles';
import { Tournament } from '../types';
import { BracketMatch } from './BracketMatch';
import { getRoundDisplayName } from '../utils';

interface TournamentBracketProps {
  tournament: Tournament;
}

export const TournamentBracket = memo<TournamentBracketProps>(
  ({ tournament }) => {
    const getPromptResponse = useCallback(
      (index: number): { prompt: string; response: string } => {
        return {
          prompt: tournament.prompts?.[index] ?? 'N/A',
          response: tournament.responses?.[index] ?? 'N/A',
        };
      },
      [tournament.prompts, tournament.responses]
    );

    // Show bracket if user has completed voting
    if (!tournament.user_state.completed) {
      return (
        <Styled.BracketSection>
          <Styled.SectionTitle>Tournament Bracket</Styled.SectionTitle>
          <Styled.CompetitionContainer>
            <Styled.BracketPlaceholder>
              Complete your voting to see the tournament bracket and how others
              voted!
            </Styled.BracketPlaceholder>
          </Styled.CompetitionContainer>
        </Styled.BracketSection>
      );
    }

    return (
      <Styled.BracketSection>
        <Styled.SectionTitle>Your Tournament Bracket</Styled.SectionTitle>

        <Styled.CompetitionContainer>
          <Styled.CompetitionTree>
            {tournament.user_bracket.map((round, roundIndex) => (
              <Styled.CompetitionRound key={roundIndex}>
                <Styled.RoundLabel>
                  {getRoundDisplayName(
                    roundIndex,
                    tournament.user_bracket.length
                  )}
                </Styled.RoundLabel>
                {round.map((match, matchIndex) => (
                  <BracketMatch
                    key={`${roundIndex}-${matchIndex}`}
                    match={match}
                    getPromptResponse={getPromptResponse}
                  />
                ))}
              </Styled.CompetitionRound>
            ))}
          </Styled.CompetitionTree>
        </Styled.CompetitionContainer>
      </Styled.BracketSection>
    );
  }
);

TournamentBracket.displayName = 'TournamentBracket';
