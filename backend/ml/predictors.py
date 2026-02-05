"""
Prediction interface for trained models.
Uses LOCAL embeddings and trained sklearn classifiers.
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from backend.ml.embeddings import get_embedder

logger = logging.getLogger(__name__)


class TicketPredictor:
    """
    Prediction interface for ticket triage.
    Loads trained models and makes predictions.
    """
    
    MODEL_DIR = Path("./models")
    
    def __init__(self):
        """Initialize predictor and load models"""
        self.embedder = get_embedder()
        self.dept_classifier = None
        self.critical_classifier = None
        self.label_encoder = None  # For XGBoost int -> string conversion
        self.use_enhanced_features = False  # Whether model uses enhanced features (disabled - hurt performance)
        self.loaded = False
    
    def create_handcrafted_features(self, text: str) -> np.ndarray:
        """
        Create handcrafted features for a single text (matching training).
        
        Args:
            text: Input text
            
        Returns:
            Feature array with shape (13,) - same as training
        """
        features = []
        
        text_lower = text.lower()
        
        # Text statistics
        features.append(len(text))  # text_length
        word_count = len(text.split())
        features.append(word_count)  # word_count
        features.append(len(text) / (word_count + 1))  # avg_word_length
        
        # Domain keywords
        features.append(int(any(word in text_lower for word in 
            ['network', 'vpn', 'wifi', 'connection', 'internet', 'router', 'ethernet'])))
        features.append(int(any(word in text_lower for word in 
            ['account', 'login', 'password', 'authentication', 'access', 'credential', 'username'])))
        features.append(int(any(word in text_lower for word in 
            ['bill', 'payment', 'invoice', 'charge', 'refund', 'price', 'cost', 'subscription'])))
        features.append(int(any(word in text_lower for word in 
            ['product', 'feature', 'functionality', 'bug', 'error', 'issue', 'problem'])))
        features.append(int(any(word in text_lower for word in 
            ['hardware', 'device', 'computer', 'laptop', 'printer', 'monitor', 'keyboard'])))
        features.append(int(any(word in text_lower for word in 
            ['software', 'application', 'app', 'program', 'install', 'update', 'upgrade'])))
        
        # Language (default to English=1, German=0 for inference)
        features.append(0)  # is_german
        features.append(1)  # is_english
        
        # Urgency
        features.append(int(any(word in text_lower for word in 
            ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'important'])))
        
        # Question
        features.append(int('?' in text))
        
        return np.array(features)
    
    def load_models(self):
        """Load trained models from disk"""
        dept_path = self.MODEL_DIR / "department_classifier.joblib"
        crit_path = self.MODEL_DIR / "criticality_classifier.joblib"
        encoder_path = self.MODEL_DIR / "label_encoder.joblib"
        
        if not dept_path.exists() or not crit_path.exists():
            raise FileNotFoundError(
                f"Models not found. Please train models first using scripts/train_models.py"
            )
        
        logger.info("Loading trained models...")
        self.dept_classifier = joblib.load(dept_path)
        self.critical_classifier = joblib.load(crit_path)
        
        # Load label encoder (for XGBoost models)
        if encoder_path.exists():
            self.label_encoder = joblib.load(encoder_path)
            logger.info("✓ Label encoder loaded")
        
        self.loaded = True
        logger.info("✓ Models loaded successfully")
    
    def predict_ticket(self, subject: str, body: str) -> Dict[str, Any]:
        """
        Predict department and criticality for a ticket.
        
        Args:
            subject: Ticket subject
            body: Ticket body
            
        Returns:
            Dictionary with predictions:
            {
                "predicted_queue": str,
                "queue_confidence": float,
                "critical_prob": float,
                "is_critical": bool,
                "embedding": np.ndarray
            }
        """
        if not self.loaded:
            self.load_models()
        
        # Create combined text
        text = f"{subject}\n\n{body}"
        
        # Generate embedding
        embedding = self.embedder.embed_single(text, normalize=True)
        
        # Add handcrafted features if model was trained with them
        if self.use_enhanced_features:
            handcrafted = self.create_handcrafted_features(text)
            combined_features = np.concatenate([embedding, handcrafted])
            embedding_2d = combined_features.reshape(1, -1)
        else:
            embedding_2d = embedding.reshape(1, -1)
        
        # Predict department
        dept_pred_raw = self.dept_classifier.predict(embedding_2d)[0]
        
        # Decode label if using XGBoost (label encoder)
        if self.label_encoder is not None:
            dept_pred = self.label_encoder.inverse_transform([dept_pred_raw])[0]
        else:
            dept_pred = dept_pred_raw
        
        # Get confidence if available
        if hasattr(self.dept_classifier, 'predict_proba'):
            dept_probs = self.dept_classifier.predict_proba(embedding_2d)[0]
            dept_confidence = float(np.max(dept_probs))
        else:
            # For SVM, use decision function
            dept_scores = self.dept_classifier.decision_function(embedding_2d)[0]
            dept_confidence = float(np.max(dept_scores) / (np.sum(np.abs(dept_scores)) + 1e-10))
        
        # Predict criticality
        critical_prob = float(self.critical_classifier.predict_proba(embedding_2d)[0, 1])
        is_critical = critical_prob >= 0.5
        
        return {
            "predicted_queue": dept_pred,
            "queue_confidence": dept_confidence,
            "critical_prob": critical_prob,
            "is_critical": is_critical,
            "embedding": embedding
        }
    
    def batch_predict(self, texts: list) -> Dict[str, np.ndarray]:
        """
        Batch prediction for multiple texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            Dictionary with batch predictions
        """
        if not self.loaded:
            self.load_models()
        
        # Generate embeddings
        embeddings = self.embedder.embed_texts(texts, normalize=True)
        
        # Predict departments
        dept_preds_raw = self.dept_classifier.predict(embeddings)
        
        # Decode labels if using XGBoost
        if self.label_encoder is not None:
            dept_preds = self.label_encoder.inverse_transform(dept_preds_raw)
        else:
            dept_preds = dept_preds_raw
        
        # Predict criticality
        critical_probs = self.critical_classifier.predict_proba(embeddings)[:, 1]
        
        return {
            "predicted_queues": dept_preds,
            "critical_probs": critical_probs,
            "embeddings": embeddings
        }


# Global predictor instance
_predictor = None


def get_predictor() -> TicketPredictor:
    """
    Get global predictor instance (singleton pattern).
    
    Returns:
        TicketPredictor instance
    """
    global _predictor
    if _predictor is None:
        _predictor = TicketPredictor()
    return _predictor
