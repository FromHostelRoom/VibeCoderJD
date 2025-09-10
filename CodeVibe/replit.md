# Vibe Coder - Python Web IDE

## Overview

Vibe Coder is an AI-powered Python Web IDE built with Streamlit that provides a secure environment for writing, executing, and debugging Python code. The application combines code execution capabilities with AI assistance from multiple providers (Anthropic Claude and OpenAI GPT) to help users write better code through intelligent suggestions and error analysis.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses Streamlit as the web framework, providing a reactive UI with real-time code editing and execution feedback. The interface is designed with a wide layout and collapsible sidebar to maximize code viewing space. Session state management handles code persistence, execution output, and AI suggestions across user interactions.

### Backend Architecture
The system follows a modular architecture with three core components:

1. **Code Execution Engine** (`CodeExecutor`): Implements sandboxed Python code execution with security restrictions and timeout protection. Uses subprocess isolation and restricts dangerous imports and operations to prevent system compromise.

2. **AI Assistant** (`AIAssistant`): Multi-provider AI integration supporting both Anthropic Claude (claude-sonnet-4-20250514) and OpenAI GPT (gpt-5) models. Automatically detects available API keys and initializes appropriate clients with fallback mechanisms.

3. **Utility Functions** (`utils.py`): Provides code validation using AST parsing for syntax checking without execution, along with error message formatting for improved user experience.

### Security Model
The application implements multiple security layers:
- Static analysis to detect dangerous code patterns before execution
- Import restrictions preventing access to system-level modules
- Execution timeout limits to prevent infinite loops
- Sandboxed execution environment using temporary files

### Error Handling and Validation
Comprehensive error handling includes syntax validation before execution, formatted error messages with line numbers and context, and graceful degradation when AI services are unavailable.

## External Dependencies

### AI Services
- **Anthropic Claude API**: Primary AI provider using claude-sonnet-4-20250514 model for code assistance
- **OpenAI API**: Secondary AI provider using gpt-5 model as fallback option

### Python Libraries
- **Streamlit**: Web framework for the user interface
- **AST**: Built-in Python module for syntax validation
- **Subprocess**: For isolated code execution
- **Tempfile**: For secure temporary file handling during code execution

### Environment Configuration
The application requires API keys configured as environment variables:
- `ANTHROPIC_API_KEY` for Claude integration
- `OPENAI_API_KEY` for OpenAI integration

The system gracefully handles missing API keys by disabling the corresponding AI features while maintaining core code execution functionality.