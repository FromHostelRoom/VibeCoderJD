# Streamlit Cloud Deployment Guide

## Quick Deployment Steps

### 1. Prepare Your Repository
- Ensure all files are in your GitHub repository
- Make sure `requirements.txt` is present and contains all dependencies
- Verify `.streamlit/config.toml` is configured properly

### 2. Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Set the main file path: `app.py`
6. Click "Deploy!"

### 3. Environment Variables (Optional)
Set these in Streamlit Cloud's "Advanced settings" if you want to use specific AI providers:

- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `OPENAI_API_KEY`: Your OpenAI API key  
- `SAMBACLOUD_API_KEY`: Your SambaCloud API key

### 4. Features on Streamlit Cloud

**✅ Available Features:**
- Full MVP generation interface
- Project file management
- Code editing and syntax validation
- Project download as ZIP files
- AI code assistance (with API keys)

**⚠️ Limited Features:**
- Live preview is disabled for security (download projects to run locally)
- Multiple Streamlit app instances not supported

## Local Development

### Setup
```bash
git clone <your-repo>
cd CodeVibe
pip install -r requirements.txt
streamlit run app.py
```

### Full Local Features
- Live preview of generated Streamlit apps
- Flask API testing
- Real-time code execution
- All AI providers

## Troubleshooting

### Common Issues:

1. **AI Assistant Not Available**
   - Check that at least one API key is set
   - Verify dependencies are installed: `pip install anthropic openai`

2. **Import Errors**
   - Ensure all dependencies in `requirements.txt` are available
   - For optional features, the app gracefully degrades

3. **Preview Not Working**
   - On Streamlit Cloud: This is expected, use download feature
   - Local: Check port availability and firewall settings

### Support
- Check the sidebar for AI provider status
- Error messages will guide you to missing dependencies or configuration issues
