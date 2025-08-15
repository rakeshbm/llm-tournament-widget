import * as Styled from '../styles';
import { useTournaments } from '../hooks';
import { EmptyState, Loader, TournamentCard } from '../components';

export const TournamentsPage = () => {
  const { data, isLoading, error } = useTournaments();
  const tournaments = data?.tournaments ?? [];

  if (isLoading) {
    return <Loader text="Loading tournaments..." />;
  }

  if (error || !Array.isArray(tournaments)) {
    return (
      <EmptyState
        title="Tournaments"
        description="Failed to load tournaments"
      />
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
