"""
Test Mistral Local Connection
==============================

This script tests if you can load and run a Mistral model locally.
It uses a lightweight model by default for faster testing.
"""

import sys
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test if required libraries are installed"""
    print("\n" + "=" * 60)
    print("Step 1: Testing Imports")
    print("=" * 60)
    
    try:
        import transformers
        import torch
        print(f"✅ transformers: {transformers.__version__}")
        print(f"✅ torch: {torch.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstall with: pip install transformers torch")
        return False


def test_model_loading(model_name="HuggingFaceTB/SmolLM-135M-Instruct"):
    """Test loading a local model"""
    print("\n" + "=" * 60)
    print("Step 2: Testing Model Loading")
    print(f"Model: {model_name}")
    print("=" * 60)
    
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        print("Loading tokenizer...")
        start = time.time()
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print(f"✅ Tokenizer loaded in {time.time()-start:.1f}s")
        
        print("Loading model (this may take a while)...")
        start = time.time()
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto"
        )
        print(f"✅ Model loaded in {time.time()-start:.1f}s")
        
        return model, tokenizer
        
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return None, None


def test_inference(model, tokenizer, prompt="What is system monitoring?"):
    """Test model inference"""
    print("\n" + "=" * 60)
    print("Step 3: Testing Inference")
    print(f"Prompt: '{prompt}'")
    print("=" * 60)
    
    try:
        print("Generating response...")
        start = time.time()
        
        # Format prompt for instruction model
        messages = [{"role": "user", "content": prompt}]
        formatted_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Tokenize
        inputs = tokenizer(formatted_prompt, return_tensors="pt")
        
        # Generate
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
        
        # Decode
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        elapsed = time.time() - start
        print(f"✅ Response generated in {elapsed:.1f}s")
        print(f"\n📝 Response:\n{response[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Inference failed: {e}")
        return False


def test_with_devops_context(model, tokenizer):
    """Test with DevOps monitoring context"""
    print("\n" + "=" * 60)
    print("Step 4: Testing DevOps Context")
    print("=" * 60)
    
    prompt = """You are a DevOps monitoring assistant. 
Given these metrics:
- CPU: 85%
- Memory: 60%
- Disk: 70%

What action should be taken?"""
    
    try:
        messages = [{"role": "user", "content": prompt}]
        formatted_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = tokenizer(formatted_prompt, return_tensors="pt")
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.7
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("✅ DevOps reasoning test passed")
        print(f"\n📝 AI Recommendation:\n{response[:400]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ DevOps test failed: {e}")
        return False


def test_agent_reasoning():
    """Test the agent's reasoning module in local mode"""
    print("\n" + "=" * 60)
    print("Step 5: Testing Agent Reasoning Module")
    print("=" * 60)
    
    try:
        from reasoning import MistralReasoner, ReasoningMode
        
        print("Initializing reasoner in LOCAL mode...")
        reasoner = MistralReasoner(mode=ReasoningMode.LOCAL)
        
        # Check if it fell back to mock
        if reasoner.mode == ReasoningMode.MOCK:
            print("⚠️  Model loading failed, fell back to MOCK mode")
            print("This is expected if the model download failed")
            return False
        
        print("✅ Reasoner initialized in LOCAL mode")
        
        # Test analysis
        metrics = {
            'cpu': {'percent': 85, 'status': 'warning'},
            'memory': {'percent': 60, 'status': 'normal'}
        }
        
        print("Testing metric analysis...")
        result = reasoner.analyze_metrics(metrics, "Check system health")
        
        print(f"✅ Analysis complete")
        print(f"   Action: {result.action}")
        print(f"   Tool: {result.tool_to_use}")
        print(f"   Confidence: {result.confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent reasoning test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 MISTRAL LOCAL CONNECTION TEST")
    print("=" * 60)
    
    results = []
    
    # Step 1: Imports
    if not test_imports():
        print("\n❌ Cannot continue without dependencies")
        sys.exit(1)
    results.append(True)
    
    # Step 2: Model Loading
    # Using a lightweight model for testing
    # For real Mistral, use: "mistralai/Mistral-7B-Instruct-v0.2"
    model_name = "HuggingFaceTB/SmolLM-135M-Instruct"
    print(f"\n💡 Using lightweight model for testing: {model_name}")
    print("   (Mistral-7B would take longer to download)")
    
    model, tokenizer = test_model_loading(model_name)
    if model is None:
        print("\n⚠️  Model loading failed - this is common on first run")
        print("   The model will download automatically (~500MB)")
        print("   Check your internet connection and disk space")
        results.append(False)
    else:
        results.append(True)
        
        # Step 3: Inference
        results.append(test_inference(model, tokenizer))
        
        # Step 4: DevOps Context
        results.append(test_with_devops_context(model, tokenizer))
    
    # Step 5: Agent Integration
    results.append(test_agent_reasoning())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYou can now use LOCAL mode in the DevOps Agent:")
        print("  from config import AgentConfig")
        print("  config = AgentConfig(reasoning_mode='local')")
        print("  agent = DevOpsAgent(config)")
    else:
        print("\n⚠️  Some tests failed")
        print("\nYou can still use the agent in MOCK mode:")
        print("  config = AgentConfig(reasoning_mode='mock')")
        print("  agent = DevOpsAgent(config)")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
