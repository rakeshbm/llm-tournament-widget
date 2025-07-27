import math
import random

from flask import current_app
import requests

LLM_MODEL = "mistralai/mistral-7b-instruct"

def generate_llm_response(prompt, question):
    try:
        headers = {
            "Authorization": f"Bearer {current_app.config["OPENROUTER_API_KEY"]}",
            "Content-Type": "application/json",
            "X-Title": "LLM Tournament Widget",
        }

        data = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"Error generating response: {str(e)}"

def create_bracket(prompts):
    num_prompts = len(prompts)
    bracket_size = 2 ** math.ceil(math.log2(num_prompts))
    
    # Randomize prompt indices
    shuffled_indices = list(range(num_prompts))
    random.shuffle(shuffled_indices)
    
    # Create initial participant list with strategic bye placement
    participants = shuffled_indices[:]
    byes_needed = bracket_size - num_prompts
    
    # Insert byes at positions that will distribute them across different bracket paths
    # This ensures no single participant gets multiple byes
    bye_positions = []
    if byes_needed > 0:
        # Calculate positions to insert byes to spread them out
        step = bracket_size // byes_needed
        for i in range(byes_needed):
            pos = i * step + (step // 2)  # Distribute evenly
            bye_positions.append(pos)
    
    # Build initial bracket with byes distributed
    full_bracket_participants = []
    bye_index = 0
    participant_index = 0
    
    for i in range(bracket_size):
        if bye_index < len(bye_positions) and i == bye_positions[bye_index]:
            full_bracket_participants.append(-1)  # -1 = Bye
            bye_index += 1
        else:
            if participant_index < len(participants):
                full_bracket_participants.append(participants[participant_index])
                participant_index += 1
            else:
                full_bracket_participants.append(-1)  # Fill remaining with byes
    
    bracket = []
    current_participants = full_bracket_participants[:]
    
    # Build all rounds
    while len(current_participants) > 1:
        round_matches = []
        next_participants = []
        
        # Create matches for this round
        for i in range(0, len(current_participants), 2):
            p1 = current_participants[i]
            p2 = current_participants[i + 1] if i + 1 < len(current_participants) else -1
            
            # Determine winner
            winner = None
            if p1 == -1 and p2 == -1:
                winner = -1  # Both bye
            elif p1 == -1:
                winner = p2  # p2 advances
            elif p2 == -1:
                winner = p1  # p1 advances
            # If both are real participants, winner stays None (needs voting)
            
            match = {
                'participant1': p1,
                'participant2': p2,
                'winner': winner
            }
            
            round_matches.append(match)
            
            # Add to next round
            if winner is not None:
                next_participants.append(winner)
            else:
                next_participants.append(None)  # Placeholder for voting result
        
        bracket.append(round_matches)
        current_participants = next_participants
    
    return bracket
