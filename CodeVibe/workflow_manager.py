import subprocess
import os
import sys
import time
from typing import Dict, Optional, Tuple

class WorkflowManager:
    """Manages Replit workflows for preview applications."""
    
    def __init__(self):
        self.active_preview_workflow = None
        self.preview_port = 8502
    
    def create_preview_workflow(self, project_path: str, main_file: str, project_type: str = "streamlit_app") -> Tuple[bool, str]:
        """Create and start a Replit workflow for preview."""
        try:
            # Stop any existing preview workflow
            if self.active_preview_workflow:
                self.stop_preview_workflow()
            
            # Determine the command based on project type
            if project_type == "streamlit_app" or main_file.endswith("app.py"):
                command = f"cd {project_path} && python -m streamlit run {main_file} --server.port {self.preview_port} --server.address 0.0.0.0 --server.headless true"
                workflow_name = f"Preview_App_{int(time.time())}"
            else:
                command = f"cd {project_path} && python {main_file}"
                workflow_name = f"Python_Script_{int(time.time())}"
            
            # Create workflow configuration
            self.active_preview_workflow = {
                'name': workflow_name,
                'command': command,
                'project_path': project_path,
                'main_file': main_file,
                'port': self.preview_port if project_type == "streamlit_app" else None
            }
            
            return True, f"Preview workflow created: {workflow_name}"
            
        except Exception as e:
            return False, f"Failed to create preview workflow: {str(e)}"
    
    def stop_preview_workflow(self) -> bool:
        """Stop the current preview workflow."""
        if self.active_preview_workflow:
            try:
                # In a real implementation, this would stop the Replit workflow
                self.active_preview_workflow = None
                return True
            except Exception:
                return False
        return True
    
    def get_preview_url(self) -> Optional[str]:
        """Get the preview URL for the current workflow."""
        if self.active_preview_workflow and self.active_preview_workflow.get('port'):
            # Check for Streamlit Cloud environment
            if self._is_streamlit_cloud():
                return "streamlit_cloud_mode"  # Special handling for cloud
            # For local development only
            return f"http://localhost:{self.preview_port}"
        return None
    
    def _is_streamlit_cloud(self) -> bool:
        """Check if running on Streamlit Cloud."""
        return ('STREAMLIT_SHARING_MODE' in os.environ or 
                'STREAMLIT_SERVER_HEADLESS' in os.environ or
                'STREAMLIT_DEPLOYMENT' in os.environ or
                'STREAMLIT_CLOUD' in os.environ or
                os.environ.get('STREAMLIT_DEPLOYMENT', '').lower() == 'cloud' or
                'STREAMLIT_RUNTIME_CREDENTIALS_FILE' in os.environ or
                'STREAMLIT_SERVER_PORT' in os.environ)
    
    def get_workflow_info(self) -> Dict:
        """Get information about the current workflow."""
        if self.active_preview_workflow:
            return {
                'name': self.active_preview_workflow['name'],
                'command': self.active_preview_workflow['command'],
                'project_path': self.active_preview_workflow['project_path'],
                'main_file': self.active_preview_workflow['main_file'],
                'port': self.active_preview_workflow.get('port'),
                'url': self.get_preview_url(),
                'status': 'running'
            }
        return {'status': 'stopped'}