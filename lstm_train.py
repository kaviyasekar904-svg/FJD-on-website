import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import CountVectorizer
from preprocessing import load_and_prepare_data

# -------------------------
# Load dataset
# -------------------------
df = load_and_prepare_data()

train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["job_content"],
    df["label"],
    test_size=0.2,
    random_state=42,
    stratify=df["label"]
)

# -------------------------
# Convert text to numeric (Bag of Words)
# -------------------------
vectorizer = CountVectorizer(max_features=5000)

X_train = vectorizer.fit_transform(train_texts).toarray()
X_val = vectorizer.transform(val_texts).toarray()

X_train = torch.tensor(X_train, dtype=torch.float32)
X_val = torch.tensor(X_val, dtype=torch.float32)

y_train = torch.tensor(train_labels.values, dtype=torch.long)
y_val = torch.tensor(val_labels.values, dtype=torch.long)

# -------------------------
# LSTM Model
# -------------------------
class LSTMModel(nn.Module):
    def __init__(self, input_size):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, 64, batch_first=True)
        self.fc = nn.Linear(64, 2)

    def forward(self, x):
        x = x.unsqueeze(1)  # add sequence dimension
        _, (hidden, _) = self.lstm(x)
        out = self.fc(hidden[-1])
        return out

model = LSTMModel(input_size=5000)

# -------------------------
# Loss & Optimizer
# -------------------------
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# -------------------------
# Training Loop
# -------------------------
model.train()

for epoch in range(5):
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()
    print(f"Epoch {epoch+1}, Loss: {loss.item()}")

# -------------------------
# Evaluation
# -------------------------
model.eval()

with torch.no_grad():
    outputs = model(X_val)
    predictions = torch.argmax(outputs, dim=1)

accuracy = accuracy_score(y_val, predictions)
print("LSTM Validation Accuracy:", accuracy)

print("LSTM Training Completed")