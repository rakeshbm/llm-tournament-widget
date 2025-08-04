import { memo, useCallback } from 'react';
import * as Styled from '../styles';
import { Tournament } from '../types';
import { calculateTournamentProgress } from '../utils';

interface TournamentHeaderProps {
  tournament: Tournament;
  onContinueVoting: () => void;
}

export const TournamentHeader = memo<TournamentHeaderProps>(
  ({ tournament, onContinueVoting }) => {
    const handleContinueVoting = useCallback(() => {
      onContinueVoting();
    }, [onContinueVoting]);

    const progressPercentage = calculateTournamentProgress(
      tournament.user_bracket,
      tournament.user_state.completed
    );

    const getStatusMessage = () => {
      if (tournament.user_state.completed) {
        return "✅ You've completed voting! Check out the results below.";
      }
      return `🗳️ Continue voting to see the results! Progress: ${progressPercentage}%`;
    };

    return (
      <Styled.TournamentCard>
        <Styled.TournamentHeader>
          <Styled.TournamentInfo>
            <Styled.TournamentTitle>
              Question: "{tournament.question}"
            </Styled.TournamentTitle>
            <Styled.TournamentMeta>
              {tournament.prompts.length} prompts:
              {tournament.prompts.map((prompt) => (
                <p>
                  <em>"{prompt}"</em>
                </p>
              ))}
            </Styled.TournamentMeta>

            <Styled.ProgressContainer>
              <Styled.ProgressBar>
                <Styled.ProgressFill width={`${progressPercentage}%`} />
              </Styled.ProgressBar>
              <Styled.ProgressText>
                Your voting progress: {progressPercentage}%
              </Styled.ProgressText>
            </Styled.ProgressContainer>

            <Styled.StatusMessage
              type={tournament.user_state.completed ? 'success' : 'action'}
            >
              {getStatusMessage()}
            </Styled.StatusMessage>
          </Styled.TournamentInfo>

          {!tournament.user_state.completed && (
            <Styled.PrimaryButton onClick={handleContinueVoting}>
              Continue Voting
            </Styled.PrimaryButton>
          )}
        </Styled.TournamentHeader>
      </Styled.TournamentCard>
    );
  }
);
