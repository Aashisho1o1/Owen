#!/bin/bash

# Enhanced AI Integration Setup Script
# Sets up local Ollama + HuggingFace cloud fallback for optimal cost/performance

set -e  # Exit on any error

echo "🚀 DOG Writer Enhanced AI Integration Setup"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
    print_status "Detected macOS system"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
    print_status "Detected Linux system"
else
    print_error "Unsupported platform: $OSTYPE"
    print_error "This script supports macOS and Linux only"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VERSION detected"
    
    # Check memory
    if [[ "$PLATFORM" == "macOS" ]]; then
        MEMORY_GB=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
    else
        MEMORY_GB=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024/1024)}')
    fi
    
    print_status "Available RAM: ${MEMORY_GB}GB"
    
    if [[ $MEMORY_GB -lt 16 ]]; then
        print_warning "Only ${MEMORY_GB}GB RAM detected. 16GB+ recommended for local models."
        print_warning "You can still use HuggingFace cloud models with lower RAM."
    else
        print_success "Sufficient RAM for local models (${MEMORY_GB}GB)"
    fi
    
    # Check disk space
    if [[ "$PLATFORM" == "macOS" ]]; then
        FREE_SPACE_GB=$(df -g . | tail -1 | awk '{print $4}')
    else
        FREE_SPACE_GB=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    fi
    
    print_status "Available disk space: ${FREE_SPACE_GB}GB"
    
    if [[ $FREE_SPACE_GB -lt 20 ]]; then
        print_warning "Only ${FREE_SPACE_GB}GB disk space available. 20GB+ recommended."
    else
        print_success "Sufficient disk space (${FREE_SPACE_GB}GB)"
    fi
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    cd backend
    
    if [[ ! -f "requirements.txt" ]]; then
        print_error "requirements.txt not found in backend directory"
        exit 1
    fi
    
    # Install dependencies
    python3 -m pip install -r requirements.txt --user
    
    print_success "Python dependencies installed"
    cd ..
}

# Setup environment variables
setup_environment() {
    print_status "Setting up environment configuration..."
    
    # Create .env file if it doesn't exist
    if [[ ! -f "backend/.env" ]]; then
        print_status "Creating backend/.env file..."
        touch backend/.env
    fi
    
    # Check for HuggingFace API key
    if ! grep -q "HUGGINGFACE_API_KEY" backend/.env; then
        echo "" >> backend/.env
        echo "# HuggingFace API Configuration" >> backend/.env
        echo "# Get your free API key at: https://huggingface.co/settings/tokens" >> backend/.env
        echo "HUGGINGFACE_API_KEY=" >> backend/.env
        
        print_warning "HuggingFace API key not configured"
        echo "📋 To enable HuggingFace models:"
        echo "   1. Visit: https://huggingface.co/settings/tokens"
        echo "   2. Create a free API token"
        echo "   3. Add it to backend/.env: HUGGINGFACE_API_KEY=your_token_here"
        echo ""
    else
        print_success "HuggingFace API key configuration found"
    fi
    
    # Check for other API keys
    if ! grep -q "GEMINI_API_KEY" backend/.env; then
        print_status "Gemini API key not found (using existing configuration)"
    fi
}

# Install and setup Ollama
setup_ollama() {
    print_status "Setting up Ollama for local models..."
    
    if command_exists ollama; then
        print_success "Ollama already installed"
    else
        print_status "Installing Ollama..."
        
        if [[ "$PLATFORM" == "macOS" ]]; then
            # Download and install Ollama for macOS
            curl -fsSL https://ollama.ai/install.sh | sh
        else
            # Download and install Ollama for Linux
            curl -fsSL https://ollama.ai/install.sh | sh
        fi
        
        if command_exists ollama; then
            print_success "Ollama installed successfully"
        else
            print_error "Ollama installation failed"
            print_warning "You can still use cloud models (HuggingFace, Gemini)"
            return 1
        fi
    fi
    
    # Check if Ollama is running
    if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_status "Starting Ollama service..."
        
        # Start Ollama in background
        ollama serve &
        OLLAMA_PID=$!
        
        # Wait for Ollama to start
        for i in {1..30}; do
            if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            print_success "Ollama service started"
        else
            print_error "Failed to start Ollama service"
            return 1
        fi
    else
        print_success "Ollama service already running"
    fi
    
    # Download models
    print_status "Checking for gpt-oss models..."
    
    AVAILABLE_MODELS=$(ollama list 2>/dev/null | grep gpt-oss || echo "")
    
    if [[ -z "$AVAILABLE_MODELS" ]]; then
        echo ""
        echo "📥 Model Download Options:"
        echo "   1. gpt-oss:20b  (14GB) - Fast model, good for real-time checks"
        echo "   2. gpt-oss:120b (65GB) - Powerful model, excellent for deep analysis"
        echo ""
        
        if [[ $MEMORY_GB -ge 16 && $FREE_SPACE_GB -ge 20 ]]; then
            read -p "Download gpt-oss:20b model? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_status "Downloading gpt-oss:20b model (this may take 10-20 minutes)..."
                ollama pull gpt-oss:20b
                print_success "gpt-oss:20b model downloaded"
            fi
            
            if [[ $MEMORY_GB -ge 32 && $FREE_SPACE_GB -ge 80 ]]; then
                read -p "Download gpt-oss:120b model? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    print_status "Downloading gpt-oss:120b model (this may take 30-60 minutes)..."
                    ollama pull gpt-oss:120b
                    print_success "gpt-oss:120b model downloaded"
                fi
            fi
        else
            print_warning "Insufficient resources for model download"
            print_status "You can manually download later with: ollama pull gpt-oss:20b"
        fi
    else
        print_success "Found existing gpt-oss models:"
        echo "$AVAILABLE_MODELS"
    fi
}

# Run integration test
run_tests() {
    print_status "Running integration tests..."
    
    if [[ -f "test_enhanced_llm_integration.py" ]]; then
        python3 test_enhanced_llm_integration.py --quick
        
        if [[ $? -eq 0 ]]; then
            print_success "Integration tests passed"
        else
            print_warning "Some tests failed (this is expected if API keys are not configured)"
        fi
    else
        print_warning "Test script not found, skipping tests"
    fi
}

# Display final setup information
show_completion_info() {
    echo ""
    echo "🎉 Enhanced AI Integration Setup Complete!"
    echo "========================================"
    echo ""
    echo "💡 Your DOG Writer now supports:"
    echo "   🏠 Local inference (Ollama + gpt-oss) - Zero cost, private"
    echo "   🤗 HuggingFace API - Low cost, reliable cloud fallback"  
    echo "   🧠 Smart routing - Automatically selects optimal model"
    echo "   💰 Cost optimization - Tracks usage and saves money"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Configure API keys in backend/.env (optional but recommended)"
    echo "   2. Start your backend: cd backend && python -m uvicorn main:app --reload"
    echo "   3. Test the integration: python test_enhanced_llm_integration.py"
    echo ""
    echo "📊 Expected performance:"
    echo "   • Local models: 5-15s response time, $0 cost"
    echo "   • HuggingFace: 10-30s response time, ~80% cheaper than Gemini"
    echo "   • Automatic fallback ensures reliability"
    echo ""
    echo "❓ Need help? Check the LOCAL_AI_INTEGRATION.md documentation"
}

# Main execution
main() {
    check_requirements
    install_python_deps
    setup_environment
    
    # Ask if user wants to set up local models
    echo ""
    read -p "Set up local Ollama models for zero-cost inference? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_ollama
    else
        print_status "Skipping local model setup - cloud models only"
    fi
    
    run_tests
    show_completion_info
}

# Run main function
main "$@"