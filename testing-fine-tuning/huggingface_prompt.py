import os 
import openai
import random
import json
from pathlib import Path
from datasets import Dataset, DatasetDict
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parent.parent / "ExpoProject" / ".env"

load_dotenv(dotenv_path=dotenv_path)

openai.api_key = os.getenv("EXPO_PUBLIC_OPEN_AI_KEY")

HF_USER_ORG = "Cesarj66"
DATASET_NAME = "quote-category-detection"

POSITIVE_PROMPT = """You are a quote generation expert creating examples for training a language model.

Generate 10 short, original quotes that clearly match the category: {CONSTRUCT}.
The quote should be 1–2 lines long and fit the definition of this category:
- Statement: Neutral observation or assertion
- Imperative: Call to action or advice
- Question: Rhetorical or probing question
- Analogy/Metaphor: Figurative comparison
- Justification: Explanation or reason
- Warning: Cautionary or preventive message
- Encouragement: Motivational or supportive statement

Only include the quotes, one per line. No explanations.
"""

NEGATIVE_PROMPT = """Give me 5 short original quotes that sound like literary or political sayings, 
but do NOT clearly fit into categories like question, imperative, warning, encouragement, etc.
They should not demonstrate any of the listed rhetorical categories.

Only include the quotes, one per line. No explanations.
"""

def call_openai(prompt, model="gpt-4", temperature=0.9):
    # Call OpenAI Chat API.
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response["choices"][0]["message"]["content"]

def parse_quotes_to_list(output_text):
    lines = output_text.strip().split("\n")
    quotes = []
    for line in lines:
        line = line.strip("-—•* ").strip('"')
        if line:
            quotes.append(line)
    return quotes


# Generation Pipeline
def generate_construct_examples(construct, num_pos_sets=10):
    pos_data = []

    for _ in range(num_pos_sets):
        pos_prompt = POSITIVE_PROMPT.format(CONSTRUCT=construct)
        pos_text = call_openai(pos_prompt)
        pos_quotes = parse_quotes_to_list(pos_text)
        pos_data.extend([{"text": q, "label": construct} for q in pos_quotes])

    return pos_data

def generate_negative_examples(num_sets=15):
    
    neg_data = []
    for _ in range(num_sets):
        neg_text = call_openai(NEGATIVE_PROMPT)
        neg_quotes = parse_quotes_to_list(neg_text)
        neg_data.extend([{"text": q, "label": "NoCategory"} for q in neg_quotes])
    return neg_data

if __name__ == "__main__":
    # Define classification categories
    constructs = ["Statement", "Imperative", "Question", "Analogy/Metaphor", "Justification", "Warning", "Encouragement"]

    all_examples = []

    neg_examples = generate_negative_examples(num_sets=15)
    all_examples.extend(neg_examples)

    for c in constructs:
        pos = generate_construct_examples(c, num_pos_sets=10)
        all_examples.extend(pos)

    random.shuffle(all_examples)

    # Convert to Hugging Face Dataset
    full_dataset = Dataset.from_list(all_examples)

    n = len(full_dataset)
    train_size = int(0.8 * n)
    valid_size = int(0.1 * n)
    test_size = n - train_size - valid_size

    train_dataset = full_dataset.select(range(train_size))
    valid_dataset = full_dataset.select(range(train_size, train_size + valid_size))
    test_dataset = full_dataset.select(range(train_size + valid_size, n))

    dataset_dict = DatasetDict({
        "train": train_dataset,
        "validation": valid_dataset,
        "test": test_dataset
    })

    dataset_dict.push_to_hub(f"{HF_USER_ORG}/{DATASET_NAME}", private=True)
    print("Dataset uploaded to Hugging Face Hub!")
