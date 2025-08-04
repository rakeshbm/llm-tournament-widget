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
        print(f"Error generating response: {str(e)}")
        return None

def create_bracket(prompts):
    num_prompts = len(prompts)
    if num_prompts < 2:
        raise ValueError("At least 2 prompts required")

    bracket_size = 2 ** math.ceil(math.log2(num_prompts))
    byes_needed = bracket_size - num_prompts
    shuffled_indices = list(range(num_prompts))
    random.shuffle(shuffled_indices)

    # Distribute byes evenly
    bye_positions = set()
    if byes_needed > 0:
        step = bracket_size // byes_needed
        bye_positions = { (i * step) % bracket_size for i in range(byes_needed) }

    # Build initial participants with byes
    participants = []
    prompt_iter = iter(shuffled_indices)
    for i in range(bracket_size):
        if i in bye_positions:
            participants.append(-1)  # Bye
        else:
            participants.append(next(prompt_iter))

    # Build rounds
    bracket = []
    current_round = participants
    while len(current_round) > 1:
        next_round = []
        round_matches = []
        
        for i in range(0, len(current_round), 2):
            p1, p2 = current_round[i], current_round[i+1] if i+1 < len(current_round) else -1
            match = {
                'participant1': p1,
                'participant2': p2,
                'winner': p2 if p1 == -1 else p1 if p2 == -1 else None
            }
            round_matches.append(match)
            next_round.append(match['winner'] if match['winner'] is not None else None)
        
        bracket.append(round_matches)
        current_round = next_round

    return bracket
