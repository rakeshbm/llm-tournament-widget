import {
  TournamentCreator,
  TournamentBracket,
  TournamentHistory,
  VotingModal,
} from './components/tournament';
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
  const progressPercentage = getTournamentProgress();

  const getLoadingMessage = (): string => {
    if (!tournament) return 'Creating your tournament...';
    return 'Processing your vote...';
  };

  const getWinnerMessage = (): string => {
    if (!tournament?.winner_prompt) return '';
    return `🏆 Winner: ${tournament.winner_prompt}`;
  };

  return (
    <>
      <Styled.AppContainer>
        <Styled.Container>
          <Styled.Header>
            <Styled.Title>LLM Prompt Tournament</Styled.Title>
            <Styled.Subtitle>
              Discover which prompts work best through head-to-head competition
            </Styled.Subtitle>
            <Styled.Description>
              Test multiple prompts against the same question and let voting
              determine the winner. Perfect for finding the most effective
              prompt variations.
            </Styled.Description>
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
                    <Styled.TournamentTitle>
                      {tournament.question}
                    </Styled.TournamentTitle>
                    <Styled.TournamentMeta>
                      Testing {tournament.prompts.length} different prompts
                    </Styled.TournamentMeta>

                    <Styled.ProgressBar>
                      <Styled.ProgressFill width={`${progressPercentage}%`} />
                    </Styled.ProgressBar>
                    <Styled.ProgressText>
                      {progressPercentage}% complete
                    </Styled.ProgressText>

                    {tournament.completed && tournament.winner_prompt && (
                      <Styled.WinnerAlert>
                        {getWinnerMessage()}
                      </Styled.WinnerAlert>
                    )}
                  </Styled.TournamentInfo>

                  <Styled.SecondaryButton onClick={resetTournament}>
                    Start New Competition
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
              onClose={() => console.log('Voting modal dismissed')}
            />
          )}
        </Styled.Container>
      </Styled.AppContainer>

      {loading && (
        <Styled.LoadingOverlay>
          <Styled.LoadingContent>
            <Styled.LoadingSpinner />
            <Styled.LoadingText>{getLoadingMessage()}</Styled.LoadingText>
          </Styled.LoadingContent>
        </Styled.LoadingOverlay>
      )}
    </>
  );
}
