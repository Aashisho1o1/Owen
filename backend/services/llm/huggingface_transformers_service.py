"""
HuggingFace Transformers Direct Service

Uses HuggingFace transformers library directly for OpenAI gpt-oss models.
This approach provides better control, faster inference, and local caching.
"""

import json
import logging
import time
import torch
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import os
from threading import Lock

from transformers import (
    pipeline, 
    AutoTokenizer, 
    AutoModelForCausalLM,
    BitsAndBytesConfig
)

from .base_service import BaseLLMService, LLMError, log_api_error

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for gpt-oss model variants"""
    name: str
    model_id: str
    context_length: int
    memory_requirement_gb: int
    recommended_use: str
    load_in_8bit: bool = False
    load_in_4bit: bool = False

class HuggingFaceTransformersService(BaseLLMService):
    """
    Direct HuggingFace transformers service for OpenAI gpt-oss models
    Uses local model loading with GPU acceleration when available
    """
    
    # Available gpt-oss models
    MODELS = {
        "gpt-oss-20b": ModelConfig(
            name="gpt-oss-20b",
            model_id="openai/gpt-oss-20b",
            context_length=128000,
            memory_requirement_gb=40,  # Full precision
            recommended_use="Fast dialogue analysis, real-time feedback",
            load_in_8bit=True  # Enable quantization for efficiency
        ),
        "gpt-oss-120b": ModelConfig(
            name="gpt-oss-120b", 
            model_id="openai/gpt-oss-120b",
            context_length=128000,
            memory_requirement_gb=240,  # Full precision
            recommended_use="Deep reasoning, complex character analysis",
            load_in_4bit=True  # Aggressive quantization for large model
        )
    }
    
    def __init__(self, 
                 default_model: str = "gpt-oss-20b",
                 cache_dir: Optional[str] = None,
                 device: str = "auto"):
        # Initialize with HuggingFace token
        super().__init__("HUGGINGFACE_API_KEY")
        
        self.default_model = default_model
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/huggingface")
        self.device = device
        
        # Model caching
        self._loaded_models = {}
        self._loaded_tokenizers = {}
        self._model_lock = Lock()
        
        # Device detection
        self.device_info = self._detect_device()
        
        # Usage statistics
        self.usage_stats = {
            "models_loaded": 0,
            "inference_calls": 0,
            "total_tokens_generated": 0,
            "cache_hits": 0
        }
        
        logger.info(f"🤗 HuggingFace Transformers service initialized")
        logger.info(f"🖥️  Device: {self.device_info}")
        logger.info(f"💾 Cache directory: {self.cache_dir}")
    
    def _detect_device(self) -> str:
        """Detect optimal device for model loading"""
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
            
            device_info = f"CUDA GPU: {gpu_name} ({vram_gb:.1f}GB VRAM, {gpu_count} GPUs)"
            logger.info(f"🎮 GPU detected: {device_info}")
            return "cuda"
        elif torch.backends.mps.is_available():
            device_info = "Apple Metal Performance Shaders (MPS)"
            logger.info(f"🍎 MPS detected: {device_info}")
            return "mps"
        else:
            device_info = "CPU (slower inference, but works everywhere)"
            logger.info(f"🖥️  CPU mode: {device_info}")
            return "cpu"
    
    def _get_quantization_config(self, model_config: ModelConfig):
        """Get optimal quantization configuration for model"""
        if not torch.cuda.is_available():
            return None
            
        if model_config.load_in_4bit:
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True
            )
        elif model_config.load_in_8bit:
            return BitsAndBytesConfig(
                load_in_8bit=True
            )
        return None
    
    def _load_model_and_tokenizer(self, model_name: str):
        """Load model and tokenizer with caching"""
        model_config = self.MODELS.get(model_name)
        if not model_config:
            raise LLMError(f"Unknown model: {model_name}")
        
        with self._model_lock:
            # Check cache first
            cache_key = model_name
            if cache_key in self._loaded_models:
                self.usage_stats["cache_hits"] += 1
                return self._loaded_models[cache_key], self._loaded_tokenizers[cache_key]
            
            logger.info(f"🔄 Loading model: {model_config.model_id}")
            start_time = time.time()
            
            try:
                # Load tokenizer
                tokenizer = AutoTokenizer.from_pretrained(
                    model_config.model_id,
                    token=self.api_key,
                    cache_dir=self.cache_dir,
                    trust_remote_code=True
                )
                
                # Get quantization config
                quantization_config = self._get_quantization_config(model_config)
                
                # Load model with optimal settings
                model_kwargs = {
                    "token": self.api_key,
                    "cache_dir": self.cache_dir,
                    "trust_remote_code": True,
                    "torch_dtype": torch.float16 if self.device != "cpu" else torch.float32,
                    "device_map": "auto" if self.device == "cuda" else None
                }
                
                if quantization_config:
                    model_kwargs["quantization_config"] = quantization_config
                    logger.info(f"🗜️  Using quantization: {'4-bit' if model_config.load_in_4bit else '8-bit'}")
                
                model = AutoModelForCausalLM.from_pretrained(
                    model_config.model_id,
                    **model_kwargs
                )
                
                # Move to device if not using device_map
                if self.device != "cuda":
                    model = model.to(self.device)
                
                load_time = time.time() - start_time
                
                # Cache the loaded models
                self._loaded_models[cache_key] = model
                self._loaded_tokenizers[cache_key] = tokenizer
                self.usage_stats["models_loaded"] += 1
                
                # Get model size info
                param_count = sum(p.numel() for p in model.parameters())
                memory_usage = torch.cuda.memory_allocated() / 1024**3 if torch.cuda.is_available() else 0
                
                logger.info(f"✅ Model loaded successfully in {load_time:.2f}s")
                logger.info(f"📊 Parameters: {param_count:,} ({param_count/1e9:.1f}B)")
                if memory_usage > 0:
                    logger.info(f"💾 GPU Memory: {memory_usage:.2f}GB")
                
                return model, tokenizer
                
            except Exception as e:
                log_api_error("HuggingFace Transformers", e, f"loading {model_config.model_id}")
                raise LLMError(f"Failed to load model {model_name}: {str(e)}")
    
    async def generate_text(self, 
                          prompt: str,
                          model_name: Optional[str] = None,
                          max_new_tokens: int = 1000,
                          temperature: float = 0.7,
                          top_p: float = 0.9,
                          do_sample: bool = True,
                          **kwargs) -> str:
        """
        Generate text using direct transformers inference
        
        Args:
            prompt: Input text prompt
            model_name: Model to use ("gpt-oss-20b" or "gpt-oss-120b")
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter
            do_sample: Whether to use sampling vs greedy decoding
        """
        model_name = model_name or self.default_model
        
        start_time = time.time()
        self.usage_stats["inference_calls"] += 1
        
        try:
            # Load model and tokenizer
            model, tokenizer = self._load_model_and_tokenizer(model_name)
            
            # Prepare messages format
            messages = [{"role": "user", "content": prompt}]
            
            # Apply chat template
            inputs = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt"
            ).to(model.device)
            
            # Generate response
            generation_kwargs = {
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": do_sample,
                "pad_token_id": tokenizer.eos_token_id,
                "eos_token_id": tokenizer.eos_token_id,
                "use_cache": True
            }
            
            # Add any additional kwargs
            generation_kwargs.update(kwargs)
            
            with torch.no_grad():
                outputs = model.generate(**inputs, **generation_kwargs)
            
            # Decode only the generated tokens (exclude input)
            generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
            response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
            
            processing_time = time.time() - start_time
            self.usage_stats["total_tokens_generated"] += len(generated_tokens)
            
            logger.info(f"🤗 Generated {len(generated_tokens)} tokens in {processing_time:.2f}s using {model_name}")
            
            return response.strip()
            
        except Exception as e:
            log_api_error("HuggingFace Transformers", e, f"generation with {model_name}")
            raise LLMError(f"Text generation failed: {str(e)}")
    
    async def generate_with_pipeline(self,
                                   prompt: str,
                                   model_name: Optional[str] = None,
                                   **kwargs) -> str:
        """Alternative generation using HuggingFace pipeline (simpler but less control)"""
        model_name = model_name or self.default_model
        model_config = self.MODELS.get(model_name)
        
        if not model_config:
            raise LLMError(f"Unknown model: {model_name}")
        
        try:
            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=model_config.model_id,
                tokenizer=model_config.model_id,
                token=self.api_key,
                torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                cache_dir=self.cache_dir
            )
            
            # Format as messages
            messages = [{"role": "user", "content": prompt}]
            
            # Generate
            result = pipe(messages, max_new_tokens=kwargs.get("max_new_tokens", 1000), 
                         temperature=kwargs.get("temperature", 0.7), **kwargs)
            
            return result[0]["generated_text"][-1]["content"]
            
        except Exception as e:
            log_api_error("HuggingFace Pipeline", e, f"generation with {model_name}")
            raise LLMError(f"Pipeline generation failed: {str(e)}")
    
    async def generate_structured(self, 
                                prompt: str, 
                                schema: Dict[str, Any],
                                model_name: Optional[str] = None,
                                **kwargs) -> Dict[str, Any]:
        """Generate structured JSON response"""
        
        # Enhance prompt for JSON output
        json_prompt = f"""{prompt}

CRITICAL: You must respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Response format: Provide ONLY valid JSON, no additional text before or after.
"""
        
        response_text = await self.generate_text(
            json_prompt,
            model_name=model_name,
            temperature=0.3,  # Lower temperature for structured output
            do_sample=True,
            **kwargs
        )
        
        try:
            # Clean and parse JSON response
            cleaned_response = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            return json.loads(cleaned_response.strip())
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from transformers: {e}")
            logger.error(f"Raw response: {response_text[:500]}...")
            raise LLMError(f"Invalid JSON response: {str(e)}")
    
    async def quick_consistency_check(self, 
                                    dialogue: str,
                                    character_context: str) -> Dict[str, Any]:
        """
        Ultra-fast consistency check using smaller model
        """
        prompt = f"""Character Context: {character_context}
Dialogue: "{dialogue}"

Quick consistency analysis:
- Is this dialogue consistent with the character? (Yes/No)
- Confidence level: 1-10
- Brief explanation (one sentence)

Keep response under 50 words."""

        start_time = time.time()
        
        try:
            response = await self.generate_text(
                prompt=prompt,
                model_name="gpt-oss-20b",  # Use faster model
                max_new_tokens=100,
                temperature=0.3
            )
            
            processing_time = time.time() - start_time
            
            # Parse response
            is_consistent = "yes" in response.lower()
            
            return {
                "is_consistent": is_consistent,
                "explanation": response,
                "processing_time": processing_time,
                "model_used": "gpt-oss-20b",
                "provider": "huggingface_transformers",
                "cost": 0.0,  # Local inference is free
                "tokens_generated": len(response.split())
            }
            
        except Exception as e:
            logger.error(f"Quick consistency check failed: {e}")
            raise LLMError(f"Consistency check failed: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models and system status"""
        return {
            "loaded_models": list(self._loaded_models.keys()),
            "available_models": list(self.MODELS.keys()),
            "device_info": self.device_info,
            "usage_stats": self.usage_stats,
            "memory_usage": {
                "cuda_allocated": f"{torch.cuda.memory_allocated() / 1024**3:.2f}GB" if torch.cuda.is_available() else "N/A",
                "cuda_cached": f"{torch.cuda.memory_reserved() / 1024**3:.2f}GB" if torch.cuda.is_available() else "N/A"
            }
        }
    
    def clear_cache(self):
        """Clear model cache to free memory"""
        with self._model_lock:
            for model in self._loaded_models.values():
                del model
            for tokenizer in self._loaded_tokenizers.values():
                del tokenizer
            
            self._loaded_models.clear()
            self._loaded_tokenizers.clear()
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("🗑️  Model cache cleared")
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.api_key is not None
    
    async def generate_with_conversation_history(self, 
                                               conversation: List[Dict[str, str]]) -> str:
        """Generate response with conversation history"""
        try:
            # Use conversation directly as messages
            model, tokenizer = self._load_model_and_tokenizer(self.default_model)
            
            # Apply chat template with conversation history
            inputs = tokenizer.apply_chat_template(
                conversation[-10:],  # Last 10 messages
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt"
            ).to(model.device)
            
            # Generate
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=1000,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode response
            generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
            response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
            
            return response.strip()
            
        except Exception as e:
            raise LLMError(f"Conversation generation failed: {str(e)}")

# Global instance
huggingface_transformers_service = HuggingFaceTransformersService()

# Convenience functions for compatibility
async def hf_quick_check(dialogue: str, character: str) -> Dict[str, Any]:
    """Quick consistency check via direct transformers"""
    return await huggingface_transformers_service.quick_consistency_check(dialogue, character)

async def hf_generate_text(prompt: str, model: str = "gpt-oss-20b") -> str:
    """Generate text via direct transformers"""
    return await huggingface_transformers_service.generate_text(prompt, model_name=model)