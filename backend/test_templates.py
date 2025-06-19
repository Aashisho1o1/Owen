from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime

app = FastAPI(title="Template Test Server")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates store
templates_store = [
    {
        "id": "academic-essay",
        "title": "Academic Essay",
        "description": "Professional academic essay template with proper structure",
        "content": """# [Essay Title]

**Author:** [Your Name]  
**Course:** [Course Name]  
**Date:** [Date]  
**Word Count Target:** 1,500-2,000 words

## Abstract
Provide a brief summary of your essay's main argument and key points (150-250 words).

## Introduction
Begin with a compelling hook that draws readers into your topic. Provide necessary background information and context. Clearly state your thesis statement - the main argument you will defend throughout the essay.

### Thesis Statement
*"[Insert your clear, specific, and arguable thesis statement here.]*"

## Body Paragraph 1: [Main Point 1]
**Topic Sentence:** Begin with a clear statement that introduces your first main point.

**Evidence:** Present specific evidence, examples, data, or quotes from credible sources to support your point.

**Analysis:** Explain how this evidence supports your thesis. Connect the dots for your reader.

**Transition:** Link to your next point smoothly.

## Body Paragraph 2: [Main Point 2]
**Topic Sentence:** [Second supporting argument]

**Evidence:** [Supporting evidence and sources]

**Analysis:** [Explanation of how evidence supports thesis]

**Transition:** [Connection to next point]

## Conclusion
Restate your thesis in new words. Summarize your main supporting points. Discuss the broader implications of your argument. End with a powerful closing thought that leaves a lasting impression.

## References
*Use appropriate citation style (APA, MLA, Chicago, etc.)*

1. [Source 1]
2. [Source 2]
3. [Source 3]

---

## Writing Checklist
- [ ] Clear thesis statement
- [ ] Strong topic sentences
- [ ] Sufficient evidence for each point
- [ ] Proper citations
- [ ] Smooth transitions
- [ ] Compelling introduction and conclusion
- [ ] Proofread for grammar and style"""
    },
    {
        "id": "creative-story",
        "title": "Creative Story",
        "description": "Structure for creative storytelling with character development",
        "content": """# [Story Title]

## Characters
### Protagonist
- **Name:** [Character Name]
- **Age:** [Age]
- **Appearance:** [Physical description]
- **Personality:** [Key traits and quirks]
- **Background:** [Relevant history]
- **Goal:** [What they want]
- **Conflict:** [What stands in their way]

### Supporting Characters
- **Character 2:** [Brief description]
- **Character 3:** [Brief description]

## Setting
- **Time:** [When does this take place?]
- **Place:** [Where does this happen?]
- **Atmosphere:** [What's the mood/feeling?]

## Plot Outline
### Opening
[Hook the reader immediately]

### Rising Action
[Build tension and develop characters]

### Climax
[The turning point]

### Falling Action
[Consequences of the climax]

### Resolution
[How everything concludes]

---

## Chapter 1
[Begin your story here...]

The morning sun cast long shadows across [setting details]. [Character name] [first action that reveals character].

[Continue with compelling opening scene...]

## Notes
- Show, don't tell
- Use sensory details
- Develop character voice
- Maintain consistent point of view
- Create tension in every scene"""
    }
]

class DocumentFromTemplateCreate(BaseModel):
    template_id: str = Field(..., description="Template ID to use")
    title: str = Field(..., min_length=1, max_length=200, description="Document title")
    folder_id: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Template Test Server", "status": "running"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "templates_count": len(templates_store)}

@app.get("/api/templates")
async def get_templates():
    return templates_store

@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    template = next((t for t in templates_store if t['id'] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@app.post("/api/documents/from-template")
async def create_document_from_template(doc_data: DocumentFromTemplateCreate):
    try:
        # Find the template
        template = next((t for t in templates_store if t['id'] == doc_data.template_id), None)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        doc_id = str(uuid.uuid4())
        content = template['content']
        
        # Mock document response
        document = {
            "id": doc_id,
            "title": doc_data.title,
            "content": content,
            "folder_id": doc_data.folder_id,
            "status": "draft",
            "tags": [],
            "word_count": len(content.split()),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "user_id": "test-user"
        }
        
        print(f"✅ Document created from template '{doc_data.template_id}': {document['title']}")
        return document
        
    except Exception as e:
        print(f"❌ Error creating document from template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document from template")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 