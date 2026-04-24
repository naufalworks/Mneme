#!/bin/bash
# HyperCode CLI - Quick Start Script

echo "🚀 HyperCode CLI - Quick Start"
echo "================================"
echo ""

# Check if index exists
if [ ! -d ".hypercode" ]; then
    echo "📁 No index found. Initializing..."
    python3 hc_enhanced.py init
    echo ""
fi

echo "✅ HyperCode is ready!"
echo ""
echo "Available commands:"
echo ""
echo "  🔍 Search:"
echo "     python3 hc_enhanced.py search \"query\""
echo ""
echo "  💭 Ask AI:"
echo "     python3 hc_enhanced.py ask \"How does X work?\""
echo ""
echo "  📝 Code Review:"
echo "     python3 hc_enhanced.py review file.py"
echo ""
echo "  🔍 Pattern Detection:"
echo "     python3 hc_enhanced.py patterns"
echo ""
echo "  🔗 Find Similar:"
echo "     python3 hc_enhanced.py similar file.py"
echo ""
echo "  📊 Statistics:"
echo "     python3 hc_enhanced.py stats"
echo ""
echo "Try it now:"
echo "  python3 hc_enhanced.py ask \"What does this codebase do?\""
echo ""
