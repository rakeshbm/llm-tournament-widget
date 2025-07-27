import * as Styled from '../../styles';
import { Tournament } from '../../types';

interface CurrentMatch {
  participant1: number | null;
  participant2: number | null;
}

interface VotingModalProps {
  tournament: Tournament;
  currentMatch: CurrentMatch | null;
  onVote: (index: number) => void;
  onClose: () => void;
}

export function VotingModal({
  tournament,
  currentMatch,
  onVote,
  onClose,
}: VotingModalProps) {
  if (!currentMatch) return null;

  const participants = [currentMatch.participant1, currentMatch.participant2];

  return (
    <Styled.ModalOverlay onClick={onClose}>
      <Styled.ModalContent onClick={(e) => e.stopPropagation()}>
        <Styled.ModalHeader>
          <Styled.ModalTitle>Which Response is Better?</Styled.ModalTitle>
          <Styled.ModalSubtitle>
            Question: "{tournament.question}"
          </Styled.ModalSubtitle>
          <Styled.ModalClose onClick={onClose} aria-label="Close modal">
            ×
          </Styled.ModalClose>
        </Styled.ModalHeader>

        <Styled.ModalBody>
          <Styled.ResponseGrid>
            {participants.map((participantIndex, idx) => {
              if (participantIndex === null || participantIndex === -1)
                return null;

              return (
                <Styled.ResponseCard
                  key={idx}
                  onClick={() => onVote(participantIndex)}
                >
                  <Styled.ResponseText>
                    {tournament.responses[participantIndex]}
                  </Styled.ResponseText>
                </Styled.ResponseCard>
              );
            })}
          </Styled.ResponseGrid>
        </Styled.ModalBody>
      </Styled.ModalContent>
    </Styled.ModalOverlay>
  );
}
