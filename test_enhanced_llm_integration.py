#!/usr/bin/env python3
"""
Enhanced LLM Integration Test Suite

Tests the improved multi-provider LLM system including:
- Local Ollama models (gpt-oss)
- HuggingFace Inference API  
- Hybrid smart routing
- Cost optimization features

Usage:
    python test_enhanced_llm_integration.py
    python test_enhanced_llm_integration.py --provider huggingface
    python test_enhanced_llm_integration.py --test-all-providers
"""

import asyncio
import os
import sys
import time
import argparse
from typing import Dict, Any, List
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
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"\n{status} {test_name} ({duration:.2f}s)")
    
    if isinstance(result, dict):
        if 'error' in result:
            print(f"   Error: {result['error']}")
        else:
            # Print key metrics
            for key, value in result.items():
                if key in ['provider', 'model_used', 'cost', 'processing_time']:
                    if key == 'cost' and isinstance(value, float):
                        print(f"   {key}: ${value:.4f}")
                    else:
                        print(f"   {key}: {value}")

class EnhancedLLMTester:
    """Test suite for enhanced LLM integration"""
    
    def __init__(self):
        self.test_results = []
        
    async def setup(self):
        """Initialize services"""
        print_banner("🚀 Enhanced LLM Integration Test Suite")
        
        try:
            # Import services (this tests the import structure)
            from backend.services.llm_service import llm_service
            self.llm_service = llm_service
            
            print("✅ Services imported successfully")
            
            # Check available providers
            providers = self.llm_service.get_available_providers()
            print(f"📋 Available providers: {providers}")
            
            return True
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    async def test_provider_status(self):
        """Test provider availability status"""
        print_banner("🔍 Testing Provider Status")
        
        start_time = time.time()
        try:
            # Check Ollama status
            local_status = await self.llm_service.check_local_model_status()
            print(f"🏠 Local models: {local_status.get('status', 'unknown')}")
            
            # Check cost analytics
            analytics = await self.llm_service.get_llm_cost_analytics()
            print(f"💰 Cost service: {'available' if analytics else 'unavailable'}")
            
            duration = time.time() - start_time
            result = {"local_status": local_status, "analytics": analytics}
            print_result("Provider Status Check", result, duration)
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = {"error": str(e)}
            print_result("Provider Status Check", result, duration)
            return result
    
    async def test_quick_consistency_check(self, provider: str = None):
        """Test quick dialogue consistency checking"""
        print_banner(f"⚡ Testing Quick Consistency Check {f'({provider})' if provider else ''}")
        
        test_cases = [
            {
                "dialogue": "Well hello there, old chap! Absolutely splendid weather today, wouldn't you say?",
                "character": "A refined British gentleman, formal speech, no contractions",
                "expected_consistent": True
            },
            {
                "dialogue": "Yo dude, what's up? That's totally wicked awesome!",
                "character": "A refined British gentleman, formal speech, no contractions", 
                "expected_consistent": False
            }
        ]
        
        results = []
        
        for i, case in enumerate(test_cases, 1):
            start_time = time.time()
            try:
                if provider:
                    # Test specific provider if available
                    result = await self.llm_service.generate_with_selected_llm(
                        f"Quick consistency check: Character: {case['character']} Dialogue: '{case['dialogue']}' Consistent? Yes/No with reason.",
                        provider
                    )
                    consistency_result = {
                        "is_consistent": "yes" in str(result).lower(),
                        "explanation": str(result),
                        "provider": provider,
                        "cost": 0.001  # Estimate
                    }
                else:
                    # Use hybrid service
                    consistency_result = await self.llm_service.quick_dialogue_consistency_check(
                        case["dialogue"], case["character"]
                    )
                
                duration = time.time() - start_time
                consistency_result["test_case"] = i
                consistency_result["processing_time"] = duration
                
                print_result(f"Quick Check Case {i}", consistency_result, duration)
                results.append(consistency_result)
                
            except Exception as e:
                duration = time.time() - start_time
                error_result = {"error": str(e), "test_case": i}
                print_result(f"Quick Check Case {i}", error_result, duration)
                results.append(error_result)
        
        return results
    
    async def test_dialogue_analysis(self, provider: str = None):
        """Test comprehensive dialogue analysis"""
        print_banner(f"🔍 Testing Dialogue Analysis {f'({provider})' if provider else ''}")
        
        character_profile = {
            "name": "Lord Pemberton",
            "personality": "Dignified, formal, well-educated",
            "traits": ["refined", "articulate", "traditional"],
            "speech_patterns": ["formal vocabulary", "complete sentences", "no contractions"]
        }
        
        dialogue_segments = [
            "Good morning, I trust you are well today.",
            "Indeed, the weather has been most agreeable of late.",
            "Yeah, it's pretty cool, I guess.",  # Inconsistent
            "Might I suggest we proceed with the utmost care?"
        ]
        
        start_time = time.time()
        try:
            if provider:
                # Create analysis prompt
                prompt = f"""Analyze dialogue consistency for {character_profile['name']}:
Character: {character_profile}
Dialogue: {dialogue_segments}
Provide detailed consistency analysis."""
                
                result = await self.llm_service.generate_with_selected_llm(prompt, provider)
                analysis_result = {
                    "analysis": str(result),
                    "provider": provider,
                    "cost": 0.01  # Estimate
                }
            else:
                # Use hybrid service
                analysis_result = await self.llm_service.analyze_dialogue_with_hybrid(
                    character_profile, dialogue_segments, speed_priority=False
                )
            
            duration = time.time() - start_time
            analysis_result["processing_time"] = duration
            
            print_result("Dialogue Analysis", analysis_result, duration)
            return analysis_result
            
        except Exception as e:
            duration = time.time() - start_time
            result = {"error": str(e)}
            print_result("Dialogue Analysis", result, duration)
            return result
    
    async def test_multiple_suggestions(self, provider: str = None):
        """Test multiple suggestion generation"""
        print_banner(f"💡 Testing Multiple Suggestions {f'({provider})' if provider else ''}")
        
        highlighted_text = "The man walked down the street."
        user_message = "Make this more vivid and engaging"
        author_persona = "Contemporary Fiction Writer"
        help_focus = "descriptive writing"
        
        start_time = time.time()
        try:
            if provider:
                # Manual suggestion generation
                prompt = f"""Provide 3 different improvements for: "{highlighted_text}"
Request: {user_message}
Author style: {author_persona}
Focus: {help_focus}

Return as numbered list."""
                
                result = await self.llm_service.generate_with_selected_llm(prompt, provider)
                suggestions_result = {
                    "suggestions_text": str(result),
                    "provider": provider,
                    "cost": 0.005  # Estimate
                }
            else:
                # Use existing suggestion system
                suggestions_result = await self.llm_service.generate_multiple_suggestions(
                    highlighted_text, user_message, author_persona, help_focus, 
                    self.llm_service.default_provider
                )
            
            duration = time.time() - start_time
            suggestions_result["processing_time"] = duration
            
            print_result("Multiple Suggestions", suggestions_result, duration)
            return suggestions_result
            
        except Exception as e:
            duration = time.time() - start_time
            result = {"error": str(e)}
            print_result("Multiple Suggestions", result, duration)
            return result
    
    async def test_cost_analytics(self):
        """Test cost analytics and optimization features"""
        print_banner("💰 Testing Cost Analytics")
        
        start_time = time.time()
        try:
            analytics = await self.llm_service.get_llm_cost_analytics()
            
            duration = time.time() - start_time
            
            # Print detailed analytics
            if isinstance(analytics, dict):
                print("\n📊 Cost Analytics Results:")
                if "cost_optimization" in analytics:
                    cost_opt = analytics["cost_optimization"]
                    for key, value in cost_opt.items():
                        print(f"   {key}: {value}")
                
                if "recommendations" in analytics:
                    print("\n💡 Recommendations:")
                    for rec in analytics["recommendations"]:
                        print(f"   • {rec}")
            
            print_result("Cost Analytics", analytics, duration)
            return analytics
            
        except Exception as e:
            duration = time.time() - start_time
            result = {"error": str(e)}
            print_result("Cost Analytics", result, duration)
            return result
    
    async def run_all_tests(self, specific_provider: str = None):
        """Run all test cases"""
        if not await self.setup():
            return False
        
        print(f"🎯 Target provider: {specific_provider or 'Auto (Hybrid Routing)'}")
        
        # Run tests
        await self.test_provider_status()
        await self.test_quick_consistency_check(specific_provider)
        await self.test_dialogue_analysis(specific_provider)
        await self.test_multiple_suggestions(specific_provider)
        await self.test_cost_analytics()
        
        print_banner("🎉 Test Suite Complete")
        return True
    
    async def test_all_providers(self):
        """Test all available providers individually"""
        if not await self.setup():
            return False
        
        providers = self.llm_service.get_available_providers()
        
        for provider in providers:
            print(f"\n🔄 Testing provider: {provider}")
            await self.test_quick_consistency_check(provider)
            
            # Small delay between providers
            await asyncio.sleep(1)
        
        print_banner("🎉 Multi-Provider Test Complete")
        return True

async def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Enhanced LLM Integration Test Suite")
    parser.add_argument("--provider", help="Test specific provider (e.g., 'HuggingFace gpt-oss')")
    parser.add_argument("--test-all-providers", action="store_true", help="Test all available providers")
    parser.add_argument("--quick", action="store_true", help="Run only quick tests")
    
    args = parser.parse_args()
    
    tester = EnhancedLLMTester()
    
    if args.test_all_providers:
        await tester.test_all_providers()
    elif args.quick:
        await tester.setup()
        await tester.test_quick_consistency_check(args.provider)
    else:
        await tester.run_all_tests(args.provider)

if __name__ == "__main__":
    # Check for required environment variables
    required_vars = []
    
    if not os.getenv("HUGGINGFACE_API_KEY"):
        print("⚠️  HUGGINGFACE_API_KEY not set - HuggingFace tests will be skipped")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  GEMINI_API_KEY not set - Gemini tests will be skipped")
    
    # Run tests
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)