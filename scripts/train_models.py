"""
Training script for ML models.
Trains department classifier and criticality classifier using local embeddings.
"""
import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ml.train import TicketClassifierTrainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main training function"""
    print("\n" + "="*80)
    print("IT TICKET TRIAGE SYSTEM - MODEL TRAINING")
    print("="*80 + "\n")
    
    # Get dataset path from command line or use default
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        dataset_path = r"C:\Users\sthfa\Downloads\aa_dataset-tickets-multi-lang-5-2-50-version.csv"
    
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset not found: {dataset_path}")
        print(f"Please provide the correct path as argument: python scripts/train_models.py <path>")
        return 1
    
    print(f"[OK] Using dataset: {dataset_path}\n")
    
    # Initialize trainer
    print("Initializing trainer...")
    trainer = TicketClassifierTrainer(dataset_path)
    
    # Train all models
    print("\nStarting training pipeline...\n")
    print("IMPORTANT: Why we split the data into train/val/test?")
    print("-" * 80)
    print("We need to evaluate how well our ML classifiers (department routing and")
    print("criticality prediction) generalize to unseen tickets. Even though Gemini")
    print("is not trained, our scikit-learn models need proper evaluation to ensure")
    print("they don't overfit and can accurately classify new, real-world tickets.")
    print("The split allows us to:")
    print("  - Train: Learn patterns from historical tickets")
    print("  - Validation: Tune hyperparameters and select best model")
    print("  - Test: Evaluate final performance on completely unseen data")
    print("-" * 80 + "\n")
    
    try:
        metrics = trainer.train_all()
        
        print("\n" + "="*80)
        print("[SUCCESS] TRAINING COMPLETE!")
        print("="*80)
        print("\nFinal Metrics:")
        print(f"\nDepartment Classifier:")
        print(f"  - Test Accuracy: {metrics['department']['test_acc']:.3f}")
        print(f"  - Test F1 (macro): {metrics['department']['test_f1']:.3f}")
        
        print(f"\nCriticality Classifier:")
        print(f"  - Test AUC: {metrics['criticality']['test_auc']:.3f}")
        print(f"  - Critical Recall: {metrics['criticality']['critical_recall']:.3f}")
        
        print("\n[OK] Models saved to ./models/")
        print("[OK] Embeddings cached to ./embeddings_cache/")
        print("\nNext steps:")
        print("  1. Run: python scripts/build_index.py")
        print("  2. Start backend: python backend/app.py")
        print("="*80 + "\n")
    
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        print(f"\n[ERROR] Training failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
