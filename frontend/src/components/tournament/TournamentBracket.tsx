import * as Styled from '../../styles';
import { Tournament } from '../../types';

interface TournamentBracketProps {
  tournament: Tournament;
}

export function TournamentBracket({ tournament }: TournamentBracketProps) {
  const getRoundName = (roundIndex: number, totalRounds: number): string => {
    if (roundIndex === totalRounds - 1) return 'Final';
    if (roundIndex === totalRounds - 2) return 'Semi-Final';
    if (roundIndex === totalRounds - 3) return 'Quarter-Final';
    return `Round ${roundIndex + 1}`;
  };

  const getPromptResponse = (index: number): string => {
    return tournament.responses?.[index] ?? 'N/A';
  };

  return (
    <div>
      <Styled.SectionTitle>Tournament Progress</Styled.SectionTitle>
      <Styled.CompetitionContainer>
        <Styled.CompetitionTree>
          {tournament.bracket.map((round, roundIndex) => (
            <Styled.CompetitionRound key={roundIndex}>
              <Styled.RoundLabel>
                {getRoundName(roundIndex, tournament.bracket.length)}
              </Styled.RoundLabel>
              {round.map((match, matchIndex) => (
                <Styled.CompetitionMatch key={matchIndex}>
                  <Styled.MatchContainer>
                    {match.participant1 !== null &&
                    match.participant1 !== -1 ? (
                      <Styled.MatchParticipant
                        isWinner={match.winner === match.participant1}
                      >
                        {getPromptResponse(match.participant1)}
                      </Styled.MatchParticipant>
                    ) : (
                      <Styled.MatchParticipant isBye isWinner={false}>
                        Bye
                      </Styled.MatchParticipant>
                    )}
                    {match.participant2 !== null &&
                    match.participant2 !== -1 ? (
                      <Styled.MatchParticipant
                        isWinner={match.winner === match.participant2}
                      >
                        {getPromptResponse(match.participant2)}
                      </Styled.MatchParticipant>
                    ) : (
                      <Styled.MatchParticipant isBye isWinner={false}>
                        Bye
                      </Styled.MatchParticipant>
                    )}
                  </Styled.MatchContainer>
                </Styled.CompetitionMatch>
              ))}
            </Styled.CompetitionRound>
          ))}
        </Styled.CompetitionTree>
      </Styled.CompetitionContainer>
    </div>
  );
}
