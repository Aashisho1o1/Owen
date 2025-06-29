#!/usr/bin/env python3
"""
Test JSON parsing with actual Gemini response
"""

import json
import re

# This is the actual response from Gemini (from our debug output)
gemini_response = '''```json
{
    "entities": [
        {
            "text": "Sarah",
            "type": "CHARACTER",
            "start_pos": 0,
            "end_pos": 5,
            "confidence": 0.99
        },
        {
            "text": "the old library",
            "type": "LOCATION",
            "start_pos": 17,
            "end_pos": 32,
            "confidence": 0.95
        },
        {
            "text": "Mr. Thompson",
            "type": "CHARACTER",
            "start_pos": 86,
            "end_pos": 99,
            "confidence": 0.98
        },
        {
            "text": "ancient mysteries",
            "type": "THEME",
            "start_pos": 129,
            "end_pos": 146,
            "confidence": 0.85
        },
        {
            "text": "the back corner",
            "type": "LOCATION",
            "start_pos": 168,
            "end_pos": 183,
            "confidence": 0.9
        },
        {
            "text": "secrets",
            "type": "THEME",
            "start_pos": 198,
            "end_pos": 205,
            "confidence": 0.75
        },
        {
            "text": "research project",
            "type": "EVENT",
            "start_pos": 221,
            "end_pos": 237,
            "confidence": 0.8
        }
    ],
    "relationships": [
        {
            "source": "Sarah",
            "target": "the old library",
            "relation_type": "LOCATED_IN",
            "confidence": 0.9,
            "context": "Sarah walked into the library"
        },
        {
            "source": "Sarah",
            "target": "Mr. Thompson",
            "relation_type": "INTERACTS_WITH",
            "confidence": 0.95,
            "context": "Sarah approached and spoke to Mr. Thompson"
        },
        {
            "source": "Sarah",
            "target": "research project",
            "relation_type": "PARTICIPATES_IN",
            "confidence": 0.85,
            "context": "Sarah felt excited about her research project"
        },
        {
            "source": "the old library",
            "target": "secrets",
            "relation_type": "REPRESENTS",
            "confidence": 0.8,
            "context": "The library held many secrets."
        },
         {
            "source": "Sarah",
            "target": "ancient mysteries",
            "relation_type": "PARTICIPATES_IN",
            "confidence": 0.75,
            "context": "Sarah looking for books about ancient mysteries."
        }
    ]
}
```'''

def test_json_parsing():
    print("🔧 Testing JSON parsing methods...")
    
    # Method 1: Direct parsing
    try:
        data = json.loads(gemini_response)
        print("✅ Method 1 (Direct): SUCCESS")
        print(f"  Entities: {len(data.get('entities', []))}")
        print(f"  Relationships: {len(data.get('relationships', []))}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Method 1 (Direct): FAILED - {e}")
    
    # Method 2: Extract from markdown code blocks
    try:
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', gemini_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            print(f"🔧 Method 2: Found JSON block, length: {len(json_str)}")
            print(f"🔧 First 100 chars: {json_str[:100]}")
            
            data = json.loads(json_str)
            print("✅ Method 2 (Code Block): SUCCESS")
            print(f"  Entities: {len(data.get('entities', []))}")
            print(f"  Relationships: {len(data.get('relationships', []))}")
            
            # Test entity creation
            print("\n📋 Sample entities:")
            for entity in data.get('entities', [])[:3]:
                print(f"  - {entity['text']} ({entity['type']}) - confidence: {entity['confidence']}")
            
            print("\n🔗 Sample relationships:")
            for rel in data.get('relationships', [])[:3]:
                print(f"  - {rel['source']} -> {rel['target']} ({rel['relation_type']}) - confidence: {rel['confidence']}")
            
            return
        else:
            print("❌ Method 2: No code block found")
    except json.JSONDecodeError as e:
        print(f"❌ Method 2 (Code Block): FAILED - {e}")
    
    # Method 3: Extract any JSON-like structure
    try:
        json_match = re.search(r'\{.*\}', gemini_response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            print(f"🔧 Method 3: Found JSON-like structure, length: {len(json_str)}")
            
            data = json.loads(json_str)
            print("✅ Method 3 (JSON-like): SUCCESS")
            print(f"  Entities: {len(data.get('entities', []))}")
            print(f"  Relationships: {len(data.get('relationships', []))}")
            return
        else:
            print("❌ Method 3: No JSON structure found")
    except json.JSONDecodeError as e:
        print(f"❌ Method 3 (JSON-like): FAILED - {e}")
    
    print("❌ All methods failed!")

if __name__ == "__main__":
    test_json_parsing() 