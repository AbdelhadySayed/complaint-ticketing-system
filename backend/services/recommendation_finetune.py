from transformers import BartTokenizer, BartForConditionalGeneration
import mlflow
import torch
import threading
import time
import logging
import textwrap
import re
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Configuration paths
LOCAL_MODEL_PATH = "recommendation_model"

script_dir = os.path.dirname(os.path.abspath(__file__))
MLFLOW_ROOT_PATH = os.path.abspath(os.path.join(script_dir, "..", "mlartifacts"))

# Text preprocessing utilities
CONTRACTION_MAP = {
    "i've": "i have",
    "i'm": "i am",
    "don't": "do not",
    "can't": "cannot",
    "won't": "will not",
    "it's": "it is",
    "you're": "you are",
    "they're": "they are",
    "we're": "we are",
    "that's": "that is",
    "what's": "what is",
    "who's": "who is",
    "where's": "where is",
    "when's": "when is",
    "why's": "why is",
    "how's": "how is",
    "let's": "let us",
    "he's": "he is",
    "she's": "she is",
    "there's": "there is",
    "here's": "here is",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "hasn't": "has not",
    "haven't": "have not",
    "hadn't": "had not",
    "doesn't": "does not",
    "didn't": "did not",
    "wouldn't": "would not",
    "shouldn't": "should not",
    "couldn't": "could not",
    "mustn't": "must not",
    "i'll": "i will",
    "you'll": "you will",
    "he'll": "he will",
    "she'll": "she will",
    "we'll": "we will",
    "they'll": "they will",
    "it'll": "it will",
    "that'll": "that will",
    "there'll": "there will",
    "this'll": "this will",
    "what'll": "what will",
    "who'll": "who will",
    "where'll": "where will",
    "when'll": "when will",
    "why'll": "why will",
    "how'll": "how will",
}


def expand_contractions(text, contraction_mapping=CONTRACTION_MAP):
    """Expands contractions in the text."""
    for contraction, expansion in contraction_mapping.items():
        text = text.replace(contraction, expansion)
    return text

def preprocess_text(text):
    """Cleans and preprocesses text."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'\b\d{6,}\b', '{number}', text)
    text = expand_contractions(text)
    text = re.sub(r"[^\w\s{}]", "", text)
    return re.sub(r"\s+", " ", text).strip()

def preprocess_generated_response(response):
    """Formats the generated response."""
    response = re.sub(r'\bi\b', 'I', response)
    response = re.sub(r'(\d) ', r'\1. ', response)
    return textwrap.fill(response, width=80)


class ResponseGenerator:
    """
    Generates responses using latest MLflow model or local fallback
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize_model()
        return cls._instance
    
    def _initialize_model(self):
        self.model = None
        self.tokenizer = None
        self.current_version = None
        self._load_model()
        self._start_refresh_thread()
    
    def _start_refresh_thread(self):
        def refresh_loop():
            while True:
                time.sleep(3600)  # Check hourly
                try:
                    self._load_model()
                except Exception as e:
                    logger.error(f"Refresh failed: {str(e)}")
        threading.Thread(target=refresh_loop, daemon=True).start()
    
    def _load_model(self):
        """Load latest MLflow model or fallback to local"""
        try:
            # Try finding and loading latest MLflow model
            mlflow_model_path, run_id = self._find_latest_mlflow_model()
            if mlflow_model_path:
                print(f"Loading MLflow model from: {mlflow_model_path}")
                pipeline = mlflow.transformers.load_model(mlflow_model_path) 
                self.model = pipeline.model
                self.tokenizer = pipeline.tokenizer
                self.current_version = run_id
                return
        except Exception as e:
            logger.warning(f"MLflow model load failed: {str(e)}")
        
        # Fallback to local model
        try:
            if os.path.exists(LOCAL_MODEL_PATH):
                print("use local model")
                logger.info("Using local model fallback")
                self.tokenizer = BartTokenizer.from_pretrained(LOCAL_MODEL_PATH)
                self.model = BartForConditionalGeneration.from_pretrained(LOCAL_MODEL_PATH)
                self.current_version = "local"
                return
        except Exception as e:
            logger.error(f"Local model load failed: {str(e)}")
        
        raise RuntimeError("No valid model available")

    def _find_latest_mlflow_model(self):
        """Find the newest model in MLflow artifacts by modification time"""
        try:
            mlflow_path = Path(MLFLOW_ROOT_PATH)
            latest_model = None
            latest_run_id = None
            latest_mtime = 0
            
            # Find all experiment folders
            for exp_dir in mlflow_path.iterdir():
                if not exp_dir.is_dir():
                    continue
                
                # Find all run folders
                for run_dir in exp_dir.iterdir():
                    if not run_dir.is_dir():
                        continue
                    
                    model_dir = run_dir / "artifacts" / "bart_complaint_model"
                    print(model_dir)
                    if model_dir.exists():
                        # Get modification time of the model directory
                        current_mtime = os.path.getmtime(model_dir)
                        if current_mtime > latest_mtime:
                            latest_mtime = current_mtime
                            latest_model = str(model_dir)
                            latest_run_id = run_dir.name
                            print("latest time", latest_mtime)

            return (latest_model, latest_run_id) if latest_model else (None, None)
        except Exception as e:
            logger.warning(f"MLflow model search failed: {str(e)}")
            return (None, None)

    def generate_response(self, text):
        """Generate response for input text"""
        try:
            if not text or not isinstance(text, str):
                return None

            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=128,
                truncation=True
            )
            
            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_length=512)
            
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            return None

# Singleton instance
response_generator = ResponseGenerator()