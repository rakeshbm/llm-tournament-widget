import styled, { keyframes } from 'styled-components';

const colors = {
  primary: '#2563eb',
  primaryHover: '#1d4ed8',
  secondary: '#64748b',
  success: '#10b981',
  successLight: '#d1fae5',
  warning: '#f59e0b',
  warningLight: '#fef3c7',
  danger: '#ef4444',
  dangerHover: '#dc2626',
  background: '#f8fafc',
  card: '#ffffff',
  border: '#e2e8f0',
  borderFocus: '#3b82f6',
  textPrimary: '#0f172a',
  textSecondary: '#64748b',
  textMuted: '#94a3b8',
  overlay: 'rgba(15, 23, 42, 0.6)',
} as const;

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const slideIn = keyframes`
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
`;

const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

// Layout
export const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, ${colors.background} 0%, #f1f5f9 100%);
  padding: 24px;
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
`;

export const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

// Loading
export const LoadingOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: ${colors.overlay};
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
`;

export const LoadingContent = styled.div`
  background: ${colors.card};
  padding: 32px;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  animation: ${slideIn} 0.3s ease-out;
`;

export const LoadingSpinner = styled.div`
  width: 40px;
  height: 40px;
  border: 3px solid ${colors.border};
  border-top: 3px solid ${colors.primary};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  margin: 0 auto 16px;
`;

export const LoadingText = styled.p`
  color: ${colors.textSecondary};
  font-size: 16px;
  margin: 0;
  font-weight: 500;
`;

// Typography
export const Header = styled.header`
  text-align: center;
  margin-bottom: 48px;
  animation: ${fadeIn} 0.6s ease-out;
`;

export const Title = styled.h1`
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: ${colors.textPrimary};
  letter-spacing: -0.025em;
`;

export const Subtitle = styled.p`
  font-size: 18px;
  color: ${colors.textSecondary};
  margin: 0 0 8px 0;
  line-height: 1.6;
`;

export const Description = styled.p`
  font-size: 16px;
  color: ${colors.textMuted};
  margin: 0;
  line-height: 1.5;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
`;

export const SectionTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: ${colors.textPrimary};
  letter-spacing: -0.025em;
`;

// Forms
export const CreatorContainer = styled.div`
  max-width: 700px;
  margin: 0 auto;
  background: ${colors.card};
  padding: 32px;
  border-radius: 16px;
  border: 1px solid ${colors.border};
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  animation: ${fadeIn} 0.5s ease-out;
`;

export const FormGroup = styled.div`
  margin-bottom: 24px;
`;

export const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: ${colors.textPrimary};
  font-size: 14px;
  letter-spacing: 0.025em;
`;

export const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid ${colors.border};
  border-radius: 8px;
  font-size: 16px;
  font-family: inherit;
  resize: vertical;
  transition: all 0.2s ease;
  background: ${colors.card};
  color: ${colors.textPrimary};
  line-height: 1.5;
  overflow-wrap: break-word;
  white-space: pre-wrap;

  &:focus {
    outline: none;
    border-color: ${colors.borderFocus};
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  &::placeholder {
    color: ${colors.textMuted};
  }
`;

export const PromptRow = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  align-items: flex-start;
`;

export const ButtonRow = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
`;

// Buttons
export const ButtonGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

export const PrimaryButton = styled.button`
  padding: 12px 24px;
  background: ${colors.primary};
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover:not(:disabled) {
    background: ${colors.primaryHover};
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
  }

  &:disabled {
    background: ${colors.textMuted};
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

export const SecondaryButton = styled.button<{ disabled?: boolean }>`
  padding: 12px 24px;
  background: ${colors.card};
  color: ${colors.secondary};
  border: 2px solid ${colors.border};
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: ${colors.background};
    border-color: ${colors.secondary};
    transform: translateY(-1px);
    cursor: pointer;
  }
`;

export const RemoveButton = styled.button<{ disabled: boolean }>`
  background: ${(props) =>
    props.disabled ? colors.background : colors.danger};
  color: ${(props) => (props.disabled ? colors.textMuted : 'white')};
  border: none;
  border-radius: 6px;
  cursor: ${(props) => (props.disabled ? 'not-allowed' : 'pointer')};
  font-size: 18px;
  min-width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  align-self: center;

  &:hover:not(:disabled) {
    background: ${colors.dangerHover};
  }
`;

export const HistoryButton = styled.button`
  width: 100%;
  padding: 16px 24px;
  background: ${colors.card};
  color: ${colors.primary};
  border: 2px solid ${colors.primary};
  border-radius: 12px;
  cursor: pointer;
  margin-top: 32px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s ease;

  &:hover {
    background: ${colors.primary};
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3);
  }
`;

export const SmallButton = styled.button<{ viewOnly?: boolean }>`
  padding: 8px 16px;
  background: ${(props) =>
    props.viewOnly ? colors.successLight : colors.warningLight};
  color: ${(props) => (props.viewOnly ? colors.success : colors.warning)};
  border: 1px solid
    ${(props) => (props.viewOnly ? colors.success : colors.warning)};
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
`;

export const CloseButton = styled.button`
  float: right;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: inherit;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(0, 0, 0, 0.1);
  }
`;

// Tournament Cards
export const TournamentCard = styled.div`
  background: ${colors.card};
  padding: 32px;
  border-radius: 16px;
  margin-bottom: 32px;
  border: 1px solid ${colors.border};
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  animation: ${fadeIn} 0.5s ease-out;
`;

export const TournamentHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
  }
`;

export const TournamentInfo = styled.div`
  flex: 1;
`;

export const TournamentTitle = styled.h2`
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 700;
  color: ${colors.textPrimary};
  line-height: 1.3;
`;

export const TournamentMeta = styled.p`
  margin: 0 0 16px 0;
  color: ${colors.textSecondary};
  font-size: 16px;
  font-weight: 500;
`;

// Progress
export const ProgressBar = styled.div`
  background: ${colors.border};
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  margin: 16px 0 8px 0;
`;

export const ProgressFill = styled.div<{ width: string }>`
  height: 100%;
  background: linear-gradient(90deg, ${colors.primary}, ${colors.success});
  width: ${(props) => props.width};
  transition: width 0.5s ease;
  border-radius: 4px;
`;

export const ProgressText = styled.p`
  font-size: 14px;
  color: ${colors.textSecondary};
  margin: 0;
  font-weight: 500;
`;

export const WinnerAlert = styled.div`
  background: ${colors.successLight};
  color: ${colors.success};
  padding: 16px;
  border-radius: 8px;
  margin-top: 16px;
  border: 1px solid ${colors.success};
  font-weight: 600;
  animation: ${fadeIn} 0.5s ease-out;
`;

// Alerts
export const ErrorAlert = styled.div`
  background: #fef2f2;
  color: #dc2626;
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 24px;
  border: 1px solid #fecaca;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  animation: ${fadeIn} 0.3s ease-out;
`;

// Competition Tree
export const CompetitionContainer = styled.div`
  overflow-x: auto;
  overflow-y: visible;
  padding: 8px 20px;
  background: ${colors.card};
  border-radius: 12px;
  border: 1px solid ${colors.border};
`;

export const CompetitionTree = styled.div`
  display: flex;
  align-items: center;
  gap: 80px;
  min-width: fit-content;
  position: relative;
`;

export const CompetitionRound = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  position: relative;
`;

export const RoundLabel = styled.p`
  font-size: 14px;
  font-weight: 600;
  color: ${colors.textSecondary};
  text-align: center;
  white-space: nowrap;
  margin-bottom: 16px;
`;

export const CompetitionMatch = styled.div`
  position: relative;
  margin: 15px 0;
  z-index: 2;
`;

export const MatchContainer = styled.div`
  background: ${colors.card};
  border: 2px solid ${colors.border};
  border-radius: 8px;
  width: 200px;
  overflow: hidden;
  position: relative;
  z-index: 3;
`;

export const MatchParticipant = styled.div<{
  isWinner: boolean;
  isBye?: boolean;
}>`
  padding: 12px 16px;
  border-bottom: 1px solid ${colors.border};
  background: ${(props) => {
    if (props.isBye) return colors.background;
    if (props.isWinner) return colors.successLight;
    return colors.card;
  }};
  color: ${(props) => {
    if (props.isBye) return colors.textMuted;
    if (props.isWinner) return colors.success;
    return colors.textPrimary;
  }};
  font-size: 14px;
  font-weight: ${(props) => (props.isWinner ? 600 : 400)};
  border-left: ${(props) =>
    props.isWinner ? `4px solid ${colors.success}` : '4px solid transparent'};
  text-align: ${(props) => (props.isBye ? 'center' : 'left')};
  transition: all 0.2s ease;

  &:last-child {
    border-bottom: none;
  }
`;

// History
export const HistoryCard = styled.div`
  background: ${colors.card};
  border: 1px solid ${colors.border};
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  transition: all 0.2s ease;
  animation: ${fadeIn} 0.3s ease-out;
`;

export const HistoryInfo = styled.div`
  flex: 1;
`;

export const HistoryQuestion = styled.h3`
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: ${colors.textPrimary};
  line-height: 1.4;
`;

export const HistoryMeta = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
`;

export const HistoryChip = styled.span<{ variant?: 'success' | 'warning' }>`
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  background: ${(props) => {
    switch (props.variant) {
      case 'success':
        return colors.successLight;
      case 'warning':
        return colors.warningLight;
      default:
        return colors.background;
    }
  }};
  color: ${(props) => {
    switch (props.variant) {
      case 'success':
        return colors.success;
      case 'warning':
        return colors.warning;
      default:
        return colors.textSecondary;
    }
  }};
  border: 1px solid
    ${(props) => {
      switch (props.variant) {
        case 'success':
          return colors.success;
        case 'warning':
          return colors.warning;
        default:
          return colors.border;
      }
    }};
`;

export const HistoryDate = styled.span`
  font-size: 14px;
  color: ${colors.textMuted};
  font-weight: 500;
`;

export const HistoryActions = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

export const EmptyHistory = styled.div`
  text-align: center;
  padding: 48px 24px;
  color: ${colors.textMuted};
  background: ${colors.card};
  border: 1px solid ${colors.border};
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
`;

// Modal
export const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: ${colors.overlay};
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 1000;
  backdrop-filter: blur(4px);
  animation: ${fadeIn} 0.2s ease-out;
`;

export const ModalContent = styled.div`
  background: ${colors.card};
  border-radius: 16px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: ${slideIn} 0.3s ease-out;
`;

export const ModalHeader = styled.div`
  position: relative;
  padding: 24px 32px;
  border-bottom: 1px solid ${colors.border};
  background: ${colors.background};
  border-radius: 16px 16px 0 0;
`;

export const ModalTitle = styled.h3`
  margin: 0 0 8px 0;
  color: ${colors.textPrimary};
  font-size: 24px;
  font-weight: 700;
`;

export const ModalSubtitle = styled.p`
  margin: 0;
  color: ${colors.textSecondary};
  font-size: 16px;
  font-weight: 500;
`;

export const ModalClose = styled.button`
  position: absolute;
  top: 16px;
  right: 16px;
  background: transparent;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;

  &:hover {
    color: #000;
  }
`;

export const ModalBody = styled.div`
  padding: 32px;
`;

export const ResponseGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

export const ResponseCard = styled.div`
  border: 2px solid ${colors.border};
  border-radius: 12px;
  padding: 16px;
  background: ${colors.card};
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: ${colors.primary};
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.15);
  }
`;

export const ResponseText = styled.div`
  font-size: 16px;
  line-height: 1.6;
  color: ${colors.textPrimary};
`;

export const HistoryModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: ${colors.overlay};
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  backdrop-filter: blur(4px);
  animation: ${fadeIn} 0.2s ease-out;
`;

export const HistoryModalContent = styled.div`
  background: ${colors.card};
  border-radius: 16px;
  padding: 32px;
  max-height: 80vh;
  overflow-y: auto;
  width: 100%;
  max-width: 800px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: ${slideIn} 0.3s ease-out;
`;
