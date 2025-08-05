import { memo } from 'react';
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
    if (!currentMatchData.participant1 || !currentMatchData.participant2) {
      return null;
    }

    return (
      <Styled.ModalOverlay
        onClick={(e) => e.target === e.currentTarget && onClose()}
      >
        <Styled.ModalContent>
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
              <Styled.ResponseCard
                onClick={() => onVote(currentMatchData.participant1!.index)}
              >
                <Styled.ResponseText>
                  {currentMatchData.participant1.response}
                </Styled.ResponseText>
              </Styled.ResponseCard>

              <Styled.ResponseCard
                onClick={() => onVote(currentMatchData.participant2!.index)}
              >
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
