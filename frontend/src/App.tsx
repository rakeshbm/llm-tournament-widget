import { TournamentCreator, TournamentBracket, TournamentHistory, VotingModal } from './components/tournament';
import { useTournament } from './hooks';
import * as Styled from './styles';

export default function App() {
  const {
    tournament,
    tournaments,
    loading,
    error,
    voteDialog,
    createTournament,
    loadTournament,
    vote,
    resetTournament,
    clearError,
    getCurrentMatchData,
    getTournamentProgress,
  } = useTournament();

  const currentMatchData = getCurrentMatchData();

  return (
    <>
      <Styled.AppContainer>
        <Styled.Container>
          <Styled.Header>
            <Styled.Title>LLM Prompt Tournament</Styled.Title>
            <Styled.Subtitle>
              Compare prompts and find the best one through bracket-style elimination
            </Styled.Subtitle>
          </Styled.Header>

          {error && (
            <Styled.ErrorAlert>
              {error}
              <Styled.CloseButton onClick={clearError}>×</Styled.CloseButton>
            </Styled.ErrorAlert>
          )}

          {!tournament && (
            <TournamentCreator 
              onCreateTournament={createTournament}
              loading={loading}
            />
          )}

          {tournament && (
            <>
              <Styled.TournamentCard>
                <Styled.TournamentHeader>
                  <Styled.TournamentInfo>
                    <Styled.TournamentTitle>{tournament.question}</Styled.TournamentTitle>
                    <Styled.TournamentMeta>
                      {tournament.prompts.length} prompts competing
                    </Styled.TournamentMeta>
                    <Styled.ProgressBar>
                      <Styled.ProgressFill width={`${getTournamentProgress()}%`} />
                    </Styled.ProgressBar>
                    <Styled.ProgressText>
                      Progress: {getTournamentProgress()}% complete
                    </Styled.ProgressText>
                    {tournament.completed && tournament.winner_prompt && (
                      <Styled.WinnerAlert>
                        <strong>🏆 Winner:</strong> {tournament.winner_prompt}
                      </Styled.WinnerAlert>
                    )}
                  </Styled.TournamentInfo>
                  <Styled.SecondaryButton onClick={resetTournament}>
                    New Tournament
                  </Styled.SecondaryButton>
                </Styled.TournamentHeader>
              </Styled.TournamentCard>

              <TournamentBracket tournament={tournament} />
            </>
          )}

          <TournamentHistory 
            tournaments={tournaments}
            onLoadTournament={loadTournament}
          />

          {voteDialog && tournament && currentMatchData && (
            <VotingModal
              tournament={tournament}
              currentMatch={currentMatchData}
              onVote={vote}
              onClose={() => console.log('Modal close clicked')}
            />
          )}
        </Styled.Container>
      </Styled.AppContainer>

      {/* Loading Overlay */}
      {loading && (
        <Styled.LoadingOverlay>
          <Styled.LoadingContent>
            <Styled.LoadingSpinner />
            <Styled.LoadingText>
              {!tournament ? 'Creating tournament...' : 'Processing...'}
            </Styled.LoadingText>
          </Styled.LoadingContent>
        </Styled.LoadingOverlay>
      )}
    </>
  );
}
