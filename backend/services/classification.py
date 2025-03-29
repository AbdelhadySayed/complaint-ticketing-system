import tensorflow as tf
import pickle
import joblib
from tensorflow.keras.preprocessing.sequence import pad_sequences



def categorize_complaint(description):

    return "pending"
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