# evaluate.py
import pandas as pd
import torch
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from tqdm import tqdm

def evaluate():
    # Load test data
    df = pd.read_csv("test.csv")  # expects 'text' and 'label' columns
    texts = df["text"].tolist()
    labels = df["label"].tolist()

    # Load tokenizer and model from current directory
    tokenizer = AutoTokenizer.from_pretrained(".")
    model = AutoModelForSequenceClassification.from_pretrained(".")
    model.eval()

    preds = []

    with torch.no_grad():
        for text in tqdm(texts, desc="Evaluating"):
            inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
            outputs = model(**inputs)
            logits = outputs.logits
            pred = torch.argmax(logits, dim=1).item()
            preds.append(pred)

    # Compute metrics
    accuracy = accuracy_score(labels, preds)
    precision = precision_score(labels, preds, average="weighted", zero_division=0)
    recall = recall_score(labels, preds, average="weighted", zero_division=0)
    f1 = f1_score(labels, preds, average="weighted", zero_division=0)

    # Save to results.json
    results = {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4)
    }

    with open("results.json", "w") as f:
        json.dump(results, f)

    print("Evaluation complete. Results saved to results.json")

if __name__ == "__main__":
    evaluate()
