import { useState, useCallback, useMemo } from 'react';
import { useCreateTournament, useAvailableModels } from '../hooks';
import * as Styled from '../styles';
import { CreateTournamentRequest } from '../types';
import { useNavigate } from 'react-router-dom';
import { Loader, MultiModelSelector } from '../components';

interface PromptItem {
  id: string;
  text: string;
}

export const CreateTournamentPage = () => {
  const [question, setQuestion] = useState('');
  const [prompts, setPrompts] = useState<PromptItem[]>([
    { id: crypto.randomUUID(), text: '' },
  ]);
  const [models, setModels] = useState<string[]>([]);

  const { data: modelsData, isLoading: modelsLoading } = useAvailableModels();
  const { mutate: createTournament, isPending } = useCreateTournament();
  const navigate = useNavigate();

  const availableModels = modelsData?.models || {};

  // Calculate total prompt-model combinations
  const totalCombinations = useMemo(() => {
    const validPrompts = prompts.filter((p) => p.text.trim());
    return validPrompts.length * models.length;
  }, [prompts, models]);

  const handleSubmit = useCallback(() => {
    const combinations = new Set<string>();
    const formattedPrompts: Array<{ text: string; model: string }> = [];

    prompts
      .filter((p) => p.text.trim() && models.length > 0)
      .forEach((prompt) => {
        models.forEach((model) => {
          const key = `${prompt.text.trim()}|${model}`;
          if (!combinations.has(key)) {
            combinations.add(key);
            formattedPrompts.push({
              text: prompt.text.trim(),
              model,
            });
          }
        });
      });

    if (question.trim() && formattedPrompts.length >= 2) {
      const request: CreateTournamentRequest = {
        question: question.trim(),
        prompts: formattedPrompts,
      };

      createTournament(request, {
        onSuccess: (tournament) => {
          navigate(`/tournaments/${tournament.id}`, { replace: true });
        },
        onError: (error) => {
          console.error('Error creating tournament:', error);
        },
      });
    }
  }, [question, prompts, models, createTournament, navigate]);

  const addPrompt = () => {
    if (prompts.length < 4) {
      setPrompts((prev) => [...prev, { id: crypto.randomUUID(), text: '' }]);
    }
  };

  const removePrompt = (id: string) => {
    if (prompts.length > 1) {
      setPrompts((prev) => prev.filter((prompt) => prompt.id !== id));
    }
  };

  const updatePromptText = (id: string, text: string) => {
    setPrompts((prev) =>
      prev.map((prompt) => (prompt.id === id ? { ...prompt, text } : prompt))
    );
  };

  const canSubmit =
    question.trim() && totalCombinations >= 2 && !isPending && !modelsLoading;

  return (
    <>
      {isPending && <Loader text="Creating your tournament..." />}
      <Styled.CreatorContainer>
        <Styled.SectionTitle>Create Tournament</Styled.SectionTitle>
        <Styled.Subtitle>
          Set up a new LLM tournament to compare different prompts and models.
          Each prompt-model combination will compete in a bracket-style
          tournament. You need at least 2 combinations (e.g., 1 prompt and 2
          models or 2 prompts and 1 model).
        </Styled.Subtitle>
        <br />

        <Styled.FormGroup>
          <Styled.Label>Tournament Question</Styled.Label>
          <Styled.PromptRow>
            <Styled.TextArea
              rows={3}
              placeholder="What should all the AI models respond to? e.g., 'Explain quantum computing in simple terms'"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={isPending}
            />
          </Styled.PromptRow>
        </Styled.FormGroup>

        <MultiModelSelector
          availableModels={availableModels}
          selectedModels={models}
          onSelectionChange={setModels}
          disabled={isPending || modelsLoading}
        />

        <Styled.FormGroup>
          <Styled.Label>Prompts (max 4)</Styled.Label>
          {prompts.map((prompt, index) => (
            <Styled.PromptRow key={prompt.id}>
              <Styled.TextArea
                placeholder={`Enter prompt ${index + 1}`}
                value={prompt.text}
                onChange={(e) => updatePromptText(prompt.id, e.target.value)}
                disabled={isPending}
              />
              <Styled.RemoveButton
                onClick={() => removePrompt(prompt.id)}
                disabled={prompts.length <= 1 || isPending}
              >
                ×
              </Styled.RemoveButton>
            </Styled.PromptRow>
          ))}
        </Styled.FormGroup>

        <Styled.ButtonRow>
          <Styled.SecondaryButton
            onClick={addPrompt}
            disabled={prompts.length >= 4 || isPending}
          >
            + Add Prompt
          </Styled.SecondaryButton>
          <Styled.PrimaryButton
            onClick={handleSubmit}
            disabled={!canSubmit}
            title={
              !canSubmit && totalCombinations < 2
                ? 'Need at least 2 prompt-model combinations'
                : undefined
            }
          >
            Submit
          </Styled.PrimaryButton>
        </Styled.ButtonRow>
      </Styled.CreatorContainer>
    </>
  );
};
