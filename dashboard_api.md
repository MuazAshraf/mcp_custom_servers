## 🎯 **Global Experiences API**

### **Base Endpoint**: `/api/v1/experiences/`
**ViewSet**: `ExperienceViewSet` in `experiences/views.py`

### **List Experiences**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/v1/experiences/
```

**Response Example**:
```json
{
  "count": 3,
  "results": [
    {
      "id": "uuid-here",
      "name": "Document Analysis Assistant",
      "description": "AI assistant specialized in document analysis",
      "instructions": "You are an expert document analyzer...",
      "default_model": {
        "id": "uuid",
        "name": "GPT-4o Mini", 
        "provider": "openai"
      },
      "is_global": true,
      "is_default": false,
      "organization": null,
      "created_by": 1,
      "created_at": "2025-09-03T10:00:00Z",
      "version": "1.0.0",
      "brains": [],
      "prompts_count": 3,
      "tools_count": 2
    }
  ]
}
```

### **Create Experience**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Experience",
       "description": "Test experience via API",
       "instructions": "You are a helpful assistant for testing.",
       "is_global": false
     }' \
     http://localhost:8000/api/v1/experiences/
```

### **Create Global Experience** (Superuser Only)
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Global Test Experience",
       "description": "Global experience available to all orgs",
       "instructions": "You are a global assistant.",
       "is_global": true
     }' \
     http://localhost:8000/api/v1/experiences/create_global/
```

### **Get Experience Details**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/v1/experiences/{experience_id}/
```

### **Update Experience**
```bash
curl -X PATCH \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"description": "Updated description"}' \
     http://localhost:8000/api/v1/experiences/{experience_id}/
```

### **Experience Actions**
- **Add Prompt**: `POST /api/v1/experiences/{id}/add_prompt/`
- **Remove Prompt**: `DELETE /api/v1/experiences/{id}/remove_prompt/`
- **Add Tool**: `POST /api/v1/experiences/{id}/add_tool/`
- **Remove Tool**: `DELETE /api/v1/experiences/{id}/remove_tool/`
- **Add Brain**: `POST /api/v1/experiences/{id}/add_brain/`
- **Remove Brain**: `DELETE /api/v1/experiences/{id}/remove_brain/`

---

## 📝 **Global Prompts API**

### **Base Endpoint**: `/api/v1/prompts/`
**ViewSet**: `PromptViewSet` in `experiences/views.py`

### **List Prompts**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/v1/prompts/
```

**Response Example**:
```json
{
  "count": 5,
  "results": [
    {
      "id": "uuid-here",
      "name": "System Introduction",
      "description": "Standard system introduction prompt",
      "content": "You are an AI assistant specialized in exit planning...",
      "prompt_type": "system",
      "is_global": true,
      "organization": null,
      "created_by": 1,
      "created_at": "2025-09-03T10:00:00Z",
      "version": "1.0.0"
    }
  ]
}
```

### **Create Prompt**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Prompt",
       "description": "Test prompt via API",
       "content": "You are a helpful assistant for testing prompts.",
       "prompt_type": "system",
       "is_global": false
     }' \
     http://localhost:8000/api/v1/prompts/
```

### **Create Global Prompt** (Superuser Only)
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Global System Prompt",
       "description": "Global prompt available to all organizations",
       "content": "You are a global AI assistant.",
       "prompt_type": "system",
       "is_global": true
     }' \
     http://localhost:8000/api/v1/prompts/create_global/
```

### **Prompt Types**:
- `system` - System-level instructions
- `human` - Human user prompts
- `assistant` - Assistant response templates

---

## 🛠️ **Global Tools API**

### **Base Endpoint**: `/api/v1/tools/`
**ViewSet**: `ToolViewSet` in `experiences/views.py`

### **List Tools**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/v1/tools/
```

**Response Example**:
```json
{
  "count": 2,
  "results": [
    {
      "id": "uuid-here",
      "name": "Document Summarizer",
      "description": "Tool for summarizing documents",
      "function_code": "def summarize_document(content): ...",
      "schema": {
        "type": "object",
        "properties": {
          "content": {"type": "string"},
          "max_length": {"type": "integer", "default": 500}
        },
        "required": ["content"]
      },
      "is_global": true,
      "organization": null,
      "created_by": 1,
      "created_at": "2025-09-03T10:00:00Z",
      "last_tested": "2025-09-03T11:00:00Z",
      "test_result": "Test passed successfully",
      "version": "1.0.0"
    }
  ]
}
```

### **Create Tool**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Tool",
       "description": "Test tool via API",
       "function_code": "def test_function(input): return {\"result\": input}",
       "schema": {
         "type": "object",
         "properties": {
           "input": {"type": "string"}
         }
       },
       "is_global": false
     }' \
     http://localhost:8000/api/v1/tools/
```

### **Test Tool**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"test_input": "sample input"}' \
     http://localhost:8000/api/v1/tools/{tool_id}/test/
```

---

## 🤖 **AI Models API**

### **Base Endpoint**: `/api/v1/ai-models/`
**ViewSet**: `AIModelViewSet` in `accounts/views.py`
**Permission**: Superuser only

### **List AI Models**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/v1/ai-models/
```

**Response Example**:
```json
{
  "count": 3,
  "results": [
    {
      "id": "uuid-here",
      "name": "GPT-4o Mini",
      "provider": "openai",
      "model_id": "gpt-4o-mini",
      "description": "Fast and efficient model for most tasks",
      "is_active": true,
      "is_default": true,
      "max_tokens": 128000,
      "cost_per_1k_tokens": "0.000150",
      "created_by": 1,
      "created_at": "2025-09-03T10:00:00Z",
      "updated_at": "2025-09-03T10:00:00Z"
    },
    {
      "id": "uuid-2",
      "name": "GPT-4o",
      "provider": "openai", 
      "model_id": "gpt-4o",
      "description": "Most capable model for complex tasks",
      "is_active": true,
      "is_default": false,
      "max_tokens": 128000,
      "cost_per_1k_tokens": "0.003000",
      "created_by": 1,
      "created_at": "2025-09-03T10:00:00Z"
    }
  ]
}
```

### **Create AI Model**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Claude 3.5 Sonnet",
       "provider": "claude",
       "model_id": "claude-3-5-sonnet-20241022",
       "description": "Anthropic Claude model for complex reasoning",
       "is_active": true,
       "max_tokens": 200000,
       "cost_per_1k_tokens": "0.003000"
     }' \
     http://localhost:8000/api/v1/ai-models/
```

### **Get Default Model**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/v1/ai-models/default/
```

### **Set Model as Default**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/v1/ai-models/{model_id}/set_default/
```

### **Get Available Provider Models**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"provider": "openai"}' \
     http://localhost:8000/api/v1/ai-models/fetch_provider_models/
```

### **Check if Model Can Be Deleted**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/v1/ai-models/{model_id}/can_delete/
```

---

## 🌐 **Global System Integration**

### **Experience-Prompt-Tool Relationships**

#### **Add Prompt to Experience**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt_id": "prompt-uuid",
       "order": 1,
       "is_hidden": false
     }' \
     http://localhost:8000/api/v1/experiences/{exp_id}/add_prompt/
```

#### **Add Tool to Experience**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"tool_id": "tool-uuid"}' \
     http://localhost:8000/api/v1/experiences/{exp_id}/add_tool/
```

### **Organization vs Global Resources**

#### **Filter by Organization**
```bash
# Get organization-specific experiences
curl -H "Authorization: Token YOUR_TOKEN" \
     "http://localhost:8000/api/v1/experiences/?organization={org_uuid}"

# Get global experiences only  
curl -H "Authorization: Token YOUR_TOKEN" \
     "http://localhost:8000/api/v1/experiences/?is_global=true"
```

**Base URL**: `http://localhost:8000`  
**PRD Prompts API**: `/api/v1/prd/prompts/`  
**PRD Types API**: `/api/v1/prd/types/`  
**Authentication**: `Authorization: Token YOUR_PERMANENT_TOKEN`

---

## 📝 **PRD Prompts Management**

### **Core Concept**
PRD Prompts are **system-level templates** that instruct the AI how to generate different types of content:
- **CEO Analysis Prompts** → How to analyze business documents like a CEO
- **PRD Generation Prompts** → How to create technical/business PRDs  
- **Experience Generation Prompts** → How to create AI assistant experiences

### **Base Endpoint**: `/api/v1/prd/prompts/`
**ViewSet**: `PrdPromptViewSet` in `prd_generator/views.py`

---

## 📋 **PRD Prompts CRUD Operations**

### **1. List All PRD Prompts**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/v1/prd/prompts/
```

**Response Example**:
```json
{
  "count": 8,
  "results": [
    {
      "id": "uuid-here",
      "name": "CEO Strategic Analysis Prompt",
      "description": "Generates executive-level strategic analysis of business documents",
      "content": "You are a seasoned CEO with 20+ years of experience in technology companies. Analyze the provided business document and generate a comprehensive strategic analysis...",
      "tag": ["ceo", "analysis", "strategic", "executive"],
      "created_at": "2025-09-03T10:00:00Z"
    },
    {
      "id": "uuid-2",
      "name": "Technical PRD Generator Prompt", 
      "description": "Creates detailed technical product requirements documents",
      "content": "You are a senior technical product manager. Create a comprehensive technical PRD from the provided analysis that includes: API specifications, system architecture, database schema...",
      "tag": ["prd", "technical", "engineering", "api"],
      "created_at": "2025-09-03T09:00:00Z"
    },
    {
      "id": "uuid-3",
      "name": "Experience Generator Prompt",
      "description": "Creates AI assistant experiences from PRD content", 
      "content": "You are an AI experience designer. Based on the provided PRD and business analysis, create specialized AI assistant experiences that would help users achieve the goals outlined...",
      "tag": ["experience", "assistant", "generation", "ai"],
      "created_at": "2025-09-03T08:00:00Z"
    }
  ]
}
```

### **2. Create PRD Prompt**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Insurance CEO Analysis Prompt",
       "description": "CEO analysis specialized for insurance industry",
       "content": "You are a CEO with deep experience in the insurance industry, specifically in agent management and commission systems. Analyze this business document focusing on: 1) Insurance market dynamics and AEP cycles 2) Agent retention and commission structures 3) Regulatory compliance (state insurance laws) 4) Technology integration with existing insurance platforms 5) Competitive positioning vs legacy systems like Benge. Provide strategic recommendations with specific focus on commission automation, AEP management, and agent productivity tools.",
       "tag": ["ceo"] // or ["prd"] or ["experience"]
     }' \
     http://localhost:8000/api/v1/prd/prompts/
```

### **3. Update PRD Prompt**
```bash
curl -X PATCH \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Updated prompt content with more specific instructions...",
       "tag": ["ceo"] // or ["prd"] or ["experience"]
     }' \
     http://localhost:8000/api/v1/prd/prompts/{prompt_id}/
```

### **4. Delete PRD Prompt**
```bash
curl -X DELETE \
     -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/v1/prd/prompts/{prompt_id}/
```

### **5. Search PRD Prompts by Tag**
```bash
# Get all CEO analysis prompts
curl -H "Authorization: Token YOUR_TOKEN" \
     "http://localhost:8000/api/v1/prd/prompts/search_by_tag/?tag=ceo"

# Get all technical PRD prompts  
curl -H "Authorization: Token YOUR_TOKEN" \
     "http://localhost:8000/api/v1/prd/prompts/search_by_tag/?tag=technical"

# Get all experience generation prompts
curl -H "Authorization: Token YOUR_TOKEN" \
     "http://localhost:8000/api/v1/prd/prompts/search_by_tag/?tag=experience"
```

---

## 🏭 **PRD Types Management**

### **Core Concept**
PRD Types define **output templates** that are linked to specific PRD Prompts, controlling what type of document gets generated.

### **Base Endpoint**: `/api/v1/prd/types/`
**ViewSet**: `PrdTypeViewSet` in `prd_generator/views.py`

### **1. List All PRD Types**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/v1/prd/types/
```

**Response Example**:
```json
{
  "count": 4,
  "results": [
    {
      "id": "uuid-here",
      "name": "Technical PRD",
      "description": "Comprehensive technical product requirements document with API specs and system architecture",
      "prompt": {
        "id": "prompt-uuid",
        "name": "Technical PRD Generator Prompt",
        "content": "Create a technical PRD that includes..."
      },
      "created_at": "2025-09-03T10:00:00Z"
    },
    {
      "id": "uuid-2",
      "name": "Business PRD",
      "description": "Business-focused requirements document emphasizing stakeholder value",
      "prompt": {
        "id": "prompt-uuid-2", 
        "name": "Business PRD Generator Prompt",
        "content": "Create a business PRD that focuses on..."
      },
      "created_at": "2025-09-03T09:00:00Z"
    },
    {
      "id": "uuid-3",
      "name": "Insurance Commission PRD",
      "description": "Specialized PRD for insurance commission management systems",
      "prompt": {
        "id": "prompt-uuid-3",
        "name": "Insurance PRD Generator Prompt",
        "content": "Create an insurance-focused PRD that addresses..."
      },
      "created_at": "2025-09-03T08:00:00Z"
    }
  ]
}
```

### **2. Create PRD Type**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "AEP Management PRD",
       "description": "PRD template for Annual Enrollment Period management systems",
       "prompt": "prompt-uuid-for-aep"
     }' \
     http://localhost:8000/api/v1/prd/types/
```

### **3. Assign Prompt to PRD Type**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"prompt_id": "prompt-uuid"}' \
     http://localhost:8000/api/v1/prd/types/{type_id}/assign_prompt/
```

### **4. Remove Prompt from PRD Type**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/v1/prd/types/{type_id}/remove_prompt/
```

---

**Tag-Based Prompt Organization**

### **Search by Tag Category**
```bash
# CEO Analysis Prompts
curl -H "Authorization: Token YOUR_TOKEN" \
     "http://localhost:8000/api/v1/prd/prompts/search_by_tag/?tag=ceo"

# Technical PRD Prompts
curl -H "Authorization: Token YOUR_TOKEN" \
     "http://localhost:8000/api/v1/prd/prompts/search_by_tag/?tag=technical"

# Business PRD Prompts
curl -H "Authorization: Token YOUR_TOKEN" \
     "http://localhost:8000/api/v1/prd/prompts/search_by_tag/?tag=business"

# Experience Generation Prompts
curl -H "Authorization: Token YOUR_TOKEN" \
     "http://localhost:8000/api/v1/prd/prompts/search_by_tag/?tag=experience"

# Insurance-Specific Prompts
curl -H "Authorization: Token YOUR_TOKEN" \
     "http://localhost:8000/api/v1/prd/prompts/search_by_tag/?tag=insurance"
```

## 🎛️ **PRD Types & Prompt Association**

### **Create PRD Type with Associated Prompt**
```bash
# 1. First create the prompt
PROMPT_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Insurance Business PRD Prompt",
    "description": "Business PRD generator for insurance industry",
    "content": "Create a business PRD for insurance technology...",
    "tag": ["prd", "business", "insurance"]
  }' \
  http://localhost:8000/api/v1/prd/prompts/)

PROMPT_ID=$(echo $PROMPT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

# 2. Create PRD Type and link the prompt
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Insurance Business PRD\",
    \"description\": \"Business requirements for insurance technology solutions\",
    \"prompt\": \"$PROMPT_ID\"
  }" \
  http://localhost:8000/api/v1/prd/types/
```

### **Get PRD Types for a Prompt**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/v1/prd/prompts/{prompt_id}/associated_types/
``` 