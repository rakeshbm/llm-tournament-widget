import { useState } from 'react';
import * as Styled from '../../styles';

interface TournamentCreatorProps {
  onCreateTournament: (question: string, prompts: string[]) => void;
  loading: boolean;
}

export function TournamentCreator({ onCreateTournament, loading }: TournamentCreatorProps) {
  const [question, setQuestion] = useState('');
  const [prompts, setPrompts] = useState(['', '']);

  const addPrompt = () => setPrompts([...prompts, '']);
  
  const removePrompt = (index: number) => {
    if (prompts.length > 2) {
      setPrompts(prompts.filter((_, i) => i !== index));
    }
  };

  const updatePrompt = (index: number, value: string) => {
    const newPrompts = [...prompts];
    newPrompts[index] = value;
    setPrompts(newPrompts);
  };

  const handleSubmit = () => {
    if (question.trim() && prompts.every(p => p.trim())) {
      onCreateTournament(question, prompts.filter(p => p.trim()));
    }
  };

  return (
    <Styled.CreatorContainer>
      <Styled.SectionTitle>Create Tournament</Styled.SectionTitle>

      <Styled.FormGroup>
        <Styled.Label>Question</Styled.Label>
        <Styled.TextArea
          rows={3}
          placeholder="What question should all prompts answer?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
      </Styled.FormGroup>

      <Styled.FormGroup>
        <Styled.Label>Prompts ({prompts.length})</Styled.Label>

        {prompts.map((prompt, index) => (
          <Styled.PromptRow key={index}>
            <Styled.TextArea
              rows={2}
              placeholder={`Prompt ${index + 1}`}
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
          <Styled.SecondaryButton onClick={addPrompt}>
            + Add Prompt
          </Styled.SecondaryButton>

          <Styled.PrimaryButton
            onClick={handleSubmit}
            disabled={loading || !question.trim() || !prompts.every(p => p.trim())}
          >
            {loading ? 'Creating...' : 'Start Tournament'}
          </Styled.PrimaryButton>
        </Styled.ButtonRow>
      </Styled.FormGroup>
    </Styled.CreatorContainer>
  );
}
