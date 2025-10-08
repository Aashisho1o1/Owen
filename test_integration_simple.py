#!/usr/bin/env python3
"""
Simple Integration Test

Tests the enhanced LLM integration without requiring heavy dependencies.
Focuses on service initialization and configuration validation.
"""

import os
import sys
from typing import Dict, Any

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all enhanced services can be imported"""
    print("🔍 Testing Enhanced LLM Service Imports...")
    
    results = {}
    
    # Test base service
    try:
        from backend.services.llm.base_service import BaseLLMService, LLMError
        results["base_service"] = "✅ Available"
    except Exception as e:
        results["base_service"] = f"❌ Failed: {e}"
    
    # Test existing services
    try:
        from backend.services.llm.ollama_service import ollama_service
        results["ollama_service"] = "✅ Available"
    except Exception as e:
        results["ollama_service"] = f"❌ Failed: {e}"
    
    try:
        from backend.services.llm.gemini_service import gemini_service
        results["gemini_service"] = "✅ Available"
    except Exception as e:
        results["gemini_service"] = f"❌ Failed: {e}"
    
    # Test new HuggingFace service (API version)
    try:
        from backend.services.llm.huggingface_service import huggingface_service
        results["huggingface_api_service"] = "✅ Available"
    except Exception as e:
        results["huggingface_api_service"] = f"❌ Failed: {e}"
    
    # Test new HuggingFace transformers service
    try:
        from backend.services.llm.huggingface_transformers_service import huggingface_transformers_service
        results["huggingface_transformers_service"] = "⚠️  Available (requires PyTorch)"
    except Exception as e:
        results["huggingface_transformers_service"] = f"❌ Failed: {e}"
    
    # Test hybrid service
    try:
        from backend.services.llm.hybrid_service import hybrid_llm_service
        results["hybrid_service"] = "✅ Available"
    except Exception as e:
        results["hybrid_service"] = f"❌ Failed: {e}"
    
    # Test main service coordinator
    try:
        from backend.services.llm_service import llm_service
        results["main_llm_service"] = "✅ Available"
    except Exception as e:
        results["main_llm_service"] = f"❌ Failed: {e}"
    
    return results

def test_configuration():
    """Test configuration and environment setup"""
    print("🔧 Testing Configuration...")
    
    results = {}
    
    # Check for HuggingFace token
    hf_token = os.getenv("HUGGINGFACE_API_KEY")
    if hf_token:
        if hf_token.startswith("hf_") and len(hf_token) > 10:
            results["huggingface_token"] = "✅ Valid format"
        else:
            results["huggingface_token"] = "⚠️  Invalid format"
    else:
        results["huggingface_token"] = "❌ Not set"
    
    # Check other API keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    results["gemini_api_key"] = "✅ Set" if gemini_key else "⚠️  Not set"
    
    openai_key = os.getenv("OPENAI_API_KEY")
    results["openai_api_key"] = "✅ Set" if openai_key else "⚠️  Not set"
    
    return results

def test_service_initialization():
    """Test service initialization and provider detection"""
    print("🚀 Testing Service Initialization...")
    
    results = {}
    
    try:
        # Set HuggingFace token for testing
        os.environ["HUGGINGFACE_API_KEY"] = "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"
        
        from backend.services.llm_service import llm_service
        
        # Test provider detection
        available_providers = llm_service.get_available_providers()
        results["available_providers"] = f"✅ Found {len(available_providers)}: {', '.join(available_providers)}"
        
        # Test default provider selection
        default_provider = llm_service.default_provider
        results["default_provider"] = f"✅ Selected: {default_provider}"
        
        # Test provider priority logic
        priority_order = ["Local gpt-oss", "HuggingFace gpt-oss", "Google Gemini", "OpenAI GPT"]
        for provider in priority_order:
            if provider in available_providers:
                expected_default = provider
                break
        
        if default_provider == expected_default:
            results["provider_priority"] = "✅ Correct priority order"
        else:
            results["provider_priority"] = f"⚠️  Expected {expected_default}, got {default_provider}"
        
    except Exception as e:
        results["service_initialization"] = f"❌ Failed: {e}"
    
    return results

def test_hybrid_routing():
    """Test hybrid routing configuration"""
    print("🧠 Testing Hybrid Routing...")
    
    results = {}
    
    try:
        from backend.services.llm.hybrid_service import hybrid_llm_service
        
        # Test routing rules
        routing_rules = hybrid_llm_service.routing_rules
        results["routing_rules"] = f"✅ {len(routing_rules)} rules configured"
        
        # Check for our new providers
        rule_providers = set()
        for rule in routing_rules.values():
            rule_providers.add(rule.preferred_provider.value)
            for fallback in rule.fallback_providers:
                rule_providers.add(fallback.value)
        
        expected_providers = {"local_20b", "local_120b", "hf_20b", "hf_120b", "cloud_gemini"}
        missing_providers = expected_providers - rule_providers
        
        if not missing_providers:
            results["provider_coverage"] = "✅ All providers covered in routing"
        else:
            results["provider_coverage"] = f"⚠️  Missing: {missing_providers}"
        
        # Test cost estimation
        try:
            from backend.services.llm.hybrid_service import ProviderType
            hf_cost = hybrid_llm_service._estimate_cost(ProviderType.HF_FAST, 1000)
            local_cost = hybrid_llm_service._estimate_cost(ProviderType.LOCAL_FAST, 1000)
            
            results["cost_estimation"] = f"✅ HF: ${hf_cost:.4f}, Local: ${local_cost:.4f}"
        except Exception as e:
            results["cost_estimation"] = f"⚠️  Error: {e}"
        
    except Exception as e:
        results["hybrid_routing"] = f"❌ Failed: {e}"
    
    return results

def test_file_structure():
    """Test that all new files are in place"""
    print("📁 Testing File Structure...")
    
    results = {}
    
    expected_files = [
        "backend/services/llm/huggingface_service.py",
        "backend/services/llm/huggingface_transformers_service.py", 
        "setup_enhanced_ai.sh",
        "test_enhanced_llm_integration.py",
        "test_transformers_direct.py",
        "backend/.env.example",
        "ENHANCED_AI_IMPLEMENTATION.md"
    ]
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            results[file_path] = f"✅ {size:,} bytes"
        else:
            results[file_path] = "❌ Missing"
    
    return results

def main():
    """Run all tests"""
    print("🧪 Enhanced LLM Integration - Simple Test Suite")
    print("=" * 60)
    
    all_results = {}
    
    # Run all test categories
    test_categories = [
        ("Imports", test_imports),
        ("Configuration", test_configuration), 
        ("Service Initialization", test_service_initialization),
        ("Hybrid Routing", test_hybrid_routing),
        ("File Structure", test_file_structure)
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for category_name, test_func in test_categories:
        print(f"\n{category_name}:")
        print("-" * 40)
        
        try:
            category_results = test_func()
            all_results[category_name] = category_results
            
            for test_name, result in category_results.items():
                print(f"  {test_name}: {result}")
                total_tests += 1
                if result.startswith("✅"):
                    passed_tests += 1
        except Exception as e:
            print(f"  ❌ Category failed: {e}")
            all_results[category_name] = {"error": str(e)}
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ Tests passed: {passed_tests}/{total_tests}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! Your enhanced LLM integration is ready!")
        print("\n💡 Key Features Available:")
        print("   • Multi-provider LLM system")
        print("   • HuggingFace integration with your token")
        print("   • Smart hybrid routing")
        print("   • Cost optimization")
        print("   • Local and cloud model support")
        
        print("\n🚀 Next Steps:")
        print("   1. Install PyTorch for local transformers: pip install torch")
        print("   2. Install transformers: pip install transformers accelerate")
        print("   3. Run full test: python test_enhanced_llm_integration.py")
        print("   4. Start backend: cd backend && python -m uvicorn main:app --reload")
        
    elif success_rate >= 70:
        print("⚠️  GOOD! Most components working, some issues to address.")
        print("   Check failed tests above and resolve dependencies.")
        
    else:
        print("❌ NEEDS WORK! Multiple issues detected.")
        print("   Review error messages and check your environment setup.")
    
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    return success_rate >= 90

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)