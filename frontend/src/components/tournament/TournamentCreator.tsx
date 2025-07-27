import { useState } from 'react';
import * as Styled from '../../styles';

interface TournamentCreatorProps {
  onCreateTournament: (question: string, prompts: string[]) => void;
  loading: boolean;
}

export function TournamentCreator({
  onCreateTournament,
  loading,
}: TournamentCreatorProps) {
  const [question, setQuestion] = useState('');
  const [prompts, setPrompts] = useState(['', '']);

  const addPrompt = () => {
    if (prompts.length < 16) {
      setPrompts([...prompts, '']);
    }
  };

  const removePrompt = (index: number) => {
    if (prompts.length > 2) {
      setPrompts(prompts.filter((_, i) => i !== index));
    }
  };

  const updatePrompt = (index: number, value: string) => {
    const updated = [...prompts];
    updated[index] = value;
    setPrompts(updated);
  };

  const handleSubmit = () => {
    const validPrompts = prompts.filter((p) => p.trim());
    if (question.trim() && validPrompts.length >= 2) {
      onCreateTournament(question.trim(), validPrompts);
    }
  };

  const canSubmit =
    question.trim() && prompts.every((p) => p.trim()) && !loading;

  return (
    <Styled.CreatorContainer>
      <Styled.SectionTitle>Set Up Your Tournament</Styled.SectionTitle>

      <Styled.FormGroup>
        <Styled.Label>Tournament Question</Styled.Label>
        <Styled.PromptRow>
          <Styled.TextArea
            rows={3}
            placeholder={`Enter the question that all prompts should answer (e.g., Explain the impact of climate change on agriculture)`}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
        </Styled.PromptRow>
      </Styled.FormGroup>

      <Styled.FormGroup>
        <Styled.Label>Competing Prompts (min 2, max 16)</Styled.Label>

        {prompts.map((prompt, index) => (
          <Styled.PromptRow key={index}>
            <Styled.TextArea
              rows={2}
              placeholder={`Enter prompt ${index + 1}`}
              value={prompt}
              onChange={(e) => updatePrompt(index, e.target.value)}
            />
            <Styled.RemoveButton
              onClick={() => removePrompt(index)}
              disabled={prompts.length <= 2}
            >
              ×
            </Styled.RemoveButton>
          </Styled.PromptRow>
        ))}

        <Styled.ButtonRow>
          <Styled.SecondaryButton
            onClick={addPrompt}
            disabled={prompts.length >= 16}
          >
            Add Another Prompt
          </Styled.SecondaryButton>

          <Styled.PrimaryButton onClick={handleSubmit} disabled={!canSubmit}>
            {loading ? 'Starting Tournament...' : 'Begin Tournament'}
          </Styled.PrimaryButton>
        </Styled.ButtonRow>
      </Styled.FormGroup>
    </Styled.CreatorContainer>
  );
}
