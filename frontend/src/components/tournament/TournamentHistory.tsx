import { useState } from 'react';
import * as Styled from '../../styles';
import { TournamentSummary } from '../../types';

interface TournamentHistoryProps {
  tournaments: TournamentSummary[];
  onLoadTournament: (id: number) => void;
}

export function TournamentHistory({
  tournaments,
  onLoadTournament,
}: TournamentHistoryProps) {
  const [isVisible, setIsVisible] = useState(false);

  const handleTournamentClick = (tournamentId: number) => {
    setIsVisible(false);
    onLoadTournament(tournamentId);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <>
      <Styled.HistoryButton onClick={() => setIsVisible(!isVisible)}>
        {isVisible ? 'Hide' : 'View'} Past Tournaments ({tournaments.length})
      </Styled.HistoryButton>

      {isVisible && (
        <Styled.HistoryModalOverlay onClick={() => setIsVisible(false)}>
          <Styled.HistoryModalContent onClick={(e) => e.stopPropagation()}>
            <Styled.SectionTitle>Tournament History</Styled.SectionTitle>

            {tournaments.length === 0 ? (
              <Styled.EmptyHistory>
                No tournaments yet. Create your first prompt tournament to get
                started!
              </Styled.EmptyHistory>
            ) : (
              tournaments.map((tournament) => (
                <Styled.HistoryCard key={tournament.id}>
                  <Styled.HistoryInfo>
                    <Styled.HistoryQuestion>
                      {tournament.question}
                    </Styled.HistoryQuestion>
                    <Styled.HistoryMeta>
                      <Styled.HistoryChip>
                        {tournament.num_prompts} prompts
                      </Styled.HistoryChip>
                      <Styled.HistoryChip
                        variant={tournament.completed ? 'success' : 'warning'}
                      >
                        {tournament.completed ? 'Finished' : 'Ongoing'}
                      </Styled.HistoryChip>
                    </Styled.HistoryMeta>
                    <Styled.HistoryDate>
                      Started {formatDate(tournament.created_at)}
                    </Styled.HistoryDate>
                  </Styled.HistoryInfo>
                  <Styled.HistoryActions>
                    <Styled.SmallButton
                      onClick={() => handleTournamentClick(tournament.id)}
                      viewOnly={tournament.completed}
                    >
                      {tournament.completed ? 'See Results' : 'Continue'}
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
