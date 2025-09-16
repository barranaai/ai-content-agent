#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append('.')

from rag_system import BarranaRAGSystem

def test_rag_initialization():
    """Test RAG system initialization"""
    
    print("🔧 Testing RAG System Initialization")
    print("=" * 50)
    
    try:
        # Initialize RAG system
        rag_system = BarranaRAGSystem()
        print(f"✅ RAG System created")
        
        # Try to initialize
        success = rag_system.initialize()
        print(f"📊 Initialization result: {success}")
        
        if success:
            print(f"✅ RAG System initialized successfully")
            print(f"📊 Stats: {rag_system.get_stats()}")
            
            # Test context retrieval
            test_query = "school reporting systems"
            context = rag_system.get_context(test_query, top_k=3, min_score=0.7)
            print(f"🔍 Test query: '{test_query}'")
            print(f"📝 Retrieved context: {len(context)} characters")
            if context:
                print(f"📄 Context preview: {context[:200]}...")
            else:
                print("❌ No context retrieved")
        else:
            print("❌ RAG System initialization failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_initialization()
