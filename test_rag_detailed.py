#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append('.')

from rag_system import BarranaRAGSystem

def test_rag_detailed():
    """Test RAG system with detailed debugging"""
    
    print("🔧 Testing RAG System with Detailed Debugging")
    print("=" * 60)
    
    try:
        # Initialize RAG system
        rag_system = BarranaRAGSystem()
        success = rag_system.initialize()
        
        if success:
            print(f"✅ RAG System initialized successfully")
            print(f"📊 Stats: {rag_system.get_stats()}")
            
            # Test different queries and thresholds
            test_queries = [
                "school reporting systems",
                "AI automation",
                "Barrana",
                "business automation",
                "workflow automation"
            ]
            
            thresholds = [0.7, 0.5, 0.3, 0.1]
            
            for query in test_queries:
                print(f"\n🔍 Testing query: '{query}'")
                for threshold in thresholds:
                    chunks = rag_system.retrieve(query, top_k=3, min_score=threshold)
                    print(f"  Threshold {threshold}: {len(chunks)} chunks")
                    if chunks:
                        for chunk in chunks:
                            print(f"    Score: {chunk['similarity_score']:.3f} - {chunk['text'][:50]}...")
                        break
                else:
                    print(f"  ❌ No relevant chunks found for '{query}'")
            
            # Test context generation
            print(f"\n📝 Testing context generation:")
            context = rag_system.get_context("AI automation", top_k=3, min_score=0.1)
            print(f"Context length: {len(context)} characters")
            if context:
                print(f"Context preview: {context[:300]}...")
            else:
                print("❌ No context generated")
                
        else:
            print("❌ RAG System initialization failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_detailed()
