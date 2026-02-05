"""
Test script to verify system components.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from backend.ml.embeddings import get_embedder
        print("  [OK] embeddings module")
        
        from backend.ml.train import TicketClassifierTrainer
        print("  [OK] train module")
        
        from backend.ml.predictors import get_predictor
        print("  [OK] predictors module")
        
        from backend.ml.retrieval import get_retriever
        print("  [OK] retrieval module")
        
        from backend.gemini.generate_reply import GeminiReplyGenerator
        print("  [OK] gemini module")
        
        from backend.models import Ticket, Response, Approval
        print("  [OK] database models")
        
        from backend.db import init_db
        print("  [OK] database module")
        
        print("\n[SUCCESS] All imports successful!\n")
        return True
    
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}\n")
        return False


def test_embedder():
    """Test embedder"""
    print("Testing local embedder...")
    
    try:
        from backend.ml.embeddings import get_embedder
        
        embedder = get_embedder()
        print(f"  [OK] Model loaded: {embedder.model_name}")
        print(f"  [OK] Embedding dimension: {embedder.embedding_dim}")
        
        # Test encoding
        test_text = "This is a test ticket about network connectivity issues."
        embedding = embedder.embed_single(test_text)
        print(f"  [OK] Embedding generated: shape {embedding.shape}")
        
        print("\n[SUCCESS] Embedder test passed!\n")
        return True
    
    except Exception as e:
        print(f"\n[ERROR] Embedder test failed: {e}\n")
        return False


def test_database():
    """Test database"""
    print("Testing database...")
    
    try:
        from backend.db import init_db, SessionLocal
        from backend.models import Ticket
        
        init_db()
        print("  [OK] Database initialized")
        
        # Test session
        db = SessionLocal()
        count = db.query(Ticket).count()
        db.close()
        print(f"  [OK] Database query successful (tickets: {count})")
        
        print("\n[SUCCESS] Database test passed!\n")
        return True
    
    except Exception as e:
        print(f"\n[ERROR] Database test failed: {e}\n")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("IT TICKET TRIAGE SYSTEM - SYSTEM TEST")
    print("="*80 + "\n")
    
    results = []
    
    # Test imports
    results.append(test_imports())
    
    # Test embedder
    results.append(test_embedder())
    
    # Test database
    results.append(test_database())
    
    # Summary
    print("="*80)
    if all(results):
        print("[SUCCESS] ALL TESTS PASSED!")
        print("="*80 + "\n")
        print("System is ready. Next steps:")
        print("  1. Train models: python scripts/train_models.py")
        print("  2. Build index: python scripts/build_index.py")
        print("  3. Start system!")
        return 0
    else:
        print("[ERROR] SOME TESTS FAILED")
        print("="*80 + "\n")
        print("Please fix the errors above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
