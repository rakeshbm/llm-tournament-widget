import { memo } from 'react';
import * as Styled from '../styles';

interface LoaderProps {
  text?: string;
}

export const Loader = memo<LoaderProps>(({ text = 'Please wait...' }) => {
  return (
    <Styled.LoadingOverlay>
      <Styled.LoadingContent>
        <Styled.LoadingSpinner />
        {text && <Styled.LoadingText>{text}</Styled.LoadingText>}
      </Styled.LoadingContent>
    </Styled.LoadingOverlay>
  );
});
