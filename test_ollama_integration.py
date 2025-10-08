#!/usr/bin/env python3
"""
Ollama Integration Test Script

Tests the OpenAI gpt-oss integration with our DOG Writer backend.
Run this to verify everything is working before using in production.
"""

import asyncio
import sys
import os
import json
import time

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_ollama_setup():
    """Test basic Ollama setup and model availability"""
    print("🏠 Testing Ollama Setup...")
    print("=" * 50)
    
    try:
        from backend.services.llm.ollama_service import ollama_service
        
        # Test 1: Check Ollama status
        print("\n1. Checking Ollama status...")
        status = await ollama_service.check_ollama_status()
        
        if status["status"] == "healthy":
            print("✅ Ollama is running!")
            models = status.get("gpt_oss_models", [])
            print(f"   Available gpt-oss models: {models}")
            
            if models:
                print("🎉 Local models are ready for inference!")
                return True
            else:
                print("⚠️ No gpt-oss models found.")
                print("   Run: ollama pull gpt-oss:20b")
                return False
        else:
            print("❌ Ollama is not running or has issues:")
            print(f"   {status.get('message', 'Unknown error')}")
            
            if "setup_instructions" in status:
                print("\n📋 Setup Instructions:")
                for instruction in status["setup_instructions"]:
                    print(f"   {instruction}")
            
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_dialogue_consistency():
    """Test dialogue consistency checking"""
    print("\n🎭 Testing Dialogue Consistency...")
    print("=" * 50)
    
    try:
        from backend.services.llm.ollama_service import ollama_service
        
        # Test data
        test_dialogue = "Well, I reckon that's mighty fine, partner!"
        test_character = "A refined British gentleman who speaks formally and precisely"
        
        print(f"\nTest Case:")
        print(f"Character: {test_character}")
        print(f"Dialogue: '{test_dialogue}'")
        print(f"Expected: Inconsistent (cowboy speech vs British gentleman)")
        
        # Test quick consistency check
        print(f"\n🚀 Running quick consistency check...")
        start_time = time.time()
        
        result = await ollama_service.quick_consistency_check(
            new_dialogue=test_dialogue,
            character_context=test_character
        )
        
        processing_time = time.time() - start_time
        
        print(f"✅ Results ({processing_time:.2f}s):")
        print(f"   Consistent: {result['is_consistent']}")
        print(f"   Explanation: {result['explanation'][:100]}...")
        print(f"   Model used: {result['model_used']}")
        print(f"   Cost: ${result['cost']:.4f}")
        
        if processing_time < 15:
            print("🎯 Great! Response time under 15 seconds")
        else:
            print("⚠️ Response time is slow - consider using 20B model only")
            
        return True
        
    except Exception as e:
        print(f"❌ Error in dialogue consistency test: {e}")
        return False

async def test_hybrid_routing():
    """Test hybrid service routing"""
    print("\n🧠 Testing Hybrid Service Routing...")
    print("=" * 50)
    
    try:
        from backend.services.llm.hybrid_service import hybrid_llm_service, quick_consistency_check
        
        # Test quick routing
        print("\n1. Testing quick consistency routing...")
        
        test_dialogue = "I ain't gonna do that, no sir!"
        test_character = "A polite, well-educated character who never uses contractions"
        
        start_time = time.time()
        result = await quick_consistency_check(test_dialogue, test_character)
        processing_time = time.time() - start_time
        
        print(f"✅ Hybrid routing result ({processing_time:.2f}s):")
        print(f"   Provider used: {result.get('routing_info', {}).get('provider_used', 'unknown')}")
        print(f"   Cost: ${result.get('routing_info', {}).get('cost_estimate', 0):.4f}")
        print(f"   Fallback used: {result.get('routing_info', {}).get('fallback_used', False)}")
        
        # Test cost analytics
        print("\n2. Testing cost analytics...")
        analytics = await hybrid_llm_service.get_cost_analytics()
        
        if "summary" in analytics:
            print(f"✅ Analytics generated:")
            print(f"   Total requests: {analytics['summary']['total_requests']}")
            print(f"   Success rate: {analytics['summary']['success_rate']}")
        else:
            print(f"📊 Analytics: {analytics.get('message', 'No data yet')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in hybrid routing test: {e}")
        return False

async def test_performance_benchmark():
    """Benchmark performance against different models"""
    print("\n⚡ Performance Benchmark...")
    print("=" * 50)
    
    try:
        from backend.services.llm.ollama_service import ollama_service
        
        test_prompt = "Analyze this dialogue for character consistency: 'Hello there, good sir! How art thou on this fine day?' Character: A modern teenager who uses contemporary slang."
        
        models_to_test = [
            ("20b", "Fast model"), 
            ("120b", "Powerful model")
        ]
        
        results = {}
        
        for model_variant, description in models_to_test:
            print(f"\n🔬 Testing {description} (gpt-oss:{model_variant})...")
            
            try:
                start_time = time.time()
                response = await ollama_service.generate_text(
                    prompt=test_prompt,
                    model_variant=model_variant,
                    max_tokens=500
                )
                end_time = time.time()
                
                processing_time = end_time - start_time
                results[model_variant] = {
                    "time": processing_time,
                    "success": True,
                    "response_length": len(response)
                }
                
                print(f"   ✅ Success: {processing_time:.2f}s")
                print(f"   Response length: {len(response)} characters")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                results[model_variant] = {
                    "time": 0,
                    "success": False,
                    "error": str(e)
                }
        
        # Summary
        print(f"\n📊 Benchmark Summary:")
        successful_tests = [k for k, v in results.items() if v["success"]]
        
        if successful_tests:
            fastest = min(successful_tests, key=lambda k: results[k]["time"])
            print(f"   🏆 Fastest model: gpt-oss:{fastest} ({results[fastest]['time']:.2f}s)")
            
            if results["20b"]["success"] and results["120b"]["success"]:
                speed_diff = results["120b"]["time"] - results["20b"]["time"]
                print(f"   📈 120B is {speed_diff:.1f}s slower than 20B")
        
        return len(successful_tests) > 0
        
    except Exception as e:
        print(f"❌ Error in performance benchmark: {e}")
        return False

async def test_cost_savings_calculation():
    """Calculate potential cost savings"""
    print("\n💰 Cost Savings Analysis...")
    print("=" * 50)
    
    # Simulate usage patterns
    usage_scenarios = [
        {"name": "Light Writer", "requests_per_month": 100, "avg_tokens": 500},
        {"name": "Regular User", "requests_per_month": 500, "avg_tokens": 750},
        {"name": "Heavy User", "requests_per_month": 2000, "avg_tokens": 1000},
        {"name": "Writing Team", "requests_per_month": 10000, "avg_tokens": 800}
    ]
    
    # Cost estimates (rough)
    cloud_cost_per_1k_tokens = 0.002  # ~$0.002 per 1K tokens for Gemini
    
    print(f"\n📊 Monthly Cost Comparison:")
    print(f"{'Scenario':<15} {'Requests':<10} {'Cloud Cost':<12} {'Local Cost':<12} {'Savings':<10}")
    print("-" * 65)
    
    total_annual_savings = 0
    
    for scenario in usage_scenarios:
        monthly_requests = scenario["requests_per_month"]
        avg_tokens = scenario["avg_tokens"]
        
        # Calculate cloud costs
        total_tokens = monthly_requests * avg_tokens
        cloud_monthly_cost = (total_tokens / 1000) * cloud_cost_per_1k_tokens
        local_monthly_cost = 0.0  # Free!
        monthly_savings = cloud_monthly_cost
        
        total_annual_savings += monthly_savings * 12
        
        print(f"{scenario['name']:<15} {monthly_requests:<10} ${cloud_monthly_cost:<11.2f} ${local_monthly_cost:<11.2f} ${monthly_savings:<9.2f}")
    
    print("-" * 65)
    print(f"💡 Total Annual Savings Potential: ${total_annual_savings:.2f}")
    print(f"🏆 ROI on local setup: Immediate (first month)")
    
    return True

async def main():
    """Run all tests"""
    print("🚀 DOG Writer - OpenAI gpt-oss Integration Test")
    print("=" * 60)
    print("Testing local AI models for dialogue consistency detection")
    print("=" * 60)
    
    tests = [
        ("Ollama Setup", test_ollama_setup),
        ("Dialogue Consistency", test_dialogue_consistency),
        ("Hybrid Routing", test_hybrid_routing),
        ("Performance Benchmark", test_performance_benchmark),
        ("Cost Savings", test_cost_savings_calculation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n" + "="*60)
            result = await test_func()
            results[test_name] = result
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
            results[test_name] = False
    
    # Final summary
    print(f"\n" + "="*60)
    print("🏁 FINAL TEST RESULTS")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your OpenAI gpt-oss integration is ready!")
    elif passed > 0:
        print("⚠️ Some tests passed. Check failed tests above.")
    else:
        print("❌ All tests failed. Please check your Ollama setup.")
    
    print(f"\n📋 Next Steps:")
    if results.get("Ollama Setup", False):
        print("   1. ✅ Ollama is working - great!")
        print("   2. 🔄 Update your frontend to use the new /api/local-ai endpoints")
        print("   3. 📊 Monitor cost savings with /api/local-ai/cost-analytics")
    else:
        print("   1. 🚀 Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("   2. 📥 Download model: ollama pull gpt-oss:20b")
        print("   3. 🔄 Re-run this test script")

if __name__ == "__main__":
    asyncio.run(main())
