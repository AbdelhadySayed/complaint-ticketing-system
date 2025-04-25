import os
from datetime import datetime, timedelta
from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer, BartForConditionalGeneration, BartTokenizer
from transformers import DataCollatorForSeq2Seq
import mlflow
from mlflow.tracking import MlflowClient
import torch
from .app import app
from models import db
from models.complaint import Complaint
from datasets import Dataset

# Initialize MLflow
mlflow.set_tracking_uri(app.config['MLFLOW_TRACKING_URI'])
mlflow.set_experiment("BART_Retraining")
client = MlflowClient()

def check_for_retraining():
    """Check data availability"""
    with app.app_context():
        count = db.session.query(Complaint).filter(
            (Complaint.admin_response != 'Pending') &
            (Complaint.used_for_training == False)).count()
        
        if count < app.config['TRAINING_DATA_THRESHOLD']:
            raise ValueError(f"Not enough data (have {count}, need {app.config['TRAINING_DATA_THRESHOLD']})")
        return True

def prepare_training_data():
    """Prepare training dataset"""
    with app.app_context():
        complaints = db.session.query(Complaint).filter(
            (Complaint.admin_response != 'Pending')
        ).limit(app.config['TRAINING_DATA_THRESHOLD']).all()
        
        data = {
            'input': [c.description for c in complaints],
            'target': [c.admin_response for c in complaints]
        }
        
        for c in complaints:
            c.used_for_training = True
        db.session.commit()
        
        return Dataset.from_dict(data)


def tokenize_dataset(dataset, tokenizer):
    """Tokenize the dataset and format for Seq2Seq training"""
    def preprocess_function(examples):
        inputs = [text for text in examples["input"]]
        targets = [text for text in examples["target"]]
        model_inputs = tokenizer(
            inputs, 
            max_length=128, 
            truncation=True,
            padding="max_length"
        )
        
        # Setup tokenizer for targets
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(
                targets,
                max_length=512,
                truncation=True,
                padding="max_length"
            )
        
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    return dataset.map(
        preprocess_function,
        batched=True,
        remove_columns=["input", "target"]
    )

def finetune_bart():
    """Finetuning the BART model on data retrieved from the database"""
    print("=== Starting retraining with MLflow ===")
    
    try:
        # 1. Load model and tokenizer
        print("1/6 Loading initial model...")
        tokenizer = BartTokenizer.from_pretrained(app.config['LOCAL_MODEL_PATH'])
        model = BartForConditionalGeneration.from_pretrained(app.config['LOCAL_MODEL_PATH'])
        
        # 2. Prepare and validate data
        print("2/6 Preparing training data...")
        raw_dataset = prepare_training_data()
        if len(raw_dataset) == 0:
            raise ValueError("No training data available")
            
        # 3. Tokenize dataset
        print("3/6 Tokenizing data...")
        tokenized_dataset = tokenize_dataset(raw_dataset, tokenizer)
        
        # Split dataset
        train_test = tokenized_dataset.train_test_split(test_size=0.1)
        print(f"Training samples: {len(train_test['train'])}, Test samples: {len(train_test['test'])}")
        
        # 4. Configure data collator
        print("4/6 Setting up data collator...")
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=tokenizer,
            model=model,
            padding=True
        )
        
        # 5. Initialize MLflow
        print("5/6 Initializing MLflow...")
        mlflow.set_tracking_uri(app.config['MLFLOW_TRACKING_URI'])
        mlflow.set_experiment("BART_Retraining")
        
        # 6. Training setup
        print("6/6 Configuring training...")
        training_args = Seq2SeqTrainingArguments(
            output_dir="./results",
            evaluation_strategy="epoch",
            per_device_train_batch_size=app.config['TRAINING_BATCH_SIZE'],
            per_device_eval_batch_size=app.config['TRAINING_BATCH_SIZE'],
            learning_rate=app.config['TRAINING_LEARNING_RATE'],
            num_train_epochs=app.config['TRAINING_EPOCHS'],
            logging_dir="./logs",
            report_to=["mlflow"],
            save_strategy="epoch",
            predict_with_generate=True
        )
        
        trainer = Seq2SeqTrainer(
            model=model,
            args=training_args,
            train_dataset=train_test["train"],
            eval_dataset=train_test["test"],
            tokenizer=tokenizer,
            data_collator=data_collator  
        )
        
        print("🚀 Starting training...")
        with mlflow.start_run() as run:
            trainer.train()
            
            # Save model with comprehensive configuration
            model_signature = mlflow.models.infer_signature(
                model_input="Sample complaint text",
                model_output="Sample generated response"
            )
            
            registered_model = mlflow.transformers.log_model(
                transformers_model={
                    "model": trainer.model,
                    "tokenizer": tokenizer
                },
                artifact_path="bart_complaint_model",
                registered_model_name=app.config['MODEL_NAME'],
                task="text2text-generation",
                signature=model_signature,
                input_example={"input": "Sample complaint text"},
                metadata={
                    "training_samples": len(train_test["train"]),
                    "eval_samples": len(train_test["test"]),
                    "epochs": app.config['TRAINING_EPOCHS']
                }
            )
            
            # Get version info correctly for all MLflow versions
            if hasattr(registered_model, 'model_version'):
                version = registered_model.model_version
            else:
                # For older MLflow versions
                client = MlflowClient()
                latest_version = client.get_latest_versions(app.config['MODEL_NAME'], stages=["None"])[0]
                version = latest_version.version
            
            print(f"Training complete! Model version {version} registered")
            return version
            
    except Exception as e:
        print(f"Retraining failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Verify MLflow server is reachable
        mlflow.get_tracking_uri()
        
        # Run training
        check_for_retraining()
        finetune_bart()
        print("=== Retraining completed successfully ===")
    except Exception as e:
        print(f"!!! Retraining failed: {str(e)}")