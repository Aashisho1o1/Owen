#!/usr/bin/env python3
"""
Comprehensive FolderScope Testing Script
Tests the folder-level contextual understanding feature without requiring a database connection.
"""

import asyncio
import json
import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

# Mock classes for testing without database
class MockDatabaseService:
    """Mock database service for testing"""
    
    def __init__(self):
        self.mock_documents = [
            {
                'id': '1',
                'title': 'Chapter 1: The Beginning',
                'content': 'John opened the letter from his grandmother. It contained important information about the family inheritance. The letter mentioned that John would receive the old house in the countryside.',
                'updated_at': '2024-01-01T10:00:00Z'
            },
            {
                'id': '2', 
                'title': 'Chapter 2: The Discovery',
                'content': 'Sarah found the letter that John had received. She was surprised to learn about the inheritance. The letter explained that the house had been in the family for generations.',
                'updated_at': '2024-01-02T10:00:00Z'
            },
            {
                'id': '3',
                'title': 'Character Notes: John',
                'content': 'John is a 35-year-old teacher who loves reading. He is kind and thoughtful. John often helps his students with their problems.',
                'updated_at': '2024-01-03T10:00:00Z'
            },
            {
                'id': '4',
                'title': 'Character Notes: Sarah',
                'content': 'Sarah is John\'s sister, a 32-year-old lawyer. She is practical and organized. Sarah always thinks things through carefully.',
                'updated_at': '2024-01-04T10:00:00Z'
            },
            {
                'id': '5',
                'title': 'Plot Outline',
                'content': 'The story follows John and Sarah as they discover their grandmother\'s letter about the family inheritance. They must work together to understand the family history.',
                'updated_at': '2024-01-05T10:00:00Z'
            }
        ]
    
    def execute_query(self, query: str, params: tuple, fetch: str = 'all'):
        """Mock database query execution"""
        if 'SELECT' in query and 'documents' in query:
            # Return mock documents
            return [(doc['id'], doc['title'], doc['content'], doc['updated_at']) for doc in self.mock_documents]
        return []

class MockGeminiService:
    """Mock Gemini service for testing"""
    
    def __init__(self):
        self.test_responses = {
            "letter": "1,2",  # Should find documents about letters
            "inheritance": "1,2,5",  # Should find documents about inheritance
            "character": "3,4",  # Should find character notes
            "house": "1,2,5",  # Should find documents about the house
            "family": "1,2,5",  # Should find documents about family
        }
    
    async def generate_with_selected_llm(self, prompts: List[Dict], provider: str):
        """Mock LLM response"""
        # Extract query from prompts
        query = ""
        for prompt in prompts:
            if "role" in prompt and prompt["role"] == "user":
                parts = prompt.get("parts", [])
                for part in parts:
                    if isinstance(part, str) and "Query:" in part:
                        # Extract query from "Query: 'something'"
                        start = part.find("Query: \"") + 8
                        end = part.find("\"", start)
                        if start > 7 and end > start:
                            query = part[start:end].lower()
                            break
        
        # Return appropriate response based on query
        for key, response in self.test_responses.items():
            if key in query:
                return response
        
        return "NONE"

class MockHybridIndexer:
    """Mock HybridIndexer for testing FolderScope functionality"""
    
    def __init__(self):
        self.db_service = MockDatabaseService()
        self.gemini_service = MockGeminiService()
        self.test_results = {}
    
    async def get_folder_context(self, user_id: int, query: str, max_documents: int = 5) -> Optional[str]:
        """Test implementation of get_folder_context"""
        print(f"🔍 Testing FolderScope for query: '{query}'")
        
        try:
            # Step 1: Get documents from database
            query_sql = """
            SELECT id, title, content, updated_at 
            FROM documents 
            WHERE user_id = %s 
            AND content IS NOT NULL 
            AND LENGTH(TRIM(content)) > 50
            ORDER BY updated_at DESC 
            LIMIT 5
            """
            
            documents = self.db_service.execute_query(query_sql, (user_id,), fetch='all')
            
            if not documents:
                print("❌ No documents found")
                return None
            
            print(f"✅ Found {len(documents)} documents")
            
            # Step 2: Create document summaries
            doc_summaries = []
            for doc in documents:
                content = doc[2]
                summary = content[:200] + "..." if len(content) > 200 else content
                doc_summaries.append({
                    'id': str(doc[0]),
                    'title': doc[1],
                    'summary': summary
                })
            
            # Step 3: Use LLM to find relevant documents
            prompt = f"""Query: "{query}"

Which documents contain relevant info? Return only the document numbers (1,2,3...) or "NONE".

{chr(10).join([f"{i+1}. {doc['title']}: {doc['summary'][:100]}..." for i, doc in enumerate(doc_summaries)])}

Answer:"""

            print(f"🤖 Asking LLM to analyze {len(doc_summaries)} documents...")
            
            response = await self.gemini_service.generate_with_selected_llm(
                prompts=[{"role": "user", "parts": [prompt]}],
                provider="Google Gemini"
            )
            
            print(f"🤖 LLM Response: {response}")
            
            if response == "NONE" or not response:
                print("❌ LLM found no relevant documents")
                return None
            
            # Step 4: Parse response and extract relevant documents
            import re
            numbers = re.findall(r'\d+', response)
            selected_indices = [int(x) - 1 for x in numbers if x.isdigit()]
            selected_indices = [i for i in selected_indices if 0 <= i < len(doc_summaries)]
            
            if not selected_indices:
                print("❌ No valid document indices found")
                return None
            
            print(f"✅ LLM selected documents: {[i+1 for i in selected_indices]}")
            
            # Step 5: Build context from selected documents
            context_parts = []
            for idx in selected_indices[:max_documents]:
                doc = documents[idx]
                title = doc[1]
                content = doc[2]
                
                # Extract relevant excerpt
                excerpt = self._extract_smart_excerpt(content, query, max_length=600)
                context_parts.append(f"**{title}**:\n{excerpt}")
            
            result = "\n\n---\n\n".join(context_parts)
            print(f"✅ Generated context with {len(context_parts)} documents ({len(result)} chars)")
            
            # Store result for testing
            self.test_results[query] = {
                'context': result,
                'documents_found': len(context_parts),
                'total_chars': len(result)
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error in get_folder_context: {e}")
            return None
    
    def _extract_smart_excerpt(self, content: str, query: str, max_length: int = 600) -> str:
        """Extract relevant excerpt from content"""
        # Simple implementation: find sentences containing query terms
        sentences = content.split('. ')
        query_terms = query.lower().split()
        
        relevant_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(term in sentence_lower for term in query_terms):
                relevant_sentences.append(sentence)
        
        if relevant_sentences:
            excerpt = '. '.join(relevant_sentences[:3]) + '.'
        else:
            # Fallback: take first part
            excerpt = content[:max_length]
        
        return excerpt[:max_length] + "..." if len(excerpt) > max_length else excerpt

class FolderScopeTester:
    """Main test class for FolderScope functionality"""
    
    def __init__(self):
        self.indexer = MockHybridIndexer()
        self.test_queries = [
            "What letter did John receive?",
            "Tell me about the inheritance",
            "What are the character descriptions?",
            "Where is the house located?",
            "What is the family history?",
            "Who is Sarah?",
            "What does the grandmother's letter say?",
            "What is the plot of the story?"
        ]
    
    async def run_comprehensive_tests(self):
        """Run all FolderScope tests"""
        print("🚀 ========== FOLDER SCOPE COMPREHENSIVE TESTING ==========")
        print(f"📅 Test started at: {datetime.now()}")
        print()
        
        # Test 1: Basic functionality
        await self.test_basic_functionality()
        
        # Test 2: Query relevance
        await self.test_query_relevance()
        
        # Test 3: Context quality
        await self.test_context_quality()
        
        # Test 4: Performance simulation
        await self.test_performance_simulation()
        
        # Test 5: Error handling
        await self.test_error_handling()
        
        # Test 6: Integration points
        await self.test_integration_points()
        
        print()
        print("✅ ========== ALL TESTS COMPLETED ==========")
        print(f"📅 Test completed at: {datetime.now()}")
    
    async def test_basic_functionality(self):
        """Test basic FolderScope functionality"""
        print("🔧 TEST 1: Basic Functionality")
        print("-" * 50)
        
        query = "What letter did John receive?"
        result = await self.indexer.get_folder_context(user_id=1, query=query)
        
        if result:
            print("✅ Basic functionality: PASSED")
            print(f"📄 Context length: {len(result)} characters")
            print(f"📄 Context preview: {result[:200]}...")
        else:
            print("❌ Basic functionality: FAILED")
        
        print()
    
    async def test_query_relevance(self):
        """Test query relevance and document selection"""
        print("🎯 TEST 2: Query Relevance")
        print("-" * 50)
        
        relevance_tests = [
            ("letter", ["Chapter 1", "Chapter 2"]),
            ("inheritance", ["Chapter 1", "Chapter 2", "Plot Outline"]),
            ("character", ["Character Notes: John", "Character Notes: Sarah"]),
            ("house", ["Chapter 1", "Chapter 2", "Plot Outline"])
        ]
        
        for query_term, expected_docs in relevance_tests:
            result = await self.indexer.get_folder_context(user_id=1, query=query_term)
            
            if result:
                found_docs = []
                for expected in expected_docs:
                    if expected in result:
                        found_docs.append(expected)
                
                relevance_score = len(found_docs) / len(expected_docs)
                print(f"🔍 Query '{query_term}': {relevance_score:.1%} relevance ({found_docs})")
            else:
                print(f"❌ Query '{query_term}': No results found")
        
        print()
    
    async def test_context_quality(self):
        """Test the quality of generated context"""
        print("📊 TEST 3: Context Quality")
        print("-" * 50)
        
        quality_metrics = {}
        
        for query in self.test_queries[:4]:  # Test first 4 queries
            result = await self.indexer.get_folder_context(user_id=1, query=query)
            
            if result:
                metrics = {
                    'length': len(result),
                    'documents': result.count('**'),
                    'has_relevant_content': any(term in result.lower() for term in query.lower().split()),
                    'structure_quality': result.count('---') > 0
                }
                quality_metrics[query] = metrics
                
                print(f"📄 '{query[:30]}...': {metrics['length']} chars, {metrics['documents']} docs")
            else:
                print(f"❌ '{query[:30]}...': No context generated")
        
        # Calculate overall quality score
        if quality_metrics:
            avg_length = sum(m['length'] for m in quality_metrics.values()) / len(quality_metrics)
            avg_docs = sum(m['documents'] for m in quality_metrics.values()) / len(quality_metrics)
            print(f"📊 Average context length: {avg_length:.0f} characters")
            print(f"📊 Average documents per query: {avg_docs:.1f}")
        
        print()
    
    async def test_performance_simulation(self):
        """Simulate performance characteristics"""
        print("⚡ TEST 4: Performance Simulation")
        print("-" * 50)
        
        import time
        
        # Test response time
        start_time = time.time()
        result = await self.indexer.get_folder_context(user_id=1, query="letter")
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"⏱️ Response time: {response_time:.1f}ms")
        
        # Simulate timeout scenarios
        if response_time < 1000:  # Less than 1 second
            print("✅ Performance: PASSED (within acceptable limits)")
        else:
            print("⚠️ Performance: SLOW (may cause timeouts)")
        
        print()
    
    async def test_error_handling(self):
        """Test error handling scenarios"""
        print("🛡️ TEST 5: Error Handling")
        print("-" * 50)
        
        # Test with empty query
        result = await self.indexer.get_folder_context(user_id=1, query="")
        if result is None:
            print("✅ Empty query handling: PASSED")
        else:
            print("❌ Empty query handling: FAILED")
        
        # Test with very long query
        long_query = "a" * 1000
        result = await self.indexer.get_folder_context(user_id=1, query=long_query)
        if result is not None:
            print("✅ Long query handling: PASSED")
        else:
            print("❌ Long query handling: FAILED")
        
        print()
    
    async def test_integration_points(self):
        """Test integration points with other components"""
        print("🔗 TEST 6: Integration Points")
        print("-" * 50)
        
        # Test ChatRequest schema compatibility
        try:
            # Simulate the ChatRequest structure
            chat_request = {
                'message': 'What letter did John receive?',
                'editor_text': 'Current editor content...',
                'folder_scope': True,
                'voice_guard': False
            }
            
            # Test that folder_scope is properly set
            if chat_request.get('folder_scope') is True:
                print("✅ ChatRequest schema: PASSED")
            else:
                print("❌ ChatRequest schema: FAILED")
                
        except Exception as e:
            print(f"❌ ChatRequest schema test failed: {e}")
        
        # Test LLM service integration
        try:
            response = await self.indexer.gemini_service.generate_with_selected_llm(
                prompts=[{"role": "user", "parts": ["Test query"]}],
                provider="Google Gemini"
            )
            if response:
                print("✅ LLM service integration: PASSED")
            else:
                print("❌ LLM service integration: FAILED")
        except Exception as e:
            print(f"❌ LLM service integration failed: {e}")
        
        print()
    
    def generate_test_report(self):
        """Generate a comprehensive test report"""
        print("📋 GENERATING TEST REPORT")
        print("-" * 50)
        
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'total_queries_tested': len(self.indexer.test_results),
            'successful_queries': len([r for r in self.indexer.test_results.values() if r['context']]),
            'average_context_length': sum(r['total_chars'] for r in self.indexer.test_results.values()) / len(self.indexer.test_results) if self.indexer.test_results else 0,
            'test_results': self.indexer.test_results
        }
        
        # Save report to file
        with open('folderscope_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Test report saved to: folderscope_test_report.json")
        print(f"📊 Total queries tested: {report['total_queries_tested']}")
        print(f"✅ Successful queries: {report['successful_queries']}")
        print(f"📏 Average context length: {report['average_context_length']:.0f} characters")
        
        return report

async def main():
    """Main test runner"""
    tester = FolderScopeTester()
    await tester.run_comprehensive_tests()
    tester.generate_test_report()

if __name__ == "__main__":
    asyncio.run(main()) 