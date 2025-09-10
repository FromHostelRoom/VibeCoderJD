import subprocess
import os
import sys
import threading
import time
import signal
import socket
# import psutil  # Optional dependency
from typing import Optional, Dict, Tuple

class PreviewManager:
    """Manages preview processes and embedded display of generated applications."""
    
    def __init__(self):
        self.preview_process = None
        self.preview_port = 8502  # Use different port to avoid conflicts
        self.preview_project_path = None
        self.preview_status = "stopped"
        self.preview_url = None
    
    def start_preview(self, project_path: str, main_file: str, project_type: str = "streamlit_app") -> Tuple[bool, str]:
        """Start preview for a generated project."""
        try:
            # Stop any existing preview
            self.stop_preview()
            
            # Check if we're running on Streamlit Cloud
            if self._is_streamlit_cloud():
                return self._handle_streamlit_cloud_preview(project_path, main_file, project_type)
            
            # Install requirements if they exist
            requirements_file = os.path.join(project_path, 'requirements.txt')
            if os.path.exists(requirements_file):
                install_result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", requirements_file
                ], capture_output=True, text=True, timeout=120)
                
                if install_result.returncode != 0:
                    return False, f"Failed to install requirements: {install_result.stderr}"
            
            # Determine command based on project type
            if project_type == "streamlit_app" or main_file.endswith("app.py"):
                cmd = [
                    sys.executable, "-m", "streamlit", "run", 
                    os.path.join(project_path, main_file),
                    "--server.port", str(self.preview_port),
                    "--server.address", "0.0.0.0",
                    "--server.headless", "true",
                    "--server.enableCORS", "false",
                    "--server.enableXsrfProtection", "false",
                    "--server.enableWebsocketCompression", "false",
                    "--server.allowRunOnSave", "false"
                ]
                # Dynamic URL detection that works anywhere
                self.preview_url = self._get_dynamic_preview_url(self.preview_port)
                
            elif project_type == "flask_api":
                # For Flask apps, we need to modify the main file to run on correct port
                # Note: Flask apps won't work properly on Streamlit Cloud
                if self._is_streamlit_cloud():
                    return self._handle_streamlit_cloud_preview(project_path, main_file, project_type)
                
                self._prepare_flask_app(project_path, main_file)
                cmd = [sys.executable, os.path.join(project_path, main_file)]
                self.preview_url = f"http://0.0.0.0:5001"
                
            else:
                # For other Python scripts, create a simple web wrapper
                # On Streamlit Cloud, handle this specially
                if self._is_streamlit_cloud():
                    return self._handle_streamlit_cloud_preview(project_path, main_file, project_type)
                
                self._create_web_wrapper(project_path, main_file)
                cmd = [
                    sys.executable, "-m", "streamlit", "run",
                    os.path.join(project_path, "_web_wrapper.py"),
                    "--server.port", str(self.preview_port),
                    "--server.address", "0.0.0.0",
                    "--server.headless", "true"
                ]
                self.preview_url = self._get_dynamic_preview_url(self.preview_port)
            
            # Start the preview process
            self.preview_process = subprocess.Popen(
                cmd,
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.preview_project_path = project_path
            self.preview_status = "starting"
            
            # Wait a moment for the process to start
            time.sleep(3)
            
            if self.preview_process.poll() is None:
                self.preview_status = "running"
                return True, f"Preview started successfully at {self.preview_url}"
            else:
                error_output = self.preview_process.stderr.read()
                self.preview_status = "failed"
                return False, f"Preview failed to start: {error_output}"
                
        except subprocess.TimeoutExpired:
            return False, "Requirements installation timed out"
        except Exception as e:
            self.preview_status = "failed"
            return False, f"Preview error: {str(e)}"
    
    def stop_preview(self) -> bool:
        """Stop the current preview process."""
        try:
            if self.preview_process and self.preview_process.poll() is None:
                # Try graceful termination first
                self.preview_process.terminate()
                
                # Wait a bit for graceful shutdown
                try:
                    self.preview_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful termination failed
                    self.preview_process.kill()
                    self.preview_process.wait()
                
                self.preview_process = None
            
            # Also kill any processes using the preview port
            self._kill_processes_on_port(self.preview_port)
            
            self.preview_status = "stopped"
            self.preview_url = None
            return True
            
        except Exception as e:
            print(f"Error stopping preview: {e}")
            return False
    
    def get_preview_status(self) -> Dict:
        """Get current preview status and information."""
        if self.preview_process:
            is_running = self.preview_process.poll() is None
            if not is_running and self.preview_status == "running":
                self.preview_status = "stopped"
        
        return {
            "status": self.preview_status,
            "url": self.preview_url,
            "port": self.preview_port,
            "project_path": self.preview_project_path,
            "is_running": self.preview_process is not None and self.preview_process.poll() is None
        }
    
    def _prepare_flask_app(self, project_path: str, main_file: str):
        """Prepare Flask app to run on the correct port."""
        main_file_path = os.path.join(project_path, main_file)
        
        if os.path.exists(main_file_path):
            with open(main_file_path, 'r') as f:
                content = f.read()
            
            # Add port configuration if not present
            if 'app.run(' not in content and 'if __name__ == "__main__":' in content:
                content = content.replace(
                    'if __name__ == "__main__":',
                    'if __name__ == "__main__":\n    app.run(host="0.0.0.0", port=5001, debug=True)'
                )
            elif 'app.run()' in content:
                content = content.replace(
                    'app.run()',
                    'app.run(host="0.0.0.0", port=5001, debug=True)'
                )
            
            with open(main_file_path, 'w') as f:
                f.write(content)
    
    def _create_web_wrapper(self, project_path: str, main_file: str):
        """Create a Streamlit wrapper for non-web Python scripts."""
        wrapper_content = f'''
import streamlit as st
import subprocess
import sys
import os

st.title("Preview: {main_file}")
st.markdown("---")

if st.button("Run Script", type="primary"):
    with st.spinner("Running script..."):
        try:
            result = subprocess.run([
                sys.executable, "{main_file}"
            ], capture_output=True, text=True, timeout=30)
            
            if result.stdout:
                st.subheader("Output:")
                st.code(result.stdout)
            
            if result.stderr:
                st.subheader("Errors:")
                st.code(result.stderr)
                
            if result.returncode == 0:
                st.success("Script executed successfully!")
            else:
                st.error(f"Script failed with return code: {{result.returncode}}")
                
        except subprocess.TimeoutExpired:
            st.error("Script execution timed out")
        except Exception as e:
            st.error(f"Error running script: {{str(e)}}")

# Show script content
st.subheader("Script Content:")
try:
    with open("{main_file}", "r") as f:
        script_content = f.read()
    st.code(script_content, language="python")
except Exception as e:
    st.error(f"Could not read script: {{str(e)}}")
'''
        
        wrapper_path = os.path.join(project_path, "_web_wrapper.py")
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_content)
    
    def _is_streamlit_cloud(self) -> bool:
        """Check if running on Streamlit Cloud."""
        return ('STREAMLIT_SHARING_MODE' in os.environ or 
                'STREAMLIT_SERVER_HEADLESS' in os.environ or
                'STREAMLIT_DEPLOYMENT' in os.environ or
                'STREAMLIT_CLOUD' in os.environ or
                os.environ.get('STREAMLIT_DEPLOYMENT', '').lower() == 'cloud' or
                # Additional checks for Streamlit Cloud
                'STREAMLIT_RUNTIME_CREDENTIALS_FILE' in os.environ or
                'STREAMLIT_SERVER_PORT' in os.environ)
    
    def _handle_streamlit_cloud_preview(self, project_path: str, main_file: str, project_type: str) -> Tuple[bool, str]:
        """Handle preview when running on Streamlit Cloud."""
        # On Streamlit Cloud, we can't run multiple Streamlit apps on different ports
        # Instead, we'll create a downloadable zip file and show code preview
        
        self.preview_status = "cloud_mode"
        self.preview_project_path = project_path
        
        # Create a downloadable version
        try:
            import zipfile
            import tempfile
            
            # Create zip file with the generated project
            zip_path = os.path.join(tempfile.gettempdir(), f"generated_mvp_{int(time.time())}.zip")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_path)
                        zipf.write(file_path, arcname)
            
            self.preview_url = zip_path  # Store zip path instead of URL
            return True, "Preview ready for Streamlit Cloud (download mode)"
            
        except Exception as e:
            return False, f"Failed to prepare cloud preview: {str(e)}"
    
    def _get_dynamic_preview_url(self, port: int) -> str:
        """Get dynamic preview URL that works on any machine."""
        # For Streamlit Cloud deployment, we should not use localhost
        # Instead, detect the environment and handle accordingly
        
        # Check for Streamlit Cloud environment
        if self._is_streamlit_cloud():
            # On Streamlit Cloud, we can't run multiple Streamlit apps
            # Return a placeholder that will be handled differently
            return "streamlit_cloud_mode"
        
        # Check for Heroku environment
        elif 'HEROKU_APP_NAME' in os.environ:
            app_name = os.environ.get('HEROKU_APP_NAME')
            return f"https://{app_name}.herokuapp.com"
        
        # Check for other cloud environments with domain info
        elif 'SERVER_NAME' in os.environ:
            server_name = os.environ.get('SERVER_NAME')
            return f"https://{server_name}"
        
        # For local development only
        else:
            # Use localhost for local development
            return f"http://localhost:{port}"
    
    def _kill_processes_on_port(self, port: int):
        """Kill any processes using the specified port."""
        try:
            # Try to use psutil if available
            try:
                import psutil
                for proc in psutil.process_iter(['pid', 'name', 'connections']):
                    try:
                        for conn in proc.info['connections'] or []:
                            if conn.laddr.port == port:
                                proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except ImportError:
                # Fallback method using lsof/netstat (Unix systems)
                import subprocess
                try:
                    result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                          capture_output=True, text=True)
                    if result.stdout:
                        pids = result.stdout.strip().split('\n')
                        for pid in pids:
                            if pid:
                                subprocess.run(['kill', '-9', pid])
                except:
                    pass  # Ignore if lsof is not available
        except Exception:
            pass  # Ignore errors in cleanup
    
    def get_preview_logs(self) -> Tuple[str, str]:
        """Get stdout and stderr from the preview process."""
        if not self.preview_process:
            return "", ""
        
        try:
            # Non-blocking read of available output
            stdout_data = ""
            stderr_data = ""
            
            if self.preview_process.stdout:
                stdout_data = self.preview_process.stdout.read()
            if self.preview_process.stderr:
                stderr_data = self.preview_process.stderr.read()
            
            return stdout_data, stderr_data
        except Exception:
            return "", ""