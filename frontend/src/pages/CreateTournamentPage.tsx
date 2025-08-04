import { useState, useCallback } from 'react';
import { useCreateTournament } from '../hooks';
import * as Styled from '../styles';
import { CreateTournamentRequest } from '../types';
import { useNavigate } from 'react-router-dom';
import { Loader } from '../components';

export const CreateTournamentPage = () => {
  const [question, setQuestion] = useState('');
  const [prompts, setPrompts] = useState(['', '']);
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

  const addPrompt = useCallback(() => {
    if (prompts.length < 8) {
      setPrompts((prev) => [...prev, '']);
    }
  }, [prompts.length]);

  const removePrompt = useCallback(
    (index: number) => {
      if (prompts.length > 2) {
        setPrompts((prev) => prev.filter((_, i) => i !== index));
      }
    },
    [prompts.length]
  );

  const updatePrompt = useCallback((index: number, value: string) => {
    setPrompts((prev) => {
      const updated = [...prev];
      updated[index] = value;
      return updated;
    });
  }, []);

  const handleSubmit = useCallback(() => {
    const validPrompts = prompts.filter((p) => p.trim());
    if (question.trim() && validPrompts.length >= 2) {
      const createTournamentRequest: CreateTournamentRequest = {
        question: question.trim(),
        prompts: validPrompts,
      };
      handleCreateTournament(createTournamentRequest);
    }
  }, [question, prompts, handleCreateTournament]);

  const canSubmit =
    question.trim() && prompts.every((p) => p.trim()) && !isPending;

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
            <Styled.PromptRow key={index}>
              <Styled.TextArea
                rows={2}
                placeholder={`Prompt ${index + 1}`}
                value={prompt}
                onChange={(e) => updatePrompt(index, e.target.value)}
                disabled={isPending}
              />
              <Styled.RemoveButton
                onClick={() => removePrompt(index)}
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
              {' '}
              Submit
            </Styled.PrimaryButton>
          </Styled.ButtonRow>
        </Styled.FormGroup>
      </Styled.CreatorContainer>
    </>
  );
};
