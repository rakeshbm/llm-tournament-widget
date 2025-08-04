import { memo } from 'react';
import { TournamentSummary } from '../types';
import * as Styled from '../styles';
import { Link } from 'react-router-dom';

interface TournamentCardProps {
  tournament: TournamentSummary;
}

export const TournamentCard = memo<TournamentCardProps>(({ tournament }) => (
  <Styled.HistoryCard>
    <Styled.HistoryInfo>
      <Styled.HistoryQuestion>{tournament.question}</Styled.HistoryQuestion>
      <Styled.HistoryMeta>
        <Styled.HistoryChip>
          {tournament.num_prompts} prompts
        </Styled.HistoryChip>
        <Styled.HistoryChip>
          {tournament.total_participants} participants
        </Styled.HistoryChip>
        <Styled.HistoryChip>
          {tournament.completed_participants} completed
        </Styled.HistoryChip>
      </Styled.HistoryMeta>
      <Styled.HistoryDate>
        Created: {new Date(tournament.created_at).toLocaleDateString()}
      </Styled.HistoryDate>
    </Styled.HistoryInfo>
    <Styled.HistoryActions>
      <Link to={`${tournament.id}`}>
        <Styled.SmallButton>View</Styled.SmallButton>
      </Link>
    </Styled.HistoryActions>
  </Styled.HistoryCard>
));
