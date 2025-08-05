import { memo, useCallback } from 'react';
import * as Styled from '../styles';
import { Tournament } from '../types';
import { getRoundDisplayName } from '../utils';

interface VotingModalProps {
  tournament: Tournament;
  currentMatchData: {
    round: number;
    match: number;
    participant1: { index: number; prompt: string; response: string } | null;
    participant2: { index: number; prompt: string; response: string } | null;
  };
  onVote: (index: number) => void;
  onClose: () => void;
}

export const VotingModal = memo<VotingModalProps>(
  ({ tournament, currentMatchData, onVote, onClose }) => {
    const handleOverlayClick = useCallback(
      (e: React.MouseEvent) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      },
      [onClose]
    );

    const handleStopPropagation = useCallback((e: React.MouseEvent) => {
      e.stopPropagation();
    }, []);

    const handleVote1 = useCallback(() => {
      if (currentMatchData.participant1) {
        onVote(currentMatchData.participant1.index);
      }
    }, [currentMatchData, onVote]);

    const handleVote2 = useCallback(() => {
      if (currentMatchData.participant2) {
        onVote(currentMatchData.participant2.index);
      }
    }, [currentMatchData, onVote]);

    if (!currentMatchData.participant1 || !currentMatchData.participant2) {
      return null;
    }

    return (
      <Styled.ModalOverlay onClick={handleOverlayClick}>
        <Styled.ModalContent onClick={handleStopPropagation}>
          <Styled.ModalHeader>
            <Styled.ModalTitle>Which response is better?</Styled.ModalTitle>
            <Styled.ModalSubtitle>
              Question: "{tournament.question}"
            </Styled.ModalSubtitle>
            <Styled.ModalSubtitle>
              {getRoundDisplayName(
                currentMatchData.round,
                tournament.user_bracket.length
              )}
              , Match {currentMatchData.match + 1}
            </Styled.ModalSubtitle>
            <Styled.ModalClose onClick={onClose} aria-label="Close modal">
              ×
            </Styled.ModalClose>
          </Styled.ModalHeader>
          <Styled.ModalBody>
            <Styled.ResponseGrid>
              <Styled.ResponseCard onClick={handleVote1}>
                <Styled.ResponseText>
                  {currentMatchData.participant1.response}
                </Styled.ResponseText>
              </Styled.ResponseCard>

              <Styled.ResponseCard onClick={handleVote2}>
                <Styled.ResponseText>
                  {currentMatchData.participant2.response}
                </Styled.ResponseText>
              </Styled.ResponseCard>
            </Styled.ResponseGrid>
          </Styled.ModalBody>
        </Styled.ModalContent>
      </Styled.ModalOverlay>
    );
  }
);
