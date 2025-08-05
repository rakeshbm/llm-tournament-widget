import { useState, useCallback } from 'react';
import { useCreateTournament } from '../hooks';
import * as Styled from '../styles';
import { CreateTournamentRequest } from '../types';
import { useNavigate } from 'react-router-dom';
import { Loader } from '../components';

interface PromptItem {
  id: string;
  value: string;
}

export const CreateTournamentPage = () => {
  const [question, setQuestion] = useState('');
  const [prompts, setPrompts] = useState<PromptItem[]>([
    { id: crypto.randomUUID(), value: '' },
    { id: crypto.randomUUID(), value: '' }
  ]);
  const { mutate: createTournament, isPending } = useCreateTournament();
  const navigate = useNavigate();

  const handleCreateTournament = useCallback(
    (tournamentData: CreateTournamentRequest) => {
      createTournament(tournamentData, {
        onSuccess: (createdTournament) => {
          navigate(`/tournaments/${createdTournament.id}`, { replace: true });
        },
        onError: (error) => {
          console.error('Error creating tournament:', error);
        },
      });
    },
    [createTournament, navigate]
  );

  const handleSubmit = useCallback(() => {
    const validPrompts = prompts
      .map(p => p.value.trim())
      .filter(p => p.length > 0);
    
    if (question.trim() && validPrompts.length >= 2) {
      const createTournamentRequest: CreateTournamentRequest = {
        question: question.trim(),
        prompts: validPrompts,
      };
      handleCreateTournament(createTournamentRequest);
    }
  }, [question, prompts, handleCreateTournament]);

  const addPrompt = () => {
    if (prompts.length < 8) {
      setPrompts(prev => [...prev, { id: crypto.randomUUID(), value: '' }]);
    }
  };

  const removePrompt = (id: string) => {
    if (prompts.length > 2) {
      setPrompts(prev => prev.filter(prompt => prompt.id !== id));
    }
  };

  const updatePrompt = (id: string, value: string) => {
    setPrompts(prev => 
      prev.map(prompt => 
        prompt.id === id ? { ...prompt, value } : prompt
      )
    );
  };

  const canSubmit =
    question.trim() && 
    prompts.every(p => p.value.trim()) && 
    !isPending;

  return (
    <>
      {isPending && <Loader text="Please wait. Creating tournament..." />}
      <Styled.CreatorContainer>
        <Styled.SectionTitle>Create New Tournament</Styled.SectionTitle>

        <Styled.FormGroup>
          <Styled.Label>Question for all prompts to answer</Styled.Label>
          <Styled.PromptRow>
            <Styled.TextArea
              rows={3}
              placeholder="e.g., Explain quantum computing in simple terms"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={isPending}
            />
          </Styled.PromptRow>
        </Styled.FormGroup>

        <Styled.FormGroup>
          <Styled.Label>Competing Prompts (2-8 prompts)</Styled.Label>
          {prompts.map((prompt, index) => (
            <Styled.PromptRow key={prompt.id}>
              <Styled.TextArea
                rows={2}
                placeholder={`Prompt ${index + 1}`}
                value={prompt.value}
                onChange={(e) => updatePrompt(prompt.id, e.target.value)}
                disabled={isPending}
              />
              <Styled.RemoveButton
                onClick={() => removePrompt(prompt.id)}
                disabled={prompts.length <= 2 || isPending}
              >
                ×
              </Styled.RemoveButton>
            </Styled.PromptRow>
          ))}

          <Styled.ButtonRow>
            <Styled.SecondaryButton
              onClick={addPrompt}
              disabled={prompts.length >= 8 || isPending}
            >
              Add Prompt
            </Styled.SecondaryButton>
            <Styled.PrimaryButton onClick={handleSubmit} disabled={!canSubmit}>
              Submit
            </Styled.PrimaryButton>
          </Styled.ButtonRow>
        </Styled.FormGroup>
      </Styled.CreatorContainer>
    </>
  );
};