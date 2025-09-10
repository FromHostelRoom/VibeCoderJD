import os
import json
import shutil
import sys
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import subprocess
import threading
import time

class ProjectManager:
    """Manage multiple files and projects within the IDE."""
    
    def __init__(self):
        self.current_project = None
        self.projects_dir = "/tmp/vibe_coder_projects"
        self.active_files = {}
        self.file_tree = {}
        self._ensure_projects_dir()
    
    def _ensure_projects_dir(self):
        """Ensure the projects directory exists."""
        os.makedirs(self.projects_dir, exist_ok=True)
    
    def create_new_project(self, project_name: str) -> str:
        """Create a new project directory."""
        project_path = os.path.join(self.projects_dir, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        # Create a default main.py file
        main_file = os.path.join(project_path, "main.py")
        with open(main_file, 'w') as f:
            f.write("# Welcome to your new project!\nprint('Hello, World!')\n")
        
        self.current_project = project_path
        self._update_file_tree()
        return project_path
    
    def load_project(self, project_path: str):
        """Load an existing project."""
        if os.path.exists(project_path):
            self.current_project = project_path
            self._update_file_tree()
            return True
        return False
    
    def _update_file_tree(self):
        """Update the file tree structure for the current project."""
        if not self.current_project:
            self.file_tree = {}
            return
        
        self.file_tree = self._build_tree(self.current_project)
    
    def _build_tree(self, path: str, prefix: str = "") -> Dict:
        """Recursively build file tree structure."""
        tree = {}
        try:
            items = sorted(os.listdir(path))
            for item in items:
                if item.startswith('.'):
                    continue
                
                item_path = os.path.join(path, item)
                relative_path = os.path.relpath(item_path, self.current_project)
                
                if os.path.isdir(item_path):
                    tree[item] = {
                        'type': 'directory',
                        'path': relative_path,
                        'children': self._build_tree(item_path, prefix + "  ")
                    }
                else:
                    tree[item] = {
                        'type': 'file',
                        'path': relative_path,
                        'size': os.path.getsize(item_path)
                    }
        except PermissionError:
            pass
        
        return tree
    
    def get_file_content(self, file_path: str) -> str:
        """Get content of a file in the current project."""
        if not self.current_project:
            return ""
        
        full_path = os.path.join(self.current_project, file_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                return "Binary file - cannot display content"
        return ""
    
    def save_file_content(self, file_path: str, content: str) -> bool:
        """Save content to a file in the current project."""
        if not self.current_project:
            return False
        
        full_path = os.path.join(self.current_project, file_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self._update_file_tree()
            return True
        except Exception:
            return False
    
    def create_file(self, file_path: str, content: str = "") -> bool:
        """Create a new file in the current project."""
        return self.save_file_content(file_path, content)
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from the current project."""
        if not self.current_project:
            return False
        
        full_path = os.path.join(self.current_project, file_path)
        try:
            if os.path.exists(full_path):
                if os.path.isfile(full_path):
                    os.remove(full_path)
                elif os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                self._update_file_tree()
                return True
        except Exception:
            pass
        return False
    
    def rename_file(self, old_path: str, new_path: str) -> bool:
        """Rename a file in the current project."""
        if not self.current_project:
            return False
        
        old_full_path = os.path.join(self.current_project, old_path)
        new_full_path = os.path.join(self.current_project, new_path)
        
        try:
            if os.path.exists(old_full_path):
                # Ensure new directory exists
                os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
                os.rename(old_full_path, new_full_path)
                self._update_file_tree()
                return True
        except Exception:
            pass
        return False
    
    def get_project_files(self) -> List[str]:
        """Get list of all Python files in the current project."""
        if not self.current_project:
            return []
        
        python_files = []
        for root, dirs, files in os.walk(self.current_project):
            for file in files:
                if file.endswith('.py'):
                    rel_path = os.path.relpath(os.path.join(root, file), self.current_project)
                    python_files.append(rel_path)
        
        return sorted(python_files)
    
    def get_project_stats(self) -> Dict:
        """Get statistics about the current project."""
        if not self.current_project:
            return {}
        
        stats = {
            'total_files': 0,
            'python_files': 0,
            'total_size': 0,
            'lines_of_code': 0
        }
        
        for root, dirs, files in os.walk(self.current_project):
            for file in files:
                file_path = os.path.join(root, file)
                stats['total_files'] += 1
                stats['total_size'] += os.path.getsize(file_path)
                
                if file.endswith('.py'):
                    stats['python_files'] += 1
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            stats['lines_of_code'] += len(f.readlines())
                    except:
                        pass
        
        return stats
    
    def install_requirements(self) -> Tuple[bool, str]:
        """Install requirements.txt if it exists in the project."""
        if not self.current_project:
            return False, "No project loaded"
        
        requirements_path = os.path.join(self.current_project, "requirements.txt")
        if not os.path.exists(requirements_path):
            return False, "No requirements.txt found"
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", requirements_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return True, "Requirements installed successfully"
            else:
                return False, f"Installation failed: {result.stderr}"
        
        except subprocess.TimeoutExpired:
            return False, "Installation timed out"
        except Exception as e:
            return False, f"Installation error: {str(e)}"