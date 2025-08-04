import { memo } from 'react';
import * as Styled from '../styles';
import { TournamentResults } from '../types';

interface TournamentResultsSectionProps {
  results: TournamentResults;
}

export const TournamentResultsSection = memo<TournamentResultsSectionProps>(
  ({ results }) => {
    return (
      <Styled.ResultsSection>
        <Styled.SectionTitle>Tournament Results</Styled.SectionTitle>

        <Styled.TournamentStatsCard>
          <Styled.StatItem>
            <Styled.StatLabel>Total Users:</Styled.StatLabel>
            <Styled.StatValue>
              {results.stats.total_participants}
            </Styled.StatValue>
          </Styled.StatItem>
          <Styled.StatItem>
            <Styled.StatLabel>Completed Voting:</Styled.StatLabel>
            <Styled.StatValue>
              {results.stats.completed_participants}
            </Styled.StatValue>
          </Styled.StatItem>
        </Styled.TournamentStatsCard>

        <Styled.ResultsList>
          {results.results.map((result, index) => (
            <Styled.ResultItem key={result.prompt_index} rank={index + 1}>
              <Styled.ResultRank>#{index + 1}</Styled.ResultRank>
              <Styled.ResultContent>
                <Styled.ResultPrompt>{result.prompt}</Styled.ResultPrompt>
                <Styled.ResultStats>
                  <Styled.ResultStat>
                    <strong>{result.win_count}</strong> wins
                  </Styled.ResultStat>
                  <Styled.ResultStat>
                    <strong>{result.win_percentage.toFixed(1)}%</strong> win
                    rate
                  </Styled.ResultStat>
                </Styled.ResultStats>
              </Styled.ResultContent>
            </Styled.ResultItem>
          ))}
        </Styled.ResultsList>
      </Styled.ResultsSection>
    );
  }
);
