import * as Styled from '../styles';
import { useTournaments } from '../hooks';
import { EmptyState, Loader, TournamentCard } from '../components';

export const TournamentsPage = () => {
  const { data: tournaments, isLoading, error } = useTournaments();

  if (isLoading) {
    return <Loader text="Loading tournaments..." />;
  }

  if (error) {
    return (
      <Styled.PageContainer>
        <Styled.Title>Tournaments</Styled.Title>
        <Styled.ErrorMessage>
          Failed to load tournaments: {error.message}
        </Styled.ErrorMessage>
      </Styled.PageContainer>
    );
  }

  if (!tournaments) {
    return (
      <Styled.PageContainer>
        <Styled.Title>Tournaments</Styled.Title>
        <Styled.ErrorMessage>No tournament data available</Styled.ErrorMessage>
      </Styled.PageContainer>
    );
  }

  return (
    <Styled.PageContainer>
      <Styled.PageHeader>
        <Styled.Title>All Tournaments</Styled.Title>
        <Styled.PrimaryLinkButton to="/tournaments/create">
          Create New Tournament
        </Styled.PrimaryLinkButton>
      </Styled.PageHeader>

      {tournaments.length === 0 ? (
        <EmptyState
          title="No tournaments yet"
          description="Create your first tournament to get started with prompt competitions!"
        />
      ) : (
        <Styled.TournamentGrid>
          {tournaments.map((tournament) => (
            <TournamentCard key={tournament.id} tournament={tournament} />
          ))}
        </Styled.TournamentGrid>
      )}
    </Styled.PageContainer>
  );
};
