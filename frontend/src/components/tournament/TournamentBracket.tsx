import * as Styled from '../../styles';
import { Tournament } from '../../types';

interface TournamentBracketProps {
  tournament: Tournament;
}

export function TournamentBracket({ tournament }: TournamentBracketProps) {
  const getRoundName = (roundIndex: number, totalRounds: number) => {
    if (roundIndex === totalRounds - 1) return 'Final';
    if (roundIndex === totalRounds - 2) return 'Semi-final';
    if (roundIndex === totalRounds - 3) return 'Quarter-final';
    return `Round ${roundIndex + 1}`;
  };

  const getPrompt = (index: number) => {
    return tournament.prompts?.[index] ?? `Prompt ${index + 1}`;
  };

  return (
    <div>
      <Styled.SectionTitle>Tournament Bracket</Styled.SectionTitle>

      <Styled.BracketContainer>
        <Styled.BracketTree>
          {tournament.bracket.map((round, roundIndex) => (
            <Styled.BracketRound key={roundIndex}>
              <Styled.RoundLabel>
                {getRoundName(roundIndex, tournament.bracket.length)}
              </Styled.RoundLabel>

              {round.map((match, matchIndex) => (
                <Styled.BracketMatch key={matchIndex} completed={match.winner !== null}>
                  <Styled.MatchContainer>
                    {/* First Participant */}
                    {match.participant1 !== null && match.participant1 !== -1 ? (
                      <Styled.MatchParticipant
                        isWinner={match.winner === match.participant1}
                      >
                        {getPrompt(match.participant1)}
                      </Styled.MatchParticipant>
                    ) : (
                      <Styled.MatchParticipant isBye isWinner={false}>
                        BYE
                      </Styled.MatchParticipant>
                    )}

                    {/* Second Participant */}
                    {match.participant2 !== null && match.participant2 !== -1 ? (
                      <Styled.MatchParticipant
                        isWinner={match.winner === match.participant2}
                      >
                        {getPrompt(match.participant2)}
                      </Styled.MatchParticipant>
                    ) : (
                      <Styled.MatchParticipant isBye isWinner={false}>
                        BYE
                      </Styled.MatchParticipant>
                    )}
                  </Styled.MatchContainer>
                </Styled.BracketMatch>
              ))}
            </Styled.BracketRound>
          ))}
        </Styled.BracketTree>
      </Styled.BracketContainer>
    </div>
  );
}
