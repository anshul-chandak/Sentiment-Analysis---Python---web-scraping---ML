# Sentiment-Driven IMDb Movie Ratings

## Business Problem

Movie ratings on platforms like IMDb can be influenced by biased or manipulated scores. Relying solely on star ratings may not reflect the actual sentiment of viewers. This project addresses that issue by using Natural Language Processing (NLP) to extract sentiment directly from audience reviews.

**Goal:** Predict viewer sentiment from unstructured IMDb reviews and generate an independent, sentiment-based score for each movie.

---

## Solution Summary

This project scrapes IMDb reviews for the Top 250 movies and applies a sentiment classification model trained on labeled Kaggle review data. By doing so, it separates training and inference sources for better generalization and realism — simulating how a real-world model might be applied to new, unseen data.

---

## Technical Overview

### Tools and Libraries

- **Language:** Python
- **Scraping:** Selenium, BeautifulSoup
- **Text Processing:** NLTK, re
- **Data Handling:** Pandas, NumPy
- **Modeling:** Scikit-learn (TF-IDF, Naive Bayes, SVM)

---

## Workflow

### 1. Data Sources

- **Training Data:** IMDb movie review dataset from Kaggle (pre-labeled for sentiment)
- **Prediction Data:** IMDb Top 250 movie reviews scraped directly from IMDb website

### 2. Web Scraping

- Used Selenium to navigate IMDb Top 250 pages
- Extracted multiple reviews per movie using BeautifulSoup
- Stored results in structured CSV format

### 3. Data Cleaning & Preprocessing

- Removed punctuation, special characters, and stop words
- Tokenized, stemmed, and lowercased text using NLTK
- Converted raw text into numerical vectors using TF-IDF

### 4. Model Training

- Trained sentiment classifiers (Naive Bayes, Logistic Regression, SVM) on Kaggle-labeled IMDb review data
- Used accuracy, F1 score, precision, and recall for evaluation
- Chose the best-performing model based on validation results

### 5. Prediction and Sentiment Scoring

- Applied trained model to scraped IMDb reviews
- Predicted sentiment (positive/negative) for each review
- Generated a custom movie rating based on proportion of positive reviews

---

## Results

- Successfully predicted sentiment of thousands of IMDb reviews
- Created a custom movie rating metric based purely on audience sentiment
- Demonstrated how ML + NLP can provide deeper insights beyond star ratings

---

## How to Run

1. Clone this repository
2. Run `IMDB_data_ETL.py` to scrape and clean IMDb reviews
3. Run `Model training and prediction.py` to train the model and generate predictions
4. Review the output sentiment labels and calculated scores

---

## Folder Structure

```
IMDB_data_ETL.py                  # Web scraping + cleaning
Model training and prediction.py # Model training, evaluation, prediction
data/                             # Output CSVs (scraped + scored)
README.md
```

---

## Author

Anshul Chandak  
MS in Information Technology and Management – University of Texas at Dallas

---

## License

This project is for academic and demonstration purposes only.
