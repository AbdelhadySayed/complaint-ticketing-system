import pickle
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split
import string
import re

# Download stopwords
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('punkt_tab')

# load the model
model = joblib.load("services/classification_models/SGD.pkl")

# Load TF-IDF Vectorizer
tfidf_vectorizer = joblib.load("services/classification_models/tfidf_vectorizer.pkl")


def preprocess_text(text):
    # Remove special placeholders like {{Order Number}}
    text = re.sub(r'{{.*?}}', '', text)

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Convert to lowercase
    text = text.lower()

    # Tokenization
    tokens = word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    essential_words = {'not', 'no', 'cannot'}
    custom_stop_words = stop_words - essential_words
    tokens = [word for word in tokens if word not in custom_stop_words]

    return ' '.join(tokens)



def categorize_complaint(description, model=model):
    """
    Preprocesses text and predicts the category using the specified model.

    Args:
        text (str): The input text.
        model_name (str, optional): The name of the model to use.
                                     Defaults to "Logistic Regression".

    Returns:
        str: The predicted category.
    """
    # Preprocess the text
    processed_description = preprocess_text(description) # Assuming you have the preprocess_text function

    if len(processed_description) ==0:
        return None

    # Transform using TF-IDF
    text_tfidf = tfidf_vectorizer.transform([processed_description])

    # Make the prediction
    prediction = model.predict(text_tfidf)[0]

    return prediction




