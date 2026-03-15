import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# load dataset
data = pd.read_csv("dataset/fake_job_postings.csv")

# fill missing text
data["description"] = data["description"].fillna("")

X = data["description"]
y = data["fraudulent"]

# convert text to vectors
vectorizer = TfidfVectorizer(stop_words="english")
X_vec = vectorizer.fit_transform(X)

# train model
model = LogisticRegression()
model.fit(X_vec, y)

# save files
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("Model and vectorizer saved successfully!")