import { useState } from 'react';
import * as Styled from '../../styles';
import { TournamentSummary } from '../../types';

interface TournamentHistoryProps {
  tournaments: TournamentSummary[];
  onLoadTournament: (id: number) => void;
}

export function TournamentHistory({ tournaments, onLoadTournament }: TournamentHistoryProps) {
  const [showHistory, setShowHistory] = useState(false);

  const handleClick = (tournamentId: number) => {
    setShowHistory(false);
    onLoadTournament(tournamentId);
  };

  return (
    <>
      <Styled.HistoryButton onClick={() => setShowHistory(!showHistory)}>
        {showHistory ? 'Hide' : 'Show'} Tournament History ({tournaments.length})
      </Styled.HistoryButton>

      {showHistory && (
        <Styled.HistoryModalOverlay onClick={() => setShowHistory(false)}>
          <Styled.HistoryModalContent onClick={(e) => e.stopPropagation()}>
            <Styled.SectionTitle>Tournament History</Styled.SectionTitle>

            {tournaments.length === 0 ? (
              <Styled.EmptyHistory>No tournaments yet</Styled.EmptyHistory>
            ) : (
              tournaments.map((tournament) => (
                <Styled.HistoryCard key={tournament.id}>
                  <Styled.HistoryInfo>
                    <Styled.HistoryQuestion>{tournament.question}</Styled.HistoryQuestion>
                    <Styled.HistoryMeta>
                      <Styled.HistoryChip>{tournament.num_prompts} prompts</Styled.HistoryChip>
                      <Styled.HistoryChip variant={tournament.completed ? 'success' : 'warning'}>
                        {tournament.completed ? 'Completed' : 'In Progress'}
                      </Styled.HistoryChip>
                    </Styled.HistoryMeta>
                    <Styled.HistoryDate>
                      {new Date(tournament.created_at).toLocaleDateString()}
                    </Styled.HistoryDate>
                  </Styled.HistoryInfo>
                  <Styled.HistoryActions>
                    <Styled.SmallButton onClick={() => handleClick(tournament.id)} viewOnly={tournament.completed}>
                      {tournament.completed ? 'View' : 'Vote'}
                    </Styled.SmallButton>
                  </Styled.HistoryActions>
                </Styled.HistoryCard>
              ))
            )}
          </Styled.HistoryModalContent>
        </Styled.HistoryModalOverlay>
      )}
    </>
  );
}
