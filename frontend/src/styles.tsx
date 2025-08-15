import { Link } from 'react-router-dom';
import styled, { keyframes } from 'styled-components';

const colors = {
  // Primary palette
  primary: '#2563eb',
  primaryHover: '#1d4ed8',
  primaryLight: '#3b82f6',

  // Semantic colors
  success: '#10b981',
  successLight: '#d1fae5',
  successBackground: '#f0fdf4',
  successDark: '#15803d',
  successBorder: '#bbf7d0',

  warning: '#f59e0b',
  warningLight: '#fef3c7',
  warningBackground: '#fffbeb',
  warningDark: '#d97706',
  warningBorder: '#fed7aa',

  danger: '#ef4444',
  dangerHover: '#dc2626',
  dangerBackground: '#fef2f2',
  dangerBorder: '#fecaca',

  // Neutral palette
  gray50: '#f8fafc',
  gray100: '#f1f5f9',
  gray200: '#e2e8f0',
  gray300: '#cbd5e1',
  gray400: '#94a3b8',
  gray500: '#64748b',
  gray600: '#475569',
  gray700: '#334155',
  gray800: '#1e293b',
  gray900: '#0f172a',

  // Background colors
  background: '#f8fafc',
  backgroundSecondary: '#f1f5f9',
  backgroundTertiary: '#f9fafb',
  card: '#ffffff',

  // Text colors
  textPrimary: '#0f172a',
  textSecondary: '#64748b',
  textMuted: '#94a3b8',
  textDark: '#374151',
  textLight: '#6b7280',

  // Utility colors
  overlay: 'rgba(15, 23, 42, 0.6)',
  disabled: '#e0e1e3',

  // Medal colors
  gold: '#f59e0b',
  goldBackground: '#fef3c7',
  silver: '#6b7280',
  silverBackground: '#e5e7eb',
  bronze: '#ea580c',
  bronzeBackground: '#fed7aa',
} as const;

// Animations
const fadeIn = keyframes`
  from { 
    opacity: 0; 
    transform: translateY(10px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
`;

const slideIn = keyframes`
  from { 
    opacity: 0; 
    transform: scale(0.95); 
  }
  to { 
    opacity: 1; 
    transform: scale(1); 
  }
`;

const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

// Base styles
const baseTransition = 'all 0.2s ease';
const baseFont = `-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif`;
const monoFont = `'SF Mono', Monaco, Consolas, 'Courier New', monospace`;

// Layout Components
export const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(
    135deg,
    ${colors.background} 0%,
    ${colors.backgroundSecondary} 100%
  );
  padding: 24px;
  font-family: ${baseFont};
`;

export const Container = styled.div`
  width: 100%;
  margin: 0 auto;
  position: relative;
`;

export const PageContainer = styled.div`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

export const PageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
`;

// Loading Components
export const LoadingOverlay = styled.div`
  position: fixed;
  inset: 0;
  background: ${colors.overlay};
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
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
  border: 3px solid ${colors.gray200};
  border-top: 3px solid ${colors.primary};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  margin: 0 auto 16px;
`;

export const LoadingText = styled.p`
  color: ${colors.textSecondary};
  font-size: 16px;
  font-weight: 500;
  margin: 0;
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
  line-height: 1.5;
  max-width: 600px;
  margin: 0 auto;
`;

export const SectionTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: ${colors.textPrimary};
  letter-spacing: -0.025em;
`;

// Form Components
export const CreatorContainer = styled.div`
  background: ${colors.card};
  padding: 32px;
  border-radius: 16px;
`;

export const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  margin: 24px 0;
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
  border: 2px solid ${colors.gray200};
  border-radius: 8px;
  font-size: 16px;
  font-family: inherit;
  resize: vertical;
  transition: ${baseTransition};
  background: ${colors.card};
  color: ${colors.textPrimary};
  line-height: 1.5;

  &:focus {
    outline: none;
    border-color: ${colors.primaryLight};
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

// Button Components
const baseButton = `
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  transition: ${baseTransition};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  text-decoration: none;
  border: none;
`;

export const ButtonGroup = styled.div`
  display: flex;
  flex-direction: column;
  margin: 0 auto;
  width: 30%;
  gap: 12px;
`;

export const PrimaryButton = styled.button`
  ${baseButton}
  background: ${colors.primary};
  color: white;

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

export const SecondaryButton = styled.button`
  ${baseButton}
  background: ${colors.card};
  color: ${colors.textSecondary};
  border: 2px solid ${colors.gray200};

  &:hover:not(:disabled) {
    background: ${colors.background};
    border-color: ${colors.textSecondary};
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

export const PrimaryLinkButton = styled(Link)`
  ${baseButton}
  background: ${colors.primary};
  color: white;
  text-align: center;

  &:hover {
    background: ${colors.primaryHover};
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
  }

  &[aria-disabled='true'] {
    background: ${colors.textMuted};
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
    pointer-events: none;
  }
`;

export const SecondaryLinkButton = styled(Link)`
  ${baseButton}
  background: ${colors.card};
  color: ${colors.textSecondary};
  border: 2px solid ${colors.gray200};
  text-align: center;

  &:hover:not([aria-disabled='true']) {
    background: ${colors.background};
    border-color: ${colors.textSecondary};
    transform: translateY(-1px);
  }

  &[aria-disabled='true'] {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
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
  transition: ${baseTransition};

  &:hover:not(:disabled) {
    background: ${colors.dangerHover};
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
  transition: ${baseTransition};

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
`;

// Card Components
export const TournamentCard = styled.div`
  background: ${colors.card};
  padding: 32px;
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
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

export const TournamentMeta = styled.div`
  margin: 16px 0;
  color: ${colors.textSecondary};
  font-size: 16px;
  font-weight: 500;

  p {
    margin: 8px 0;
    font-size: 14px;
    color: ${colors.textMuted};
    line-height: 1.4;
  }

  em {
    background: ${colors.background};
    padding: 4px 8px;
    border-radius: 4px;
    font-style: normal;
    display: inline-block;
    margin: 2px 0;
  }
`;

// Progress Components
export const ProgressBar = styled.div`
  background: ${colors.gray200};
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

export const ProgressContainer = styled.div`
  margin: 20px 0;
`;

// Competition Components
export const CompetitionContainer = styled.div`
  overflow-x: auto;
  overflow-y: visible;
  padding: 24px;
  background: ${colors.background};
  border-radius: 12px;
`;

export const CompetitionTree = styled.div`
  display: flex;
  align-items: center;
  gap: 80px;
  min-width: fit-content;
`;

export const CompetitionRound = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: space-around;
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
  margin: 15px 0;
  z-index: 2;
`;

export const MatchContainer = styled.div`
  background: ${colors.card};
  border: 1px solid ${colors.gray200};
  border-radius: 8px;
  width: 200px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
`;

export const MatchParticipant = styled.div<{
  isWinner: boolean;
  isBye?: boolean;
  isUserChoice?: boolean;
}>`
  padding: 12px;
  border-left: ${(props) => {
    if (props.isUserChoice) return `4px solid ${colors.success}`;
    if (props.isWinner) return `4px solid ${colors.primaryLight}`;
    return '4px solid transparent';
  }};
  background: ${(props) => {
    if (props.isBye) return colors.disabled;
    if (props.isUserChoice) return colors.successBackground;
    if (props.isWinner) return colors.backgroundSecondary;
    return 'white';
  }};
  border-bottom: ${(props) =>
    props.isBye ? 'none' : `1px solid ${colors.gray100}`};
  transition: ${baseTransition};

  &:last-child {
    border-bottom: none;
  }
`;

// History Components
export const HistoryCard = styled.div`
  background: ${colors.card};
  border: 1px solid ${colors.gray200};
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  transition: ${baseTransition};
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
          return colors.gray200;
      }
    }};
`;

export const HistoryActions = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

export const HistoryDate = styled.div`
  color: ${colors.textLight};
  font-size: 12px;
  margin-top: 8px;
`;

// Modal Components
export const ModalOverlay = styled.div`
  position: fixed;
  inset: 0;
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
  padding: 24px 32px;
  border-bottom: 1px solid ${colors.gray200};
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
  color: ${colors.textDark};
  transition: ${baseTransition};

  &:hover {
    color: ${colors.textPrimary};
  }
`;

export const ModalBody = styled.div`
  padding: 32px;
`;

// Response Components
export const ResponseGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

export const ResponseText = styled.div`
  font-size: 16px;
  line-height: 1.6;
  color: ${colors.textPrimary};
`;

export const ResponseCard = styled.div<{ disabled?: boolean }>`
  border: 2px solid ${colors.gray200};
  border-radius: 12px;
  padding: 16px;
  background: ${colors.card};
  cursor: ${(props) => (props.disabled ? 'not-allowed' : 'pointer')};
  transition: ${baseTransition};
  opacity: ${(props) => (props.disabled ? 0.6 : 1)};

  &:hover:not([disabled]) {
    border-color: ${colors.primary};
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.15);
  }
`;

export const ParticipantText = styled.div`
  flex: 1;
  line-height: 1.4;
`;

export const VoteCount = styled.div`
  font-size: 12px;
  color: ${colors.textMuted};
  margin-top: 4px;
  font-weight: 500;
`;

// Status Components
export const StatusMessage = styled.div<{
  type: 'success' | 'action' | 'waiting';
}>`
  padding: 16px 20px;
  border-radius: 12px;
  margin: 16px 0 0 0;
  font-weight: 500;
  font-size: 15px;
  text-align: center;
  background: ${(props) => {
    switch (props.type) {
      case 'success':
        return colors.successBackground;
      case 'action':
        return colors.backgroundSecondary;
      case 'waiting':
        return colors.warningBackground;
      default:
        return colors.background;
    }
  }};
  color: ${(props) => {
    switch (props.type) {
      case 'success':
        return colors.successDark;
      case 'action':
        return colors.primaryHover;
      case 'waiting':
        return colors.warningDark;
      default:
        return colors.textSecondary;
    }
  }};
  border: 1px solid
    ${(props) => {
      switch (props.type) {
        case 'success':
          return colors.successBorder;
        case 'action':
          return colors.gray300;
        case 'waiting':
          return colors.warningBorder;
        default:
          return colors.gray200;
      }
    }};
`;

export const ErrorMessage = styled.div`
  background: ${colors.dangerBackground};
  border: 1px solid ${colors.dangerBorder};
  color: ${colors.dangerHover};
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
`;

// Section Components
export const BracketSection = styled.div`
  animation: ${fadeIn} 0.5s ease-out;
  background: ${colors.card};
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
`;

export const TournamentStatsCard = styled.div`
  margin-bottom: 24px;
  padding: 20px;
  background: ${colors.background};
  border-radius: 12px;
  display: flex;
  gap: 32px;
  flex-wrap: wrap;

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 16px;
  }
`;

export const StatItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

export const StatLabel = styled.span`
  font-weight: 600;
  color: ${colors.textPrimary};
  font-size: 14px;
`;

export const StatValue = styled.span<{ winner?: boolean }>`
  color: ${(props) => (props.winner ? colors.success : colors.textSecondary)};
  font-weight: ${(props) => (props.winner ? 700 : 500)};
  font-size: 14px;
`;

// Grid and List Components
export const TournamentGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

export const ResultsSection = styled.div`
  background: ${colors.card};
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
`;

export const ResultsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 24px;
`;

export const ResultItem = styled.div<{ rank: number }>`
  display: flex;
  align-items: center;
  padding: 16px;
  border-radius: 8px;
  background: ${(props) => {
    if (props.rank === 1) return colors.goldBackground;
    if (props.rank === 2) return colors.silverBackground;
    if (props.rank === 3) return colors.bronzeBackground;
    return colors.backgroundTertiary;
  }};
  border: 2px solid
    ${(props) => {
      if (props.rank === 1) return colors.gold;
      if (props.rank === 2) return colors.silver;
      if (props.rank === 3) return colors.bronze;
      return colors.gray300;
    }};
`;

export const ResultRank = styled.div`
  font-size: 24px;
  font-weight: bold;
  margin-right: 16px;
  min-width: 48px;
  text-align: center;
`;

export const ResultContent = styled.div`
  flex: 1;
`;

export const ResultPrompt = styled.div`
  font-weight: 600;
  margin-bottom: 8px;
  color: ${colors.textDark};
`;

export const ResultStats = styled.div`
  display: flex;
  gap: 16px;
`;

export const ResultStat = styled.div`
  color: ${colors.textLight};
  font-size: 14px;
`;

// Empty State Components
export const EmptyState = styled.div`
  text-align: center;
  padding: 64px 24px;
`;

export const EmptyStateIcon = styled.div`
  font-size: 64px;
  margin-bottom: 16px;
`;

export const EmptyStateTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  color: ${colors.textDark};
  margin-bottom: 8px;
`;

export const EmptyStateText = styled.p`
  color: ${colors.textLight};
  margin-bottom: 24px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
`;

export const BracketPlaceholder = styled.div`
  text-align: center;
  padding: 64px 24px;
  color: ${colors.textLight};
  font-size: 18px;
  background: ${colors.backgroundTertiary};
  border-radius: 8px;
  border: 2px dashed ${colors.gray300};
`;

export const PromptText = styled.div`
  font-weight: 600;
  color: ${colors.textDark};
  margin-bottom: 8px;
  font-size: 14px;
`;

// Selector Components
export const SelectorContainer = styled.div<{
  isOpen: boolean;
  hasError?: boolean;
}>`
  position: relative;
  background: white;
  border: 2px solid
    ${(props) =>
      props.hasError
        ? colors.danger
        : props.isOpen
          ? colors.primaryLight
          : colors.gray200};
  border-radius: 12px;
  transition: ${baseTransition};
  box-shadow: ${(props) =>
    props.isOpen
      ? '0 4px 12px rgba(59, 130, 246, 0.15)'
      : '0 1px 3px rgba(0, 0, 0, 0.1)'};

  &:hover {
    border-color: ${(props) =>
      props.hasError ? colors.danger : colors.gray300};
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

export const SelectedArea = styled.div`
  padding: 12px 16px;
  min-height: 48px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  cursor: pointer;
`;

export const ModelChip = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: ${colors.success};
  color: white;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
  transition: ${baseTransition};

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
  }
`;

export const RemoveChip = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  transition: ${baseTransition};

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
`;

export const SearchInput = styled.input`
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: ${colors.textDark};
  flex: 1;
  min-width: 150px;
  padding: 4px 0;

  &::placeholder {
    color: ${colors.textMuted};
  }
`;

export const Dropdown = styled.div<{ isOpen: boolean }>`
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid ${colors.gray200};
  border-radius: 12px;
  box-shadow:
    0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
  z-index: 1000;
  overflow: hidden;
  opacity: ${(props) => (props.isOpen ? 1 : 0)};
  transform: ${(props) =>
    props.isOpen ? 'translateY(0) scale(1)' : 'translateY(-8px) scale(0.95)'};
  transition: all 0.2s ease;
  display: ${(props) => (props.isOpen ? 'block' : 'none')};
`;

export const DropdownContent = styled.div`
  max-height: 300px;
  overflow-y: auto;
  padding: 8px;
`;

export const ModelOption = styled.div<{
  isSelected: boolean;
  isHighlighted: boolean;
}>`
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 4px;
  transition: all 0.15s ease;
  background: ${(props) => {
    if (props.isHighlighted) return colors.gray50;
    if (props.isSelected) return colors.successLight;
    return 'transparent';
  }};
  border: 2px solid
    ${(props) => (props.isSelected ? colors.success : 'transparent')};

  &:hover {
    background: ${colors.gray50};
    transform: translateX(4px);
  }

  &:last-child {
    margin-bottom: 0;
  }
`;

export const ModelInfo = styled.div`
  flex: 1;
`;

export const ModelName = styled.div`
  font-weight: 600;
  color: ${colors.textPrimary};
  font-size: 14px;
  margin-bottom: 2px;
`;

export const ModelId = styled.div`
  font-size: 12px;
  color: ${colors.textLight};
  font-family: ${monoFont};
`;

export const CheckIcon = styled.div`
  color: ${colors.success};
  font-size: 18px;
  font-weight: bold;
`;
