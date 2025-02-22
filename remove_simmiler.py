import json
import spacy
from collections import defaultdict
from fuzzywuzzy import fuzz

# Load NLP model
nlp = spacy.load("en_core_web_md")

# Initialize the dictionary to store duplicate answers
duplicate_answers = defaultdict(list)
unrelated_answers = []

# Load dataset from JSONL file (one JSON object per line)
with open("dataset/study_abroad_dataset.jsonl", "r", encoding="utf-8") as file:
    dataset = []
    for line in file.readlines():
        try:
            data = json.loads(line.strip())
            dataset.append(data)
        except json.JSONDecodeError:
            print("Skipping invalid line: ", line)

# Debug: Print the first entry to check its structure
if dataset:
    print("First entry in dataset:", dataset[0])

# Compare all Q&A pairs
for i in range(len(dataset)):
    # Check if 'conversations' key exists
    if "conversations" not in dataset[i]:
        print(f"Skipping entry {i} due to missing 'conversations'.")
        continue
    
    # Loop through the conversations list
    for conv in dataset[i]["conversations"]:
        if conv["from"] == "human":  # Question
            question_i = conv["value"]
        elif conv["from"] == "assistant":  # Answer
            answer_i = conv["value"]
            
            # Convert the answer to an NLP object (embedding)
            doc_i = nlp(answer_i)
            
            for j in range(i + 1, len(dataset)):
                if "conversations" not in dataset[j]:
                    print(f"Skipping entry {j} due to missing 'conversations'.")
                    continue
                
                # Loop through the conversations list
                for conv2 in dataset[j]["conversations"]:
                    if conv2["from"] == "human":  # Question
                        question_j = conv2["value"]
                    elif conv2["from"] == "assistant":  # Answer
                        answer_j = conv2["value"]
                        
                        # Check for duplicate answers (fuzzy matching)
                        similarity = fuzz.ratio(answer_i, answer_j)
                        if similarity > 90 and question_i != question_j:  # Same answer for different questions
                            duplicate_answers[question_i].append(question_j)

                        # Check if answer is relevant to the question (semantic similarity)
                        doc_j = nlp(question_j)
                        if doc_i.similarity(doc_j) < 0.5:  # Low semantic similarity between answer and question
                            unrelated_answers.append((question_j, answer_j))

# Print results

# Handle duplicate answers
if duplicate_answers:
    print("🚨 Duplicate Answers Found:")
    for q, dups in duplicate_answers.items():
        print(f"\n❌ Question: {q}\n  → Duplicate Answers Used for: {', '.join(dups)}")
else:
    print("No duplicate answers detected.")

# Handle unrelated answers
if unrelated_answers:
    print("\n🚨 Unrelated Answers Detected:")
    for q, a in unrelated_answers:
        print(f"\n❌ Question: {q}\n  → Answer: {a}")
else:
    print("No unrelated answers detected.")
