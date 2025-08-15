import React, { useState, useRef, useEffect, memo } from 'react';
import * as Styled from '../styles';

interface MultiModelSelectorProps {
  availableModels: Record<string, string>;
  selectedModels: string[];
  onSelectionChange: (models: string[]) => void;
  disabled?: boolean;
  error?: string;
}

export const MultiModelSelector = ({
  availableModels,
  selectedModels,
  onSelectionChange,
  disabled = false,
  error,
}: MultiModelSelectorProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const filteredModels = Object.entries(availableModels).filter(
    ([id, name]) =>
      name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setSearchTerm('');
        setHighlightedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (disabled) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else {
          setHighlightedIndex((prev) =>
            prev < filteredModels.length - 1 ? prev + 1 : 0
          );
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (isOpen) {
          setHighlightedIndex((prev) =>
            prev > 0 ? prev - 1 : filteredModels.length - 1
          );
        }
        break;
      case 'Enter':
        e.preventDefault();
        if (isOpen && highlightedIndex >= 0) {
          const [modelId] = filteredModels[highlightedIndex];
          toggleModel(modelId);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setSearchTerm('');
        setHighlightedIndex(-1);
        break;
      case 'Backspace':
        if (searchTerm === '' && selectedModels.length > 0) {
          onSelectionChange(selectedModels.slice(0, -1));
        }
        break;
    }
  };

  const toggleModel = (modelId: string) => {
    if (selectedModels.includes(modelId)) {
      onSelectionChange(selectedModels.filter((id) => id !== modelId));
    } else if (selectedModels.length < 4) {
      // limit to 4 selections
      onSelectionChange([...selectedModels, modelId]);
    }
    setSearchTerm('');
    setHighlightedIndex(-1);
    inputRef.current?.focus();
  };

  const removeModel = (modelId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onSelectionChange(selectedModels.filter((id) => id !== modelId));
  };

  return (
    <Styled.Container ref={containerRef}>
      <Styled.Label>Models (max 4)</Styled.Label>

      <Styled.SelectorContainer isOpen={isOpen} hasError={!!error}>
        <Styled.SelectedArea
          onClick={() => {
            if (!disabled) {
              setIsOpen(true);
              inputRef.current?.focus();
            }
          }}
        >
          {selectedModels.map((modelId) => (
            <Styled.ModelChip key={modelId}>
              {availableModels[modelId] || modelId}
              <Styled.RemoveChip
                onClick={(e) => removeModel(modelId, e)}
                disabled={disabled}
              >
                ×
              </Styled.RemoveChip>
            </Styled.ModelChip>
          ))}

          <Styled.SearchInput
            ref={inputRef}
            type="text"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setIsOpen(true);
              setHighlightedIndex(-1);
            }}
            placeholder={selectedModels.length === 0 ? 'Select models' : ''}
            disabled={disabled}
            onKeyDown={handleKeyDown}
            onFocus={() => !disabled && setIsOpen(true)}
          />
        </Styled.SelectedArea>
      </Styled.SelectorContainer>

      <Styled.Dropdown isOpen={isOpen && !disabled}>
        <Styled.DropdownContent>
          {filteredModels.length === 0
            ? 'No models available'
            : filteredModels.map(([modelId, modelName], index) => {
                const isSelected = selectedModels.includes(modelId);
                const isHighlighted = index === highlightedIndex;

                return (
                  <Styled.ModelOption
                    key={modelId}
                    isSelected={isSelected}
                    isHighlighted={isHighlighted}
                    onClick={() => {
                      if (isSelected || selectedModels.length < 4) {
                        toggleModel(modelId);
                      }
                    }}
                    onMouseEnter={() => setHighlightedIndex(index)}
                  >
                    <Styled.ModelInfo>
                      <Styled.ModelName>{modelName}</Styled.ModelName>
                      <Styled.ModelId>{modelId}</Styled.ModelId>
                    </Styled.ModelInfo>
                    {isSelected && <Styled.CheckIcon>✓</Styled.CheckIcon>}
                  </Styled.ModelOption>
                );
              })}
        </Styled.DropdownContent>
      </Styled.Dropdown>
    </Styled.Container>
  );
};

MultiModelSelector.displayName = 'MultiModelSelector';
