"""
ML model training for department classification and criticality prediction.
Uses LOCAL embeddings (NOT Gemini) and scikit-learn classifiers.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report,
    confusion_matrix, roc_auc_score, roc_curve
)
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import lightgbm as lgb
import joblib
from pathlib import Path
from typing import Tuple, Dict, Any
import logging
from tqdm import tqdm

from backend.ml.embeddings import get_embedder

logger = logging.getLogger(__name__)


class TicketClassifierTrainer:
    """
    Train department and criticality classifiers using local embeddings.
    """
    
    MODEL_DIR = Path("./models")
    
    def __init__(self, dataset_path: str, embedder=None):
        """
        Initialize trainer.
        
        Args:
            dataset_path: Path to CSV dataset
            embedder: LocalEmbedder instance (optional)
        """
        self.dataset_path = dataset_path
        self.embedder = embedder or get_embedder()
        self.MODEL_DIR.mkdir(exist_ok=True)
        
        # Models
        self.dept_classifier = None
        self.critical_classifier = None
        self.label_encoder = LabelEncoder()  # For XGBoost string -> int conversion
        
        # Data
        self.df = None
        self.texts = None
        self.embeddings = None
        
        # Split data
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_dept_train = None
        self.y_dept_val = None
        self.y_dept_test = None
        self.y_crit_train = None
        self.y_crit_val = None
        self.y_crit_test = None
    
    def load_and_prepare_data(self):
        """
        Load CSV and prepare data.
        Creates text = subject + "\n\n" + body
        Creates is_critical = (priority == "high")
        """
        logger.info(f"Loading dataset from {self.dataset_path}")
        self.df = pd.read_csv(self.dataset_path)
        
        # Create combined text
        self.df['text'] = self.df['subject'].fillna('') + "\n\n" + self.df['body'].fillna('')
        
        # Create is_critical label
        self.df['is_critical'] = (self.df['priority'].str.lower() == 'high').astype(int)
        
        # Filter out rows with missing queue or text
        self.df = self.df[self.df['queue'].notna() & self.df['text'].notna()].copy()
        
        logger.info(f"✓ Loaded {len(self.df)} valid tickets")
        logger.info(f"  - Queues: {self.df['queue'].nunique()} unique")
        logger.info(f"  - Critical tickets: {self.df['is_critical'].sum()} ({self.df['is_critical'].mean()*100:.1f}%)")
        logger.info(f"  - Languages: {self.df['language'].unique()}")
        
        return self.df
    
    def generate_embeddings(self):
        """
        Generate embeddings for all texts using LOCAL embedder.
        """
        logger.info("Generating embeddings (this may take a while)...")
        
        # Try to load from cache
        cached = self.embedder.load_embeddings("dataset_embeddings")
        if cached is not None and len(cached) == len(self.df):
            logger.info(f"✓ Loaded cached embeddings: {cached.shape}")
            self.embeddings = cached
            return self.embeddings
        
        # Generate embeddings
        self.texts = self.df['text'].tolist()
        self.embeddings = self.embedder.embed_texts(
            self.texts,
            batch_size=32,
            normalize=True,
            show_progress=True
        )
        
        # Save to cache
        self.embedder.save_embeddings(self.embeddings, "dataset_embeddings")
        
        logger.info(f"✓ Generated embeddings: {self.embeddings.shape}")
        return self.embeddings
    
    def create_handcrafted_features(self) -> np.ndarray:
        """
        Create domain-specific handcrafted features to enhance embeddings.
        
        Returns:
            Feature matrix with shape (n_samples, n_features)
        """
        logger.info("Creating handcrafted features...")
        
        features = {}
        
        # Text statistics
        features['text_length'] = self.df['text'].str.len()
        features['word_count'] = self.df['text'].str.split().str.len()
        features['avg_word_length'] = features['text_length'] / (features['word_count'] + 1)
        
        # Domain-specific keyword indicators
        text_lower = self.df['text'].str.lower()
        
        features['has_network_words'] = text_lower.str.contains(
            'network|vpn|wifi|connection|internet|router|ethernet', 
            case=False, regex=True, na=False
        ).astype(int)
        
        features['has_account_words'] = text_lower.str.contains(
            'account|login|password|authentication|access|credential|username',
            case=False, regex=True, na=False
        ).astype(int)
        
        features['has_billing_words'] = text_lower.str.contains(
            'bill|payment|invoice|charge|refund|price|cost|subscription',
            case=False, regex=True, na=False
        ).astype(int)
        
        features['has_product_words'] = text_lower.str.contains(
            'product|feature|functionality|bug|error|issue|problem',
            case=False, regex=True, na=False
        ).astype(int)
        
        features['has_hardware_words'] = text_lower.str.contains(
            'hardware|device|computer|laptop|printer|monitor|keyboard',
            case=False, regex=True, na=False
        ).astype(int)
        
        features['has_software_words'] = text_lower.str.contains(
            'software|application|app|program|install|update|upgrade',
            case=False, regex=True, na=False
        ).astype(int)
        
        # Language indicator
        features['is_german'] = (self.df['language'] == 'de').astype(int)
        features['is_english'] = (self.df['language'] == 'en').astype(int)
        
        # Urgency indicators
        features['has_urgent_words'] = text_lower.str.contains(
            'urgent|asap|immediately|critical|emergency|important',
            case=False, regex=True, na=False
        ).astype(int)
        
        # Question indicators
        features['has_question'] = self.df['text'].str.contains(r'\?', regex=True, na=False).astype(int)
        
        # Convert to numpy array
        feature_df = pd.DataFrame(features)
        handcrafted = feature_df.values
        
        logger.info(f"✓ Created {handcrafted.shape[1]} handcrafted features")
        return handcrafted
    
    def split_data(self, test_size: float = 0.15, val_size: float = 0.15, random_state: int = 42, 
                   use_enhanced_features: bool = False):
        """
        Split data into train/val/test sets.
        
        Why split? To evaluate classifier generalization and prevent overfitting.
        Even though Gemini is not trained, we need to ensure our routing/criticality
        classifiers generalize well to unseen tickets.
        
        Args:
            test_size: Test set proportion
            val_size: Validation set proportion (from remaining after test)
            random_state: Random seed
            use_enhanced_features: If True, add handcrafted features to embeddings
        """
        logger.info("Splitting data into train/val/test...")
        
        # Combine embeddings with handcrafted features
        if use_enhanced_features:
            handcrafted = self.create_handcrafted_features()
            X = np.hstack([self.embeddings, handcrafted])
            logger.info(f"✓ Combined features shape: {X.shape} (embeddings + handcrafted)")
        else:
            X = self.embeddings
        
        # Encode department labels as integers for XGBoost
        y_dept_encoded = self.label_encoder.fit_transform(self.df['queue'].values)
        y_crit = self.df['is_critical'].values
        
        # First split: train+val vs test
        X_temp, self.X_test, y_dept_temp, self.y_dept_test, y_crit_temp, self.y_crit_test = train_test_split(
            X, y_dept_encoded, y_crit,
            test_size=test_size,
            random_state=random_state,
            stratify=y_dept_encoded  # Stratify by department
        )
        
        # Second split: train vs val
        val_size_adjusted = val_size / (1 - test_size)
        self.X_train, self.X_val, self.y_dept_train, self.y_dept_val, self.y_crit_train, self.y_crit_val = train_test_split(
            X_temp, y_dept_temp, y_crit_temp,
            test_size=val_size_adjusted,
            random_state=random_state,
            stratify=y_dept_temp
        )
        
        logger.info(f"✓ Split complete:")
        logger.info(f"  - Train: {len(self.X_train)} samples")
        logger.info(f"  - Val:   {len(self.X_val)} samples")
        logger.info(f"  - Test:  {len(self.X_test)} samples")
    
    def train_department_classifier(self, model_type: str = "ensemble", 
                                   use_smote: bool = False, use_ensemble: bool = True):
        """
        Train department classifier with advanced techniques.
        
        Args:
            model_type: "logistic", "svm", "xgboost", "xgboost_tuned", or "ensemble"
            use_smote: Use SMOTE to balance classes
            use_ensemble: Use ensemble of XGBoost + LightGBM
        """
        logger.info(f"Training department classifier ({model_type})...")
        
        # Apply SMOTE to balance classes
        X_train_balanced = self.X_train
        y_train_balanced = self.y_dept_train
        
        if use_smote:
            logger.info("Applying SMOTE to balance classes...")
            # Use sampling_strategy to limit oversampling and reduce memory usage
            smote = SMOTE(random_state=42, k_neighbors=3, sampling_strategy='not majority')
            try:
                X_train_balanced, y_train_balanced = smote.fit_resample(self.X_train, self.y_dept_train)
                logger.info(f"✓ SMOTE applied: {self.X_train.shape[0]} -> {X_train_balanced.shape[0]} samples")
            except Exception as e:
                logger.warning(f"SMOTE failed: {e}. Using original data.")
                X_train_balanced = self.X_train
                y_train_balanced = self.y_dept_train
        
        if model_type == "logistic":
            self.dept_classifier = LogisticRegression(
                max_iter=1000,
                random_state=42,
                multi_class='multinomial',
                class_weight='balanced'
            )
        elif model_type == "svm":
            self.dept_classifier = LinearSVC(
                max_iter=2000,
                random_state=42,
                class_weight='balanced'
            )
        elif model_type == "xgboost" or model_type == "xgboost_optimized":
            # Simple XGBoost that works (with enhanced features for better performance)
            self.dept_classifier = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.15,
                objective='multi:softmax',
                num_class=len(np.unique(self.y_dept_train)),
                eval_metric='mlogloss',
                random_state=42,
                tree_method='hist',
                n_jobs=-1,
                verbosity=0
            )
        elif model_type == "xgboost_tuned":
            logger.info("Running hyperparameter tuning (this may take 3-5 minutes)...")
            
            # Smaller grid to reduce memory usage
            param_grid = {
                'n_estimators': [100, 150],
                'max_depth': [6, 8],
                'learning_rate': [0.1, 0.2],
                'subsample': [0.9, 1.0]
            }
            
            base_model = xgb.XGBClassifier(
                objective='multi:softmax',
                num_class=len(np.unique(self.y_dept_train)),
                eval_metric='mlogloss',
                random_state=42,
                tree_method='hist',
                n_jobs=2,  # Limit parallel jobs to reduce memory
                verbosity=0
            )
            
            grid_search = GridSearchCV(
                base_model,
                param_grid,
                cv=2,  # Reduced from 3 to save memory
                scoring='f1_macro',
                n_jobs=2,  # Limit parallel jobs
                verbose=1
            )
            
            grid_search.fit(X_train_balanced, y_train_balanced)
            self.dept_classifier = grid_search.best_estimator_
            
            logger.info(f"✓ Best hyperparameters: {grid_search.best_params_}")
            logger.info(f"✓ Best CV F1 score: {grid_search.best_score_:.3f}")
        
        elif use_ensemble or model_type == "ensemble":
            logger.info("Training ensemble (XGBoost + LightGBM)...")
            
            xgb_clf = xgb.XGBClassifier(
                n_estimators=120,
                max_depth=6,
                learning_rate=0.15,
                objective='multi:softmax',
                num_class=len(np.unique(self.y_dept_train)),
                random_state=42,
                tree_method='hist',
                n_jobs=-1,
                verbosity=0
            )
            
            lgb_clf = lgb.LGBMClassifier(
                n_estimators=120,
                max_depth=6,
                learning_rate=0.15,
                random_state=42,
                n_jobs=-1,
                verbose=-1
            )
            
            self.dept_classifier = VotingClassifier(
                estimators=[
                    ('xgb', xgb_clf),
                    ('lgb', lgb_clf)
                ],
                voting='soft',
                n_jobs=-1
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Train the model
        if model_type != "xgboost_tuned":  # GridSearch already fitted
            self.dept_classifier.fit(X_train_balanced, y_train_balanced)
        
        # Evaluate
        train_preds = self.dept_classifier.predict(self.X_train)
        val_preds = self.dept_classifier.predict(self.X_val)
        test_preds = self.dept_classifier.predict(self.X_test)
        
        train_acc = accuracy_score(self.y_dept_train, train_preds)
        val_acc = accuracy_score(self.y_dept_val, val_preds)
        test_acc = accuracy_score(self.y_dept_test, test_preds)
        
        train_f1 = f1_score(self.y_dept_train, train_preds, average='macro')
        val_f1 = f1_score(self.y_dept_val, val_preds, average='macro')
        test_f1 = f1_score(self.y_dept_test, test_preds, average='macro')
        
        logger.info(f"✓ Department classifier trained:")
        logger.info(f"  - Train: Acc={train_acc:.3f}, F1={train_f1:.3f}")
        logger.info(f"  - Val:   Acc={val_acc:.3f}, F1={val_f1:.3f}")
        logger.info(f"  - Test:  Acc={test_acc:.3f}, F1={test_f1:.3f}")
        
        # Detailed report on test set (decode labels back to department names)
        print("\nDepartment Classification Report (Test Set):")
        y_test_names = self.label_encoder.inverse_transform(self.y_dept_test)
        test_preds_names = self.label_encoder.inverse_transform(test_preds)
        print(classification_report(y_test_names, test_preds_names))
        
        return {
            "train_acc": train_acc,
            "val_acc": val_acc,
            "test_acc": test_acc,
            "train_f1": train_f1,
            "val_f1": val_f1,
            "test_f1": test_f1
        }
    
    def train_criticality_classifier(self):
        """
        Train criticality classifier (binary: critical vs non-critical).
        """
        logger.info("Training criticality classifier (Logistic Regression)...")
        
        self.critical_classifier = LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        )
        
        self.critical_classifier.fit(self.X_train, self.y_crit_train)
        
        # Evaluate
        train_preds = self.critical_classifier.predict(self.X_train)
        val_preds = self.critical_classifier.predict(self.X_val)
        test_preds = self.critical_classifier.predict(self.X_test)
        
        # Probabilities for AUC
        train_probs = self.critical_classifier.predict_proba(self.X_train)[:, 1]
        val_probs = self.critical_classifier.predict_proba(self.X_val)[:, 1]
        test_probs = self.critical_classifier.predict_proba(self.X_test)[:, 1]
        
        train_auc = roc_auc_score(self.y_crit_train, train_probs)
        val_auc = roc_auc_score(self.y_crit_val, val_probs)
        test_auc = roc_auc_score(self.y_crit_test, test_probs)
        
        # Critical recall (important!)
        from sklearn.metrics import recall_score
        critical_recall = recall_score(self.y_crit_test, test_preds, pos_label=1)
        
        logger.info(f"✓ Criticality classifier trained:")
        logger.info(f"  - Train AUC: {train_auc:.3f}")
        logger.info(f"  - Val AUC:   {val_auc:.3f}")
        logger.info(f"  - Test AUC:  {test_auc:.3f}")
        logger.info(f"  - Critical Recall (Test): {critical_recall:.3f}")
        
        # Confusion matrix
        cm = confusion_matrix(self.y_crit_test, test_preds)
        print("\nCriticality Confusion Matrix (Test Set):")
        print(f"                Predicted")
        print(f"                Non-Crit  Critical")
        print(f"Actual Non-Crit  {cm[0,0]:6d}    {cm[0,1]:6d}")
        print(f"Actual Critical  {cm[1,0]:6d}    {cm[1,1]:6d}")
        
        print("\nCriticality Classification Report (Test Set):")
        print(classification_report(self.y_crit_test, test_preds, target_names=['Non-Critical', 'Critical']))
        
        return {
            "train_auc": train_auc,
            "val_auc": val_auc,
            "test_auc": test_auc,
            "critical_recall": critical_recall
        }
    
    def save_models(self):
        """Save trained models to disk"""
        dept_path = self.MODEL_DIR / "department_classifier.joblib"
        crit_path = self.MODEL_DIR / "criticality_classifier.joblib"
        encoder_path = self.MODEL_DIR / "label_encoder.joblib"
        
        joblib.dump(self.dept_classifier, dept_path)
        joblib.dump(self.critical_classifier, crit_path)
        joblib.dump(self.label_encoder, encoder_path)
        
        logger.info(f"✓ Saved models:")
        logger.info(f"  - {dept_path}")
        logger.info(f"  - {crit_path}")
        logger.info(f"  - {encoder_path}")
    
    def train_all(self):
        """Run full training pipeline"""
        self.load_and_prepare_data()
        self.generate_embeddings()
        self.split_data()
        
        dept_metrics = self.train_department_classifier()
        crit_metrics = self.train_criticality_classifier()
        
        self.save_models()
        
        return {
            "department": dept_metrics,
            "criticality": crit_metrics
        }
