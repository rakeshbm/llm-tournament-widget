import { ReactNode } from 'react';
import * as Styled from '../styles';

export interface EmptyStateProps {
  icon?: ReactNode;
  title?: string;
  description: ReactNode;
}

export function EmptyState({ icon, title, description }: EmptyStateProps) {
  return (
    <Styled.EmptyState>
      <Styled.EmptyStateIcon>{icon}</Styled.EmptyStateIcon>
      <Styled.EmptyStateTitle>{title}</Styled.EmptyStateTitle>
      <Styled.EmptyStateText>{description}</Styled.EmptyStateText>
    </Styled.EmptyState>
  );
}

EmptyState.displayName = 'EmptyState';
