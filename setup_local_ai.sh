#!/bin/bash
# OpenAI gpt-oss Setup Script for DOG Writer
# Automates the installation of Ollama and gpt-oss models

set -e  # Exit on any error

echo "🚀 DOG Writer - OpenAI gpt-oss Setup Script"
echo "============================================"
echo "This script will install Ollama and download gpt-oss models"
echo "for cost-free, local AI inference in your writing assistant."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check system requirements
check_requirements() {
    echo "📋 Checking system requirements..."
    
    # Check available RAM
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        RAM_GB=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        RAM_GB=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024/1024)}')
    else
        print_warning "Cannot detect RAM automatically. Assuming sufficient memory."
        RAM_GB=16
    fi
    
    print_info "Detected RAM: ${RAM_GB}GB"
    
    if [ $RAM_GB -lt 16 ]; then
        print_error "Insufficient RAM detected (${RAM_GB}GB)"
        print_error "Minimum requirement: 16GB RAM for gpt-oss:20b"
        echo "Consider upgrading your system or using cloud models only."
        exit 1
    elif [ $RAM_GB -lt 32 ]; then
        print_warning "RAM: ${RAM_GB}GB - can run gpt-oss:20b only"
        INSTALL_120B=false
    else
        print_status "RAM: ${RAM_GB}GB - can run both models"
        INSTALL_120B=true
    fi
    
    # Check available disk space
    FREE_SPACE_GB=$(df . | awk 'NR==2 {print int($4/1024/1024)}')
    print_info "Available disk space: ${FREE_SPACE_GB}GB"
    
    if [ $FREE_SPACE_GB -lt 20 ]; then
        print_error "Insufficient disk space (${FREE_SPACE_GB}GB)"
        print_error "Minimum requirement: 20GB for gpt-oss:20b (80GB for both models)"
        exit 1
    fi
}

# Install Ollama
install_ollama() {
    echo ""
    echo "🔽 Installing Ollama..."
    
    if command -v ollama &> /dev/null; then
        print_status "Ollama is already installed"
        ollama --version
    else
        print_info "Downloading and installing Ollama..."
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            curl -fsSL https://ollama.ai/install.sh | sh
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            curl -fsSL https://ollama.ai/install.sh | sh
        else
            print_error "Unsupported operating system: $OSTYPE"
            print_info "Please install Ollama manually from https://ollama.ai"
            exit 1
        fi
        
        if command -v ollama &> /dev/null; then
            print_status "Ollama installed successfully"
        else
            print_error "Ollama installation failed"
            exit 1
        fi
    fi
}

# Start Ollama service
start_ollama() {
    echo ""
    echo "🚀 Starting Ollama service..."
    
    # Check if Ollama is already running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_status "Ollama service is already running"
    else
        print_info "Starting Ollama service in background..."
        
        # Start Ollama in background
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        OLLAMA_PID=$!
        
        # Wait for service to start
        echo "Waiting for Ollama to start..."
        for i in {1..30}; do
            if curl -s http://localhost:11434/api/tags &> /dev/null; then
                print_status "Ollama service started successfully (PID: $OLLAMA_PID)"
                break
            fi
            sleep 1
            echo -n "."
        done
        
        if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
            print_error "Failed to start Ollama service"
            print_info "Try starting manually: ollama serve"
            exit 1
        fi
    fi
}

# Download models
download_models() {
    echo ""
    echo "📥 Downloading gpt-oss models..."
    
    # Download gpt-oss:20b (fast model)
    echo ""
    print_info "Downloading gpt-oss:20b (14GB) - Fast model for real-time analysis"
    print_warning "This may take 5-20 minutes depending on your internet speed..."
    
    if ollama pull gpt-oss:20b; then
        print_status "gpt-oss:20b downloaded successfully"
    else
        print_error "Failed to download gpt-oss:20b"
        exit 1
    fi
    
    # Download gpt-oss:120b if system can handle it
    if [ "$INSTALL_120B" = true ]; then
        echo ""
        echo "Would you like to download gpt-oss:120b (65GB) for better analysis quality?"
        echo "This requires 64GB+ RAM and will take 20-60 minutes to download."
        read -p "Download gpt-oss:120b? (y/N): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Downloading gpt-oss:120b (65GB) - Powerful model for complex reasoning"
            print_warning "This will take 20-60 minutes depending on your internet speed..."
            
            if ollama pull gpt-oss:120b; then
                print_status "gpt-oss:120b downloaded successfully"
            else
                print_warning "Failed to download gpt-oss:120b (continuing with 20b only)"
            fi
        else
            print_info "Skipping gpt-oss:120b download"
        fi
    fi
}

# Test installation
test_installation() {
    echo ""
    echo "🧪 Testing installation..."
    
    # List available models
    print_info "Available models:"
    ollama list | grep gpt-oss || print_warning "No gpt-oss models found"
    
    # Test inference
    echo ""
    print_info "Testing model inference..."
    
    TEST_RESPONSE=$(ollama run gpt-oss:20b "Hello! Can you help me analyze dialogue consistency?" --timeout 30)
    
    if [ $? -eq 0 ] && [ -n "$TEST_RESPONSE" ]; then
        print_status "Model inference test successful!"
        echo "Response preview: ${TEST_RESPONSE:0:100}..."
    else
        print_error "Model inference test failed"
        print_info "You may need to restart the service: ollama serve"
    fi
}

# Generate usage instructions
generate_instructions() {
    echo ""
    echo "📋 Setup Complete! Next Steps:"
    echo "=========================================="
    echo ""
    echo "1. 🎯 Test your installation:"
    echo "   python test_ollama_integration.py"
    echo ""
    echo "2. 🔄 Start your DOG Writer backend:"
    echo "   cd backend && python -m uvicorn main:app --reload"
    echo ""
    echo "3. 📊 Check new endpoints:"
    echo "   GET  /api/local-ai/status           - Check model status"
    echo "   POST /api/local-ai/quick-consistency-check - Fast analysis"
    echo "   GET  /api/local-ai/cost-analytics   - View savings"
    echo ""
    echo "4. 💰 Expected benefits:"
    echo "   • 100% cost savings on dialogue analysis"
    echo "   • 5-15 second response times"
    echo "   • Complete privacy (no data leaves your machine)"
    echo "   • Works offline"
    echo ""
    echo "5. 🛠️ To manage models:"
    echo "   ollama list                    - List installed models"
    echo "   ollama run gpt-oss:20b        - Interactive chat"
    echo "   ollama rm gpt-oss:20b         - Remove model"
    echo ""
    echo "6. 🔧 Troubleshooting:"
    echo "   • If service stops: ollama serve"
    echo "   • Check logs: tail -f /tmp/ollama.log"
    echo "   • Restart: pkill ollama && ollama serve"
    echo ""
    
    # Show estimated savings
    echo "💡 Estimated Monthly Savings:"
    echo "   Light usage (100 requests):  $5-15"
    echo "   Medium usage (500 requests): $25-75"
    echo "   Heavy usage (2000 requests): $100-300"
    echo ""
    
    print_status "OpenAI gpt-oss integration is ready!"
}

# Main execution
main() {
    echo "Starting automated setup..."
    echo ""
    
    check_requirements
    install_ollama
    start_ollama
    download_models
    test_installation
    generate_instructions
    
    echo ""
    print_status "🎉 Setup completed successfully!"
    echo "Your DOG Writer now has local AI capabilities with zero ongoing costs."
}

# Run main function
main "$@"
