import * as Styled from '../styles';

export const HomePage = () => {
  return (
    <Styled.AppContainer>
      <Styled.Container>
        <Styled.Header>
          <Styled.Title>LLM Prompt Tournament</Styled.Title>
          <Styled.Subtitle>
            Discover which prompts work best through head-to-head competition
          </Styled.Subtitle>
          <Styled.Description>
            Test multiple prompts against the same question and let voting
            determine the winner. Perfect for finding the most effective prompt
            variations.
          </Styled.Description>
        </Styled.Header>

        <Styled.ButtonGroup>
          <Styled.PrimaryLinkButton to="/tournaments">
            View Tournaments
          </Styled.PrimaryLinkButton>

          <Styled.SecondaryLinkButton to="/tournaments/create">
            Create New Tournament
          </Styled.SecondaryLinkButton>
        </Styled.ButtonGroup>
      </Styled.Container>
    </Styled.AppContainer>
  );
};
