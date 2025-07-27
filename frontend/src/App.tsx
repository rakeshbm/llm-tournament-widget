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
    vote,
    resetTournament,
    clearError,
    createTournament,
    loadTournament,
    getCurrentMatchData,
    getTournamentProgress,
    closeVotingModal,
    openVotingModal,
  } = useTournament();

  const currentMatchData = getCurrentMatchData();
  const progressPercentage = getTournamentProgress();

  const getLoadingMessage = (): string => {
    if (!tournament) return 'Creating your tournament...';
    return 'Loading tournament...';
  };

  const getWinnerMessage = (): string => {
    if (!tournament?.winner_prompt) return '';
    return `🏆 Winner prompt: ${tournament.winner_prompt}`;
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

                  <Styled.ButtonGroup>
                    {!tournament.completed && (
                      <Styled.PrimaryButton onClick={openVotingModal}>
                        Continue Tournament
                      </Styled.PrimaryButton>
                    )}
                    <Styled.SecondaryButton onClick={resetTournament}>
                      Start New Tournament
                    </Styled.SecondaryButton>
                  </Styled.ButtonGroup>
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
              onClose={closeVotingModal}
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
