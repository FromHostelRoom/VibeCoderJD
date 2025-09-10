# -*- coding: utf-8 -*-
import streamlit as st
import os
import tempfile
import time
from io import StringIO
import traceback
import subprocess
import sys
from code_executor import CodeExecutor
from ai_assistant import AIAssistant
from utils import validate_python_syntax, format_error_message
from mvp_generator import MVPGenerator
from project_manager import ProjectManager
from preview_manager import PreviewManager

# Set SambaCloud API key (use environment variable in production)
if 'SAMBACLOUD_API_KEY' not in os.environ:
    os.environ['SAMBACLOUD_API_KEY'] = '9c0f7166-57d0-4f31-97b3-7d8698575065'

# Detect if running on Streamlit Cloud
IS_STREAMLIT_CLOUD = ('STREAMLIT_SHARING_MODE' in os.environ or 
                     'STREAMLIT_SERVER_HEADLESS' in os.environ or
                     'STREAMLIT_DEPLOYMENT' in os.environ or
                     'STREAMLIT_CLOUD' in os.environ or
                     'STREAMLIT_RUNTIME_CREDENTIALS_FILE' in os.environ or
                     'STREAMLIT_SERVER_PORT' in os.environ)

# Configure page
st.set_page_config(
    page_title="Vibe Coder - AI MVP Builder",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'code' not in st.session_state:
    st.session_state.code = '''# Welcome to Vibe Coder - AI MVP Builder!
# Describe what you want to build below and I'll create it for you!

def hello_world():
    print("Hello, World!")
    return "Ready to build amazing projects!"

result = hello_world()
print(f"Result: {result}")
'''

if 'output' not in st.session_state:
    st.session_state.output = ""

if 'execution_time' not in st.session_state:
    st.session_state.execution_time = 0

if 'ai_suggestions' not in st.session_state:
    st.session_state.ai_suggestions = ""

if 'current_project' not in st.session_state:
    st.session_state.current_project = None

if 'generated_project' not in st.session_state:
    st.session_state.generated_project = None

if 'project_files' not in st.session_state:
    st.session_state.project_files = {}

if 'active_file' not in st.session_state:
    st.session_state.active_file = "main.py"

if 'preview_manager' not in st.session_state:
    st.session_state.preview_manager = PreviewManager()

if 'show_mvp_generator' not in st.session_state:
    st.session_state.show_mvp_generator = True

# Initialize components
code_executor = CodeExecutor()

# Initialize AI assistant with error handling
try:
    ai_assistant = AIAssistant()
    # Check if any providers are available
    available_providers = ai_assistant.get_available_providers()
    if not available_providers:
        st.warning("⚠️ No AI providers are currently available. AI features will be limited.")
except Exception as e:
    st.error(f"❌ Error initializing AI assistant: {e}")
    ai_assistant = None

mvp_generator = MVPGenerator(ai_assistant) if ai_assistant else None
project_manager = ProjectManager()
preview_manager = st.session_state.preview_manager

# Main title and header
st.title("🚀 Vibe Coder - AI MVP Builder")
st.markdown("*Describe what you want to build, and I'll create a complete working project for you!*")

# Show cloud deployment notice
if IS_STREAMLIT_CLOUD:
    st.info("🌟 **Running on Streamlit Cloud**: Generated projects will be available for download. For live previews, download and run projects locally.")
elif 'localhost' in st.get_option('server.baseUrlPath') if hasattr(st, 'get_option') else False:
    st.success("💻 **Local Development Mode**: Full preview capabilities available.")
else:
    st.info("🔧 **Development Mode**: Preview capabilities may vary depending on your environment.")

# MVP Generator - Main Screen Placement
if st.session_state.show_mvp_generator:
    st.markdown("---")
    st.header("🎯 AI MVP Generator")
    
    # Large prominent input area
    mvp_col1, mvp_col2 = st.columns([3, 1])
    
    with mvp_col1:
        user_prompt = st.text_area(
            "**Describe what you want to build:**",
            height=120,
            placeholder="""Examples:
• "Create a todo list app with Streamlit where users can add, delete, and mark tasks as complete"
• "Build a weather dashboard that shows current weather and 5-day forecast"
• "Make a simple calculator with a GUI using tkinter"
• "Create a web scraper that gets news headlines from multiple sites"
• "Build a data analysis tool for CSV files with charts and statistics"
""",
            help="Be specific about what features you want - the more details, the better your MVP will be!"
        )
    
    with mvp_col2:
        st.markdown("### Quick Examples")
        if st.button("📝 Todo App", use_container_width=True):
            user_prompt = "Create a todo list app with Streamlit where users can add, delete, and mark tasks as complete"
            st.session_state.user_prompt = user_prompt
        
        if st.button("🌤️ Weather App", use_container_width=True):
            user_prompt = "Build a weather dashboard that shows current weather and 5-day forecast with beautiful charts"
            st.session_state.user_prompt = user_prompt
        
        if st.button("🧮 Calculator", use_container_width=True):
            user_prompt = "Make a simple calculator with a GUI that can do basic math operations"
            st.session_state.user_prompt = user_prompt
        
        if st.button("📊 Data Analyzer", use_container_width=True):
            user_prompt = "Create a data analysis tool for CSV files with charts and statistics"
            st.session_state.user_prompt = user_prompt
    
    # Generate button
    gen_col1, gen_col2, gen_col3 = st.columns([1, 2, 1])
    with gen_col2:
        if st.button("🚀 **GENERATE MY MVP**", type="primary", use_container_width=True, key="main_generate"):
            if user_prompt and user_prompt.strip():
                if not ai_assistant or not ai_assistant.get_available_providers():
                    st.error("❌ AI assistant is not available. Please check your API keys and dependencies.")
                    st.info("To use the MVP generator, you need at least one AI provider configured.")
                else:
                    with st.spinner("🤖 AI is building your complete MVP... This may take a minute."):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        status_text.text("🔍 Analyzing your requirements...")
                        progress_bar.progress(20)
                        
                        success, message, project_info = mvp_generator.generate_mvp(user_prompt)
                        progress_bar.progress(60)
                        
                        if success:
                            status_text.text("📁 Setting up project files...")
                            st.session_state.generated_project = project_info
                            st.session_state.current_project = project_info['path']
                            
                            # Load generated files into session
                            st.session_state.project_files = project_info['files']
                            st.session_state.active_file = project_info.get('main_file', 'app.py')
                            st.session_state.code = project_info['files'].get(st.session_state.active_file, '')
                            st.session_state.show_mvp_generator = False
                            
                            progress_bar.progress(100)
                            status_text.text("✅ MVP Generated Successfully!")
                            
                            st.success(f"🎉 {message}")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            progress_bar.progress(100)
                            status_text.text("❌ Generation failed")
                            st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Please describe what you want to build!")

# Project View - When MVP is generated
if st.session_state.generated_project and not st.session_state.show_mvp_generator:
    # Project header with info
    project_info = st.session_state.generated_project['analysis']
    
    st.markdown("---")
    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])
    
    with header_col1:
        st.header(f"📁 {project_info.get('project_name', 'My Project')}")
        st.caption(f"Type: {project_info.get('project_type', 'Custom')} | {project_info.get('description', '')}")
    
    with header_col2:
        if st.button("🔄 Generate New MVP", use_container_width=True):
            st.session_state.show_mvp_generator = True
            st.session_state.generated_project = None
            st.session_state.project_files = {}
            st.rerun()
    
    with header_col3:
        if st.button("💾 Download Project", use_container_width=True):
            try:
                zip_data = mvp_generator.create_project_zip(st.session_state.generated_project)
                project_name = st.session_state.generated_project['analysis'].get('project_name', 'project')
                
                st.download_button(
                    label="⬇️ Download ZIP",
                    data=zip_data,
                    file_name=f"{project_name}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error creating download: {str(e)}")
    
    # Main project layout
    proj_col1, proj_col2, proj_col3 = st.columns([1, 2, 1])
    
    # File Tree and Project Structure
    with proj_col1:
        st.subheader("📂 Project Files")
        
        project_files = list(st.session_state.project_files.keys())
        
        # Show file tree structure
        for file_name in sorted(project_files):
            file_icon = "📄" if file_name.endswith('.py') else "📋" if file_name.endswith('.txt') else "⚙️" if file_name.endswith('.toml') else "📄"
            
            # Highlight active file
            if file_name == st.session_state.active_file:
                st.markdown(f"**🔹 {file_icon} {file_name}**")
            else:
                if st.button(f"{file_icon} {file_name}", key=f"file_{file_name}", use_container_width=True):
                    st.session_state.active_file = file_name
                    st.session_state.code = st.session_state.project_files[file_name]
                    st.rerun()
        
        st.markdown("---")
        st.subheader("📊 Project Stats")
        st.metric("Files", len(project_files))
        st.metric("Main File", st.session_state.active_file)
        
        # Key features
        st.markdown("**🎯 Features:**")
        features = project_info.get('key_features', [])
        for feature in features:
            st.markdown(f"• {feature}")
        
        # Required libraries
        st.markdown("**📚 Libraries:**")
        libraries = project_info.get('required_libraries', [])
        for lib in libraries:
            st.markdown(f"• {lib}")
    
    # Code Editor
    with proj_col2:
        st.subheader(f"📝 {st.session_state.active_file}")
        
        # File actions
        file_actions_col1, file_actions_col2 = st.columns(2)
        
        with file_actions_col1:
            if st.button("💾 Save Changes", use_container_width=True):
                # Save changes back to the project
                st.session_state.project_files[st.session_state.active_file] = st.session_state.code
                
                # Also save to file system
                project_path = st.session_state.generated_project['path']
                file_path = os.path.join(project_path, st.session_state.active_file)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(st.session_state.code)
                
                st.success("✅ Changes saved!")
        
        with file_actions_col2:
            if st.button("🚀 Run This File", use_container_width=True):
                # Execute the current file
                with st.spinner("Running..."):
                    try:
                        project_path = st.session_state.generated_project['path']
                        original_cwd = os.getcwd()
                        try:
                            os.chdir(project_path)
                            output, error = code_executor.execute_code(st.session_state.code)
                        finally:
                            os.chdir(original_cwd)
                        
                        if error:
                            st.error(f"❌ Error: {error}")
                        else:
                            st.success(f"✅ Output: {output}" if output else "✅ Executed successfully")
                    except Exception as e:
                        st.error(f"❌ Execution Error: {str(e)}")
        
        # Code editor
        try:
            from streamlit_ace import st_ace
            
            new_code = st_ace(
                value=st.session_state.code,
                language='python',
                theme='monokai',
                key=f"editor_{st.session_state.active_file}",
                height=500,
                auto_update=True,
                font_size=14,
                tab_size=4,
                wrap=True
            )
            
            if new_code != st.session_state.code:
                st.session_state.code = new_code
                
        except ImportError:
            new_code = st.text_area(
                "Code Editor",
                value=st.session_state.code,
                height=500,
                key=f"textarea_{st.session_state.active_file}"
            )
            st.session_state.code = new_code
        
        # Syntax validation
        syntax_valid, syntax_error = validate_python_syntax(st.session_state.code)
        if not syntax_valid:
            st.error(f"⚠️ Syntax Error: {syntax_error}")
        else:
            st.success("✅ Syntax is valid")
    
    # Live Preview Panel
    with proj_col3:
        st.subheader("👀 Live Preview")
        
        # Get preview status
        preview_status = preview_manager.get_preview_status()
        
        # Preview controls
        preview_col1, preview_col2 = st.columns(2)
        
        with preview_col1:
            if not preview_status["is_running"]:
                preview_button_text = "📥 Generate Download" if IS_STREAMLIT_CLOUD else "▶️ Start Preview"
                button_type = "secondary" if IS_STREAMLIT_CLOUD else "primary"
                
                if st.button(preview_button_text, use_container_width=True, type=button_type):
                    project_path = st.session_state.generated_project['path']
                    main_file = st.session_state.generated_project.get('main_file', 'app.py')
                    project_type = project_info.get('project_type', 'custom')
                    
                    with st.spinner("🚀 Preparing your project..."):
                        success, message = preview_manager.start_preview(project_path, main_file, project_type)
                        
                        if success:
                            st.success(message)
                            if not IS_STREAMLIT_CLOUD:
                                time.sleep(2)  # Give the server time to start
                            st.rerun()
                        else:
                            st.error(message)
            else:
                st.success("✅ Preview Running")
        
        with preview_col2:
            if preview_status["is_running"]:
                if st.button("⏹️ Stop Preview", use_container_width=True):
                    preview_manager.stop_preview()
                    st.info("Preview stopped")
                    st.rerun()
        
        # Embedded preview display
        if preview_status["is_running"] and preview_status["url"]:
            st.markdown("---")
            st.markdown("**🌐 Live Application:**")
            
            # Try different approaches for iframe display
            try:
                    # Check if we're in Streamlit Cloud mode
                    if preview_status["status"] == "cloud_mode" or preview_status.get("url") == "streamlit_cloud_mode":
                        # Streamlit Cloud deployment mode - show download and code preview
                        st.markdown("### 📦 Your Generated MVP is Ready!")
                        
                        st.info("🌟 **Streamlit Cloud Mode**: Your MVP has been generated successfully! Download it to run locally or deploy it separately.")
                        
                        # Show download button
                        if preview_status.get('url') and preview_status['url'] != "streamlit_cloud_mode":
                            zip_path = preview_status['url']  # This is actually the zip file path
                            if os.path.exists(zip_path):
                                with open(zip_path, 'rb') as f:
                                    st.download_button(
                                        label="📥 Download MVP Project",
                                        data=f.read(),
                                        file_name="generated_mvp.zip",
                                        mime="application/zip",
                                        use_container_width=True
                                    )
                        else:
                            # Create download on demand
                            try:
                                zip_data = mvp_generator.create_project_zip(st.session_state.generated_project)
                                project_name = st.session_state.generated_project['analysis'].get('project_name', 'project')
                                
                                st.download_button(
                                    label="📥 Download MVP Project",
                                    data=zip_data,
                                    file_name=f"{project_name}.zip",
                                    mime="application/zip",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Error creating download: {str(e)}")
                        
                        st.markdown("### 👁️ Code Preview")
                        
                        # Show instructions for running locally
                        st.markdown("""
                        **📋 To run your MVP locally:**
                        1. Download the project ZIP file above
                        2. Extract it to your desired location
                        3. Open terminal/command prompt in the project folder
                        4. Install dependencies: `pip install -r requirements.txt`
                        5. Run the app: `streamlit run app.py`
                        """)
                        
                        # Show file structure and main file content
                        if preview_status.get("project_path"):
                            project_path = preview_status["project_path"]
                            main_file = "app.py"  # Default main file
                            
                            # Show main file content
                            main_file_path = os.path.join(project_path, main_file)
                            if os.path.exists(main_file_path):
                                with open(main_file_path, 'r') as f:
                                    code_content = f.read()
                                
                                st.markdown(f"**📄 {main_file} (Preview):**")
                                st.code(code_content[:1500] + "..." if len(code_content) > 1500 else code_content, language="python")
                        
                        # Show project structure
                        st.markdown("**📂 Project Structure:**")
                        for file_name in sorted(st.session_state.project_files.keys()):
                            st.markdown(f"• {file_name}")
                
                    else:
                        # Regular preview mode for local development
                        preview_url = preview_status['url']
                        
                        # Show the preview link
                        st.markdown(f"🌐 **[Open Preview in New Tab]({preview_url})**")
                        
                        iframe_height = 400
                        st.markdown("**Preview:**")
                        
                        # Local environments - show iframe (only if not localhost in cloud)
                        if not preview_url.startswith('http://localhost') or 'STREAMLIT_CLOUD' not in os.environ:
                            iframe_html = f'''
                            <iframe 
                                src="{preview_url}" 
                                width="100%" 
                                height="{iframe_height}px" 
                                frameborder="0"
                                style="border: 1px solid #ddd; border-radius: 5px;"
                                sandbox="allow-same-origin allow-scripts allow-forms"
                            ></iframe>
                            '''
                            st.components.v1.html(iframe_html, height=iframe_height + 10, scrolling=True)
                        else:
                            st.info("Preview is running locally. Click the link above to open in a new tab.")
                        
                        # Fallback information
                        st.markdown(f"""
                        <div style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px; text-align: center;">
                            <p style="margin: 0; color: #6c757d;">
                                If the preview doesn't load above, click the link to open in a new tab
                            </p>
                            <code style="color: #e83e8c; font-size: 12px;">{preview_url}</code>
                        </div>
                        """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Preview display error: {e}")
                st.markdown(f"**Preview URL:** {preview_status['url']}")
            
            # Refresh button
            if st.button("🔄 Refresh Preview", use_container_width=True):
                st.rerun()
        
        elif preview_status["status"] == "starting":
            st.info("🔄 Preview is starting... Please wait.")
            time.sleep(2)
            st.rerun()
        
        elif preview_status["status"] == "failed":
            st.error("❌ Preview failed to start. Check the logs below.")
        
        else:
            st.info("👆 Click 'Start Preview' to see your app running live!")
        
        st.markdown("---")
        
        # Preview information
        st.markdown("**🔧 Preview Info:**")
        main_file = st.session_state.generated_project.get('main_file', 'app.py')
        st.markdown(f"• Main file: `{main_file}`")
        
        project_type = project_info.get('project_type', 'custom')
        if project_type == 'streamlit_app':
            st.markdown("• Type: Streamlit Web App")
        elif project_type == 'flask_api':
            st.markdown("• Type: Flask API")
        else:
            st.markdown(f"• Type: {project_type}")
        
        if preview_status["url"]:
            st.markdown(f"• URL: {preview_status['url']}")
        
        # Preview logs (expandable)
        if preview_status["is_running"]:
            with st.expander("📋 Preview Logs"):
                stdout, stderr = preview_manager.get_preview_logs()
                if stdout:
                    st.text_area("Output:", stdout, height=100)
                if stderr:
                    st.text_area("Errors:", stderr, height=100)
        
        # Project actions
        st.markdown("---")
        st.markdown("**⚡ Quick Actions:**")
        
        if st.button("🔄 Regenerate Project", use_container_width=True):
            preview_manager.stop_preview()  # Stop preview before regenerating
            st.session_state.show_mvp_generator = True
            st.rerun()
        
        if st.button("📝 Edit Description", use_container_width=True):
            st.session_state.show_mvp_generator = True
            st.rerun()

# Regular Code Editor (when no project is generated)
elif not st.session_state.generated_project:
    st.markdown("---")
    
    # Regular IDE layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Code Editor")
        
        # Code editor
        try:
            from streamlit_ace import st_ace
            
            new_code = st_ace(
                value=st.session_state.code,
                language='python',
                theme='monokai',
                key="main_editor",
                height=400,
                auto_update=True,
                font_size=14,
                tab_size=4,
                wrap=True
            )
            
            if new_code != st.session_state.code:
                st.session_state.code = new_code
                
        except ImportError:
            new_code = st.text_area(
                "Python Code Editor",
                value=st.session_state.code,
                height=400
            )
            st.session_state.code = new_code
        
        # Execution controls
        exec_col1, exec_col2, exec_col3 = st.columns(3)
        
        with exec_col1:
            run_button = st.button("🚀 Run Code", type="primary", use_container_width=True)
        
        with exec_col2:
            clear_button = st.button("🗑️ Clear Output", use_container_width=True)
        
        with exec_col3:
            clear_code_button = st.button("📄 New File", use_container_width=True)
    
    with col2:
        st.subheader("📺 Output Console")
        
        if run_button:
            with st.spinner("Executing code..."):
                try:
                    start_time = time.time()
                    output, error = code_executor.execute_code(st.session_state.code)
                    execution_time = time.time() - start_time
                    
                    st.session_state.execution_time = execution_time
                    
                    if error:
                        st.session_state.output = f"❌ Error:\n{format_error_message(error)}"
                    else:
                        st.session_state.output = f"✅ Success:\n{output}" if output else "✅ Code executed successfully"
                        
                except Exception as e:
                    st.session_state.output = f"❌ Execution Error:\n{str(e)}"
        
        if clear_button:
            st.session_state.output = ""
            st.session_state.execution_time = 0
            st.rerun()
        
        if clear_code_button:
            st.session_state.code = "# New Python file\n\n"
            st.session_state.output = ""
            st.rerun()
        
        # Output display
        if st.session_state.output:
            st.text_area(
                "Output",
                value=st.session_state.output,
                height=300,
                disabled=True
            )
            
            if st.session_state.execution_time > 0:
                st.caption(f"⏱️ Execution time: {st.session_state.execution_time:.3f} seconds")
        else:
            st.info("👆 Click 'Run Code' to see output here")

# AI Assistant Section
st.markdown("---")
st.subheader("🤖 AI Assistant")

# Check if AI is available
if not ai_assistant or not ai_assistant.get_available_providers():
    st.warning("⚠️ AI Assistant is not available. Please check your API keys and dependencies.")
    st.info("To use AI features, set one of these environment variables:\n- ANTHROPIC_API_KEY\n- OPENAI_API_KEY\n- SAMBACLOUD_API_KEY")
else:
    ai_col1, ai_col2, ai_col3, ai_col4 = st.columns(4)

    with ai_col1:
        get_suggestions = st.button("💡 Get Suggestions", use_container_width=True)

    with ai_col2:
        explain_code = st.button("📖 Explain Code", use_container_width=True)

    with ai_col3:
        debug_code = st.button("🐛 Debug Code", use_container_width=True)

    with ai_col4:
        optimize_code = st.button("⚡ Optimize Code", use_container_width=True)

    # User question input
    user_question = st.text_area(
        "Ask AI anything about your code:",
        height=80,
        placeholder="e.g., 'How can I add error handling?', 'Make this more efficient', 'Add a database'"
    )

    ask_ai = st.button("🎯 Ask AI", type="secondary", use_container_width=True)

    # AI responses
    if get_suggestions:
        with st.spinner("Getting AI suggestions..."):
            suggestions = ai_assistant.get_code_suggestions(st.session_state.code)
            st.session_state.ai_suggestions = suggestions

    if explain_code:
        with st.spinner("Analyzing code..."):
            explanation = ai_assistant.explain_code(st.session_state.code)
            st.session_state.ai_suggestions = explanation

    if debug_code:
        with st.spinner("Debugging code..."):
            if st.session_state.output and "Error" in st.session_state.output:
                debug_help = ai_assistant.debug_error(st.session_state.code, st.session_state.output)
            else:
                debug_help = ai_assistant.get_code_suggestions(st.session_state.code)
            st.session_state.ai_suggestions = debug_help

    if optimize_code:
        with st.spinner("Optimizing code..."):
            optimization = ai_assistant.ask_question(st.session_state.code, "How can I optimize this code for better performance and readability?")
            st.session_state.ai_suggestions = optimization

    if ask_ai and user_question:
        with st.spinner("Processing your question..."):
            response = ai_assistant.ask_question(st.session_state.code, user_question)
            st.session_state.ai_suggestions = response

    # AI suggestions display
    if st.session_state.ai_suggestions:
        st.text_area(
            "AI Response",
            value=st.session_state.ai_suggestions,
            height=150,
            disabled=True
        )
        
        if st.button("🗑️ Clear AI Response"):
            st.session_state.ai_suggestions = ""
            st.rerun()
    else:
        st.info("🤖 AI assistant ready to help! Use the buttons above or ask a question.")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # AI Provider Settings
    if ai_assistant:
        available_providers = ai_assistant.get_available_providers()
        provider_status = ai_assistant.get_provider_status()
        
        # Show provider status
        st.subheader("🤖 AI Provider Status")
        for provider, status in provider_status.items():
            if status:
                st.success(f"✅ {provider}")
            else:
                st.error(f"❌ {provider}")
        
        if available_providers:
            current_provider = st.selectbox(
                "Active AI Provider",
                available_providers,
                help="Choose your AI assistant provider"
            )
            ai_assistant.set_provider(current_provider)
        else:
            st.error("⚠️ No AI providers available. Please check your API keys.")
            st.info("To use AI features, set one of these environment variables:\n- ANTHROPIC_API_KEY\n- OPENAI_API_KEY\n- SAMBACLOUD_API_KEY")
    else:
        st.error("❌ AI Assistant not initialized")
        st.info("Please check your dependencies and API keys.")
    
    # Execution settings
    st.subheader("🔧 Code Execution")
    timeout = st.slider("Timeout (seconds)", 1, 60, 30)
    code_executor.set_timeout(timeout)
    
    # About
    st.subheader("ℹ️ About")
    st.markdown("""
    **Vibe Coder** - AI MVP Builder
    
    🚀 Generate complete projects from descriptions
    📁 Multi-file project management  
    👀 Live preview capabilities
    🤖 AI-powered code assistance
    💾 Download projects as ZIP files
    """)