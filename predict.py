def predict_job(text):

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    prediction = torch.argmax(logits).item()

    confidence = torch.softmax(logits, dim=1)[0][prediction].item()

    if prediction == 1:
        return "⚠ Fake Job", confidence
    else:
        return "✅ Legit Job", confidence