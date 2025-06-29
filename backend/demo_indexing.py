"""
Demo script for the codebase indexing system
Shows how to use the indexing features for a writing project
"""

import asyncio
from services.indexing import HybridIndexer

async def demo_indexing():
    """
    Demonstrates the key features of the indexing system
    """
    
    # Initialize the indexer
    indexer = HybridIndexer(persist_dir="./demo_indexing_data")
    
    print("🚀 Writing Assistant Indexing Demo")
    print("=" * 50)
    
    # Sample narrative text (chapters from a story)
    chapter_1 = """
    Sarah stood at the edge of the cliff, watching the storm clouds gather over the ancient city of Eldoria. 
    She had traveled for three days to reach this point, following the cryptic map her grandmother had left her.
    
    "The answers you seek lie within the Temple of Whispers," the old woman had said on her deathbed. 
    Sarah clutched the worn leather pouch containing the mysterious artifact - a crystal that glowed with an inner light.
    
    As she descended the narrow path toward the city, she noticed a figure following her. It was Marcus, 
    the treasure hunter she had met in the tavern. He claimed to be searching for his lost brother, 
    but Sarah suspected his motives were less noble.
    
    The city gates loomed before her, carved with symbols she couldn't decipher. This was it - the beginning 
    of her quest to uncover the truth about her family's dark secret.
    """
    
    chapter_2 = """
    Inside the city walls, Sarah found herself in a bustling marketplace. The locals eyed her suspiciously, 
    whispering in a dialect she barely understood. She made her way to the Inn of the Silver Moon, 
    where she hoped to find information about the Temple of Whispers.
    
    Marcus appeared at her table uninvited. "You're looking for the temple," he said. It wasn't a question.
    Sarah's hand instinctively moved to the pouch at her side. "What's it to you?"
    
    "I know the way," Marcus replied, his scarred face revealing nothing. "But the path is dangerous. 
    You'll need a guide." He paused, then added, "My brother disappeared searching for that same temple."
    
    Sarah studied him carefully. Trust was a luxury she couldn't afford, but neither could she navigate 
    this foreign city alone. The crystal in her pouch pulsed warmly, as if responding to her dilemma.
    
    "Fine," she said finally. "But if you betray me, you'll regret it."
    Marcus smiled grimly. "Likewise."
    """
    
    chapter_3 = """
    The Temple of Whispers stood at the heart of the city, its entrance guarded by stone sentinels. 
    Sarah and Marcus had fought their way through the underground tunnels, barely escaping the creatures 
    that dwelt in the darkness.
    
    "Your brother was here," Sarah said, pointing to fresh scratches on the wall - a message in code.
    Marcus's face paled as he read it. "He's alive, but trapped inside."
    
    The crystal in Sarah's pouch began to glow brighter, resonating with the temple's ancient magic. 
    She realized with growing dread that her grandmother's artifact was a key - but to what?
    
    As they entered the temple, the massive doors sealed behind them. In the distance, they could hear 
    chanting in the same ancient dialect. Sarah's quest for answers had led them into a trap, and the 
    dark secret of her family was about to be revealed.
    
    Marcus grabbed her arm. "Whatever happens in there, we face it together."
    Sarah nodded, surprised by the trust that had grown between them. The unlikely allies ventured deeper 
    into the temple, where destiny awaited.
    """
    
    print("\n📚 Step 1: Indexing Documents")
    print("-" * 30)
    
    # Index the chapters
    result1 = await indexer.index_document(
        doc_id="chapter_1",
        text=chapter_1,
        metadata={
            "title": "Chapter 1: The Journey Begins",
            "type": "chapter",
            "setting": "Cliff overlooking Eldoria"
        }
    )
    print(f"✅ Chapter 1 indexed: {result1['entities_extracted']} entities, {result1['relationships_found']} relationships")
    
    result2 = await indexer.index_document(
        doc_id="chapter_2",
        text=chapter_2,
        metadata={
            "title": "Chapter 2: An Unlikely Alliance",
            "type": "chapter",
            "setting": "Inside Eldoria"
        }
    )
    print(f"✅ Chapter 2 indexed: {result2['entities_extracted']} entities, {result2['relationships_found']} relationships")
    
    result3 = await indexer.index_document(
        doc_id="chapter_3",
        text=chapter_3,
        metadata={
            "title": "Chapter 3: The Temple's Secret",
            "type": "chapter",
            "setting": "Temple of Whispers"
        }
    )
    print(f"✅ Chapter 3 indexed: {result3['entities_extracted']} entities, {result3['relationships_found']} relationships")
    
    # Build unified graph
    print("\n🔗 Building narrative graph...")
    await indexer.index_folder([
        ("chapter_1", chapter_1, {"title": "Chapter 1"}),
        ("chapter_2", chapter_2, {"title": "Chapter 2"}),
        ("chapter_3", chapter_3, {"title": "Chapter 3"})
    ])
    print(f"✅ Graph built with {indexer.graph_builder.graph.number_of_nodes()} nodes and {indexer.graph_builder.graph.number_of_edges()} edges")
    
    print("\n💡 Step 2: Contextual Feedback")
    print("-" * 30)
    
    # Get contextual feedback for a highlighted passage
    feedback = await indexer.get_contextual_feedback(
        highlighted_text="The crystal in Sarah's pouch began to glow brighter",
        doc_id="chapter_3"
    )
    
    print("Highlighted text:", feedback['highlighted_text'])
    print("\nEntities mentioned:")
    for entity in feedback['entities_mentioned']:
        print(f"  - {entity['text']} ({entity['type']})")
    
    print("\nNarrative paths:")
    for path in feedback['narrative_paths']:
        print(f"  - {path['narrative']} (score: {path['score']:.2f})")
    
    print("\nSuggestions:")
    for suggestion in feedback['suggestions']:
        print(f"  - {suggestion}")
    
    print("\n🔍 Step 3: Consistency Checking")
    print("-" * 30)
    
    # Check consistency of a statement
    consistency = await indexer.check_consistency(
        statement="Sarah met Marcus in the temple",
        doc_id="chapter_3",
        check_type="all"
    )
    
    print(f"Statement: '{consistency['statement']}'")
    print(f"Consistent: {consistency['is_consistent']}")
    print(f"Recommendation: {consistency['recommendation']}")
    
    if consistency['conflicts']:
        print("\nConflicts found:")
        for conflict in consistency['conflicts']:
            print(f"  - {conflict['type']}: {conflict['conflict']}")
    
    if consistency['confirmations']:
        print("\nSupporting evidence:")
        for confirmation in consistency['confirmations']:
            print(f"  - {confirmation['narrative']} (confidence: {confirmation['confidence']:.2f})")
    
    print("\n✍️ Step 4: Writing Suggestions")
    print("-" * 30)
    
    # Get writing suggestions
    suggestions = await indexer.get_writing_suggestions(
        context="Sarah and Marcus stood before the temple doors, unsure of what awaited them inside.",
        suggestion_type="all"
    )
    
    print("Context:", suggestions['context'])
    print("\nSuggestions:")
    for i, suggestion in enumerate(suggestions['suggestions'], 1):
        print(f"{i}. [{suggestion['type']}] {suggestion['suggestion']}")
        print(f"   Based on: {suggestion['based_on']}")
    
    print("\n🔎 Step 5: Advanced Search")
    print("-" * 30)
    
    # Perform hybrid search
    search_results = indexer.search(
        query="crystal artifact temple",
        search_type="hybrid"
    )
    
    print(f"Search query: 'crystal artifact temple'")
    print(f"\nTop results:")
    for i, result in enumerate(search_results[:3], 1):
        print(f"\n{i}. Type: {result['type']}")
        print(f"   Content: {result['content'][:150]}...")
        print(f"   Score: {result['score']:.3f}")
    
    print("\n👥 Step 6: Character Analysis")
    print("-" * 30)
    
    # Get character arc
    sarah_arc = indexer.graph_builder.get_character_arc("Sarah")
    print(f"Sarah's character arc: {len(sarah_arc)} key events")
    for event in sarah_arc[:5]:  # Show first 5 events
        print(f"  - {event['source']} {event['type']} {event['target']}")
    
    # Get character-specific paths
    marcus_paths = indexer.path_retriever.get_character_context_paths("Marcus", "relationships")
    print(f"\nMarcus's relationships:")
    for path in marcus_paths[:3]:
        print(f"  - {path['narrative']}")
    
    print("\n📊 Step 7: Document Statistics")
    print("-" * 30)
    
    # Get stats for a document
    stats = indexer.get_document_stats("chapter_1")
    print(f"Chapter 1 Statistics:")
    print(f"  - Chunks: {stats['chunks']}")
    print(f"  - Total entities: {stats['total_entities']}")
    print(f"  - Entity breakdown:")
    for entity_type, count in stats['entities'].items():
        print(f"    • {entity_type}: {count}")
    
    print("\n🎯 Demo Complete!")
    print("=" * 50)
    print("\nThis demo showed:")
    print("✅ Document indexing with entity extraction")
    print("✅ Contextual feedback for highlighted text")
    print("✅ Consistency checking across documents")
    print("✅ AI-powered writing suggestions")
    print("✅ Hybrid search (vector + graph)")
    print("✅ Character arc analysis")
    print("✅ Document statistics")
    
    print("\n💡 Next steps:")
    print("1. Index your own writing project")
    print("2. Use contextual feedback while writing")
    print("3. Check consistency as you develop your story")
    print("4. Let AI suggest plot developments")
    print("5. Track character arcs across chapters")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_indexing())
