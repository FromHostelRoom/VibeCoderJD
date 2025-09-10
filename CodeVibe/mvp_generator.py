import os
import json
import tempfile
import shutil
import subprocess
import sys
from typing import Dict, List, Tuple
from pathlib import Path
import zipfile
from io import BytesIO

class MVPGenerator:
    """AI-powered MVP generator that creates complete projects from user prompts."""
    
    def __init__(self, ai_assistant):
        self.ai_assistant = ai_assistant
        self.project_templates = {
            "streamlit_app": {
                "description": "Interactive web app with Streamlit",
                "files": ["app.py", "requirements.txt", ".streamlit/config.toml"]
            },
            "flask_api": {
                "description": "REST API with Flask",
                "files": ["app.py", "requirements.txt", "README.md"]
            },
            "data_analysis": {
                "description": "Data analysis with Pandas and Matplotlib",
                "files": ["analysis.py", "requirements.txt", "data/sample_data.csv"]
            },
            "web_scraper": {
                "description": "Web scraper with requests and BeautifulSoup",
                "files": ["scraper.py", "requirements.txt", "config.json"]
            },
            "game": {
                "description": "Simple game with Pygame",
                "files": ["game.py", "requirements.txt", "assets/README.md"]
            }
        }
    
    def analyze_user_prompt(self, prompt: str) -> Dict:
        """Analyze user prompt and determine project type and requirements."""
        analysis_prompt = f"""
Analyze this user request and determine what type of MVP they want to build:

User Request: "{prompt}"

Please respond in JSON format with the following structure:
{{
    "project_type": "one of: streamlit_app, flask_api, data_analysis, web_scraper, game, custom",
    "project_name": "suggested project name (snake_case)",
    "description": "brief description of what the project will do",
    "key_features": ["list", "of", "main", "features"],
    "required_libraries": ["list", "of", "python", "libraries"],
    "main_files": ["list", "of", "files", "to", "create"],
    "complexity": "simple, medium, or complex"
}}

Focus on creating a practical, working MVP that demonstrates the core functionality.
"""
        
        messages = [{"role": "user", "content": analysis_prompt}]
        response = self.ai_assistant._get_ai_response(messages)
        
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except (json.JSONDecodeError, ValueError):
            # Fallback to simple analysis
            return {
                "project_type": "streamlit_app",
                "project_name": "user_project",
                "description": "Custom project based on user requirements",
                "key_features": ["Basic functionality"],
                "required_libraries": ["streamlit"],
                "main_files": ["app.py", "requirements.txt"],
                "complexity": "simple"
            }
    
    def generate_file_content(self, file_name: str, project_analysis: Dict, user_prompt: str) -> str:
        """Generate content for a specific file based on project analysis."""
        generation_prompt = f"""
Generate the complete content for the file: {file_name}

Project Details:
- Name: {project_analysis.get('project_name', 'project')}
- Type: {project_analysis.get('project_type', 'custom')}
- Description: {project_analysis.get('description', '')}
- Features: {', '.join(project_analysis.get('key_features', []))}
- Required Libraries: {', '.join(project_analysis.get('required_libraries', []))}

Original User Request: "{user_prompt}"

Requirements for {file_name}:
1. Write complete, working code that implements the core functionality
2. Include proper error handling and user feedback
3. Add helpful comments explaining key parts
4. Make sure the code is production-ready and follows Python best practices
5. If it's a web app, ensure it works on port 5000
6. Include all necessary imports and setup

IMPORTANT: Provide ONLY the raw file content without any markdown formatting, code blocks, or explanations. Do NOT include ```python or ``` markers. Start directly with the code.
"""
        
        messages = [{"role": "user", "content": generation_prompt}]
        response = self.ai_assistant._get_ai_response(messages)
        
        # Clean up any markdown formatting that might slip through
        cleaned_response = self._clean_code_response(response)
        return cleaned_response
    
    def _clean_code_response(self, response: str) -> str:
        """Remove markdown code blocks and other formatting from AI response."""
        # Remove markdown code blocks
        lines = response.split('\n')
        cleaned_lines = []
        
        skip_line = False
        for line in lines:
            stripped = line.strip()
            
            # Skip lines that are markdown code block markers
            if stripped.startswith('```'):
                skip_line = not skip_line
                continue
            
            # Skip if we're in a code block marker section
            if skip_line:
                continue
                
            cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Remove any remaining markdown formatting
        cleaned_content = cleaned_content.replace('```python', '')
        cleaned_content = cleaned_content.replace('```', '')
        
        # Remove leading/trailing whitespace but preserve internal structure
        cleaned_content = cleaned_content.strip()
        
        return cleaned_content
    
    def create_project_structure(self, project_analysis: Dict) -> str:
        """Create project directory structure and return the path."""
        project_name = project_analysis.get('project_name', 'generated_project')
        project_path = f"/tmp/{project_name}"
        
        # Remove existing project if it exists
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        
        # Create project directory
        os.makedirs(project_path, exist_ok=True)
        
        # Create subdirectories if needed
        main_files = project_analysis.get('main_files', ['app.py'])
        for file_path in main_files:
            full_path = os.path.join(project_path, file_path)
            dir_path = os.path.dirname(full_path)
            if dir_path and dir_path != project_path:
                os.makedirs(dir_path, exist_ok=True)
        
        return project_path
    
    def generate_mvp(self, user_prompt: str) -> Tuple[bool, str, Dict]:
        """
        Generate a complete MVP based on user prompt.
        
        Returns:
            tuple: (success, message, project_info)
        """
        try:
            # Step 1: Analyze user prompt
            project_analysis = self.analyze_user_prompt(user_prompt)
            
            # Step 2: Create project structure
            project_path = self.create_project_structure(project_analysis)
            
            # Step 3: Generate files
            generated_files = {}
            main_files = project_analysis.get('main_files', ['app.py', 'requirements.txt'])
            
            for file_name in main_files:
                content = self.generate_file_content(file_name, project_analysis, user_prompt)
                file_path = os.path.join(project_path, file_name)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Write content to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                generated_files[file_name] = content
            
            project_info = {
                'path': project_path,
                'analysis': project_analysis,
                'files': generated_files,
                'main_file': self._get_main_file(project_analysis)
            }
            
            return True, f"Successfully generated MVP: {project_analysis.get('project_name', 'project')}", project_info
            
        except Exception as e:
            return False, f"Error generating MVP: {str(e)}", {}
    
    def _get_main_file(self, project_analysis: Dict) -> str:
        """Determine the main file to run for the project."""
        project_type = project_analysis.get('project_type', 'custom')
        main_files = project_analysis.get('main_files', ['app.py'])
        
        # Look for common main file patterns
        for file_name in main_files:
            if file_name in ['app.py', 'main.py', 'run.py']:
                return file_name
            if file_name.endswith('.py') and not file_name.startswith('test_'):
                return file_name
        
        return main_files[0] if main_files else 'app.py'
    
    def create_project_zip(self, project_info: Dict) -> bytes:
        """Create a downloadable zip file of the generated project."""
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            project_path = project_info['path']
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, project_path)
                    zip_file.write(file_path, arc_name)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def get_project_preview_command(self, project_info: Dict) -> str:
        """Get the command to run the project for preview."""
        project_analysis = project_info.get('analysis', {})
        project_type = project_analysis.get('project_type', 'custom')
        main_file = project_info.get('main_file', 'app.py')
        
        if project_type == 'streamlit_app':
            return f"streamlit run {main_file} --server.port 5000"
        elif project_type == 'flask_api':
            return f"python {main_file}"
        else:
            return f"python {main_file}"