# Vibe Coder - AI MVP Builder

An AI-powered tool for generating complete MVP projects from simple descriptions.

## Features

🚀 **AI MVP Generator**: Describe what you want to build and get a complete working project
📁 **Multi-file Project Management**: Full project structure with proper file organization  
👀 **Live Preview**: See your generated projects running in real-time (local mode)
🤖 **AI Code Assistant**: Get help with coding, debugging, and optimization
💾 **Project Downloads**: Download generated projects as ZIP files

## Deployment on Streamlit Cloud

This application is optimized for Streamlit Cloud deployment. When deployed:

- Generated MVPs will be available for download as ZIP files
- Live previews are disabled in cloud mode (for security)
- All core functionality remains available

### Deploying to Streamlit Cloud

1. Fork this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Set the main file path: `app.py`
6. Deploy!

### Environment Variables (Optional)

- `SAMBACLOUD_API_KEY`: Your SambaCloud API key for AI features
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI provider)
- `ANTHROPIC_API_KEY`: Anthropic API key (if using Claude provider)

## Local Development

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CodeVibe
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

### Local Features

When running locally, you get additional features:
- Live preview of generated Streamlit apps
- Local Flask API testing
- Real-time code execution

## Usage

1. **Describe Your Project**: Use the large text area to describe what you want to build
2. **Generate MVP**: Click the "Generate My MVP" button
3. **Explore Your Project**: Browse the generated files in the file tree
4. **Download or Preview**: Download the project ZIP or preview it live (local mode)
5. **Get AI Help**: Use the AI assistant for code suggestions and improvements

## Example Prompts

- "Create a todo list app with Streamlit where users can add, delete, and mark tasks as complete"
- "Build a weather dashboard that shows current weather and 5-day forecast"
- "Make a simple calculator with a GUI using tkinter"
- "Create a data analysis tool for CSV files with charts and statistics"

## Dependencies

- `streamlit`: Web framework
- `anthropic`: AI provider for code generation
- `openai`: Alternative AI provider
- `streamlit-ace`: Enhanced code editor (optional)

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues or questions, please open an issue on GitHub.
