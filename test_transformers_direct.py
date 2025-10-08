#!/usr/bin/env python3
"""
Test Direct Transformers Integration

Tests the updated HuggingFace transformers service that uses the library directly
for local model loading and inference with your provided token.
"""

import asyncio
import os
import sys
import time
from typing import Dict, Any
from dotenv import load_dotenv

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

load_dotenv()

def print_banner(title: str):
    """Print a formatted banner"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def print_result(test_name: str, result: Dict[str, Any], duration: float):
    """Print formatted test results"""
    status = "✅ PASS" if result and not result.get('error') else "❌ FAIL"
    print(f"\n{status} {test_name} ({duration:.2f}s)")
    
    if isinstance(result, dict):
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            # Print key metrics
            for key, value in result.items():
                if key in ['provider', 'model_used', 'processing_time', 'tokens_generated']:
                    print(f"   📊 {key}: {value}")
            
            # Show part of response for text generation
            if 'response' in result and len(str(result['response'])) > 100:
                preview = str(result['response'])[:200] + "..."
                print(f"   📝 Response preview: {preview}")
            elif 'explanation' in result:
                print(f"   💬 Explanation: {result['explanation']}")

class DirectTransformersTest:
    """Test suite for direct transformers integration"""
    
    def __init__(self):
        self.service = None
        
    async def setup(self):
        """Initialize the transformers service"""
        print_banner("🤗 Direct Transformers Integration Test")
        
        # Set the HuggingFace token
        os.environ["HUGGINGFACE_API_KEY"] = "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"
        
        try:
            # Import the direct transformers service
            from backend.services.llm.huggingface_transformers_service import huggingface_transformers_service
            self.service = huggingface_transformers_service
            
            print("✅ Direct transformers service imported")
            print(f"🎯 Default model: {self.service.default_model}")
            print(f"🖥️  Device detection: {self.service.device}")
            
            return True
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_device_detection(self):
        """Test device detection and system info"""
        print_banner("🖥️ Testing Device Detection")
        
        start_time = time.time()
        try:
            model_info = self.service.get_model_info()
            
            duration = time.time() - start_time
            result = {
                "device_info": self.service.device_info,
                "available_models": model_info["available_models"],
                "loaded_models": model_info["loaded_models"],
                "memory_info": model_info.get("memory_usage", {})
            }
            
            print_result("Device Detection", result, duration)
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = {"error": str(e)}
            print_result("Device Detection", result, duration)
            return result
    
    async def test_simple_generation(self):
        """Test basic text generation"""
        print_banner("📝 Testing Simple Text Generation")
        
        prompt = "Hello, I am an AI assistant. Let me introduce myself:"
        
        start_time = time.time()
        try:
            response = await self.service.generate_text(
                prompt=prompt,
                model_name="gpt-oss-20b",  # Use smaller model first
                max_new_tokens=100,
                temperature=0.7
            )
            
            duration = time.time() - start_time
            result = {
                "response": response,
                "processing_time": duration,
                "model_used": "gpt-oss-20b",
                "provider": "huggingface_transformers"
            }
            
            print_result("Simple Text Generation", result, duration)
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = {"error": str(e)}
            print_result("Simple Text Generation", result, duration)
            return result
    
    async def test_dialogue_consistency_check(self):
        """Test dialogue consistency checking"""
        print_banner("🎭 Testing Dialogue Consistency Check")
        
        dialogue = "Good evening, I trust you are well today, old chap?"
        character = "A refined British gentleman, formal speech patterns"
        
        start_time = time.time()
        try:
            result = await self.service.quick_consistency_check(dialogue, character)
            
            duration = time.time() - start_time
            result["processing_time"] = duration
            
            print_result("Dialogue Consistency Check", result, duration)
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = {"error": str(e)}
            print_result("Dialogue Consistency Check", result, duration)
            return result
    
    async def test_json_generation(self):
        """Test structured JSON generation"""
        print_banner("🗂️ Testing JSON Generation")
        
        prompt = "Analyze the writing style of this sentence: 'The cat sat on the mat.'"
        schema = {
            "style": "str",
            "tone": "str", 
            "complexity": "int (1-10)",
            "improvements": ["str"]
        }
        
        start_time = time.time()
        try:
            result = await self.service.generate_structured(
                prompt=prompt,
                schema=schema,
                model_name="gpt-oss-20b",
                max_new_tokens=200
            )
            
            duration = time.time() - start_time
            result["processing_time"] = duration
            result["model_used"] = "gpt-oss-20b"
            
            print_result("JSON Generation", result, duration)
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = {"error": str(e)}
            print_result("JSON Generation", result, duration)
            return result
    
    async def test_conversation_history(self):
        """Test conversation with history"""
        print_banner("💬 Testing Conversation History")
        
        conversation = [
            {"role": "user", "content": "What's your name?"},
            {"role": "assistant", "content": "I'm Claude, an AI assistant."},
            {"role": "user", "content": "What can you help me with?"}
        ]
        
        start_time = time.time()
        try:
            response = await self.service.generate_with_conversation_history(conversation)
            
            duration = time.time() - start_time
            result = {
                "response": response,
                "processing_time": duration,
                "conversation_length": len(conversation),
                "model_used": self.service.default_model
            }
            
            print_result("Conversation History", result, duration)
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = {"error": str(e)}
            print_result("Conversation History", result, duration)
            return result
    
    async def test_model_info_and_cache(self):
        """Test model information and caching"""
        print_banner("🔍 Testing Model Info & Caching")
        
        start_time = time.time()
        try:
            # Get model info
            info = self.service.get_model_info()
            
            # Test cache statistics
            initial_cache_hits = self.service.usage_stats["cache_hits"]
            
            # Make another call to test caching
            await self.service.generate_text("Test cache", max_new_tokens=10)
            
            final_cache_hits = self.service.usage_stats["cache_hits"]
            
            duration = time.time() - start_time
            result = {
                "loaded_models": info["loaded_models"],
                "usage_stats": self.service.usage_stats,
                "cache_improvement": final_cache_hits > initial_cache_hits,
                "memory_usage": info.get("memory_usage", {})
            }
            
            print_result("Model Info & Caching", result, duration)
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = {"error": str(e)}
            print_result("Model Info & Caching", result, duration)
            return result
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        if not await self.setup():
            return False
        
        print("🎯 Testing Direct HuggingFace Transformers Integration")
        print(f"🔑 Using token: hf_FgWUBDRE...vsBY")
        
        tests = [
            self.test_device_detection(),
            self.test_simple_generation(),
            self.test_dialogue_consistency_check(),
            self.test_json_generation(),
            self.test_conversation_history(),
            self.test_model_info_and_cache()
        ]
        
        results = []
        for test in tests:
            try:
                result = await test
                results.append(result)
                
                # Small delay between tests
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                results.append({"error": str(e)})
        
        # Summary
        print_banner("📊 Test Summary")
        
        passed = len([r for r in results if r and not r.get('error')])
        total = len(results)
        
        print(f"✅ Tests passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed! Direct transformers integration is working.")
        elif passed > 0:
            print("⚠️  Some tests passed. Check errors above for issues.")
        else:
            print("❌ All tests failed. Check your environment and dependencies.")
        
        # Show final stats
        if self.service:
            stats = self.service.usage_stats
            print(f"\n📈 Final Usage Stats:")
            print(f"   Models loaded: {stats['models_loaded']}")
            print(f"   Inference calls: {stats['inference_calls']}")
            print(f"   Tokens generated: {stats['total_tokens_generated']}")
            print(f"   Cache hits: {stats['cache_hits']}")
        
        return passed == total

async def main():
    """Main test runner"""
    print("🚀 Direct HuggingFace Transformers Test Suite")
    print("=" * 50)
    
    # Check PyTorch availability
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} detected")
        if torch.cuda.is_available():
            print(f"🎮 CUDA available: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            print("🍎 Apple MPS available")
        else:
            print("🖥️  CPU mode (slower but functional)")
    except ImportError:
        print("❌ PyTorch not installed - install with: pip install torch")
        return
    
    # Check transformers availability
    try:
        import transformers
        print(f"✅ Transformers {transformers.__version__} detected")
    except ImportError:
        print("❌ Transformers not installed - install with: pip install transformers")
        return
    
    # Run tests
    tester = DirectTransformersTest()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 Ready to use direct transformers integration!")
        print("💡 Benefits:")
        print("   • Local model loading and inference")
        print("   • GPU acceleration when available") 
        print("   • Model quantization for efficiency")
        print("   • Zero API costs after model download")
        print("   • Complete privacy (no data sent to cloud)")
    else:
        print("\n⚠️  Integration needs attention. Check errors above.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)