import tensorflow as tf
import pickle
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.sequence import pad_sequences
import string
import re

# Download stopwords
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

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


# Example usage:
new_text = "I need help with my order"
predicted_category = categorize_complaint(new_text)
print(f"Predicted Category: {predicted_category}")

# # Load Tokenizer & Label Encoder
# with open("class_model/tokenizer.pkl", "rb") as handle:
#     tokenizer = joblib.load(handle)

# with open("class_model//label_encoder.pkl", "rb") as handle:
#     label_encoder = joblib.load(handle)

# # Load Trained Models
# lstm_model = tf.keras.models.load_model("class_model//lstm_model.h5")


# print("✅ Models, tokenizer, and label encoder loaded successfully!")

# # Function to Predict with Deep Learning Models
# def predict_with_dl(model, text):
#     seq = pad_sequences(tokenizer.texts_to_sequences([text]), maxlen=100)
#     pred_index = model.predict(seq).argmax(axis=1)
#     pred_label = label_encoder.inverse_transform(pred_index)
#     return pred_label[0]  # Extract string label

# # Example Prediction
# new_ticket = [
#     "I placed an order last week, but I haven’t received a confirmation email yet. I checked my account, and the order status says 'Processing.' Could you please confirm if my order has been successfully placed? Also, I need to know the estimated delivery time.",
    
# ]

# lstm_prediction =[predict_with_dl(lstm_model, ticket) for ticket in new_ticket]


# print("LSTM Prediction:", lstm_prediction)