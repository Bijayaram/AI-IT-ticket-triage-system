"""
Build FAISS index for ticket retrieval.
Uses local embeddings (same as training) to create searchable vector index.
"""
import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ml.retrieval import TicketRetriever
from backend.ml.embeddings import get_embedder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main function to build FAISS index"""
    print("\n" + "="*80)
    print("IT TICKET TRIAGE SYSTEM - BUILD FAISS INDEX")
    print("="*80 + "\n")
    
    # Get dataset path from command line or use default
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        dataset_path = r"C:\Users\sthfa\Downloads\aa_dataset-tickets-multi-lang-5-2-50-version.csv"
    
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset not found: {dataset_path}")
        print(f"Please provide the correct path as argument: python scripts/build_index.py <path>")
        return 1
    
    print(f"[OK] Using dataset: {dataset_path}\n")
    
    try:
        # Initialize embedder and retriever
        embedder = get_embedder()
        retriever = TicketRetriever(embedder=embedder)
        
        # Try to load cached embeddings
        print("Checking for cached embeddings...")
        cached_embeddings = embedder.load_embeddings("dataset_embeddings")
        
        if cached_embeddings is not None:
            print(f"[OK] Found cached embeddings: {cached_embeddings.shape}")
            print("Using cached embeddings to build index...\n")
            retriever.build_index(dataset_path, embeddings=cached_embeddings)
        else:
            print("No cached embeddings found. Generating embeddings...")
            print("(This may take a while for large datasets)\n")
            retriever.build_index(dataset_path)
        
        # Save index
        retriever.save_index()
        
        print("\n" + "="*80)
        print("[SUCCESS] FAISS INDEX BUILT SUCCESSFULLY!")
        print("="*80)
        print(f"\nIndex contains {retriever.index.ntotal} vectors")
        print("[OK] Index saved to ./faiss_index/")
        print("\nThe retrieval system is now ready to:")
        print("  - Find similar historical tickets")
        print("  - Provide RAG context to Gemini")
        print("  - Ground responses in past resolutions")
        print("\nNext steps:")
        print("  1. Set GEMINI_API_KEY in .env file")
        print("  2. Start backend: python backend/app.py")
        print("  3. Start customer portal: streamlit run customer_portal/streamlit_app.py")
        print("  4. Start manager dashboard: streamlit run manager_dashboard/streamlit_dashboard.py")
        print("="*80 + "\n")
    
    except Exception as e:
        logger.error(f"Index building failed: {e}", exc_info=True)
        print(f"\n[ERROR] Index building failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
