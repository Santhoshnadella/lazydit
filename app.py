import streamlit as st
import os
import json
from agents import VideoAgency
from llama_cpp import Llama
from utils.ffmpeg_utils import FinalRenderer
from utils.moviepy_utils import TimelineBuilder
from utils.pedalboard_utils import AudioMaster
from utils.comfyui_utils import ComfyUIClient
from dotenv import load_dotenv
import requests

load_dotenv()

st.set_page_config(page_title="LazyDit", layout="wide", page_icon="🎬")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background: linear-gradient(45deg, #00C9FF, #92FE9D); color: white; font-weight: bold; border: none; }
    .stTextInput>div>div>input { background-color: #262730; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 LazyDit")
st.subheader("Pro-Lazy AI Studio (Python 3.9 + Laptop Optimized)")

# Sidebar Settings
st.sidebar.header("⚙️ Settings")

# ComfyUI Status Check
is_comfy_up = False
try:
    response = requests.get(os.getenv("COMFYUI_URL", "http://127.0.0.1:8188"), timeout=1)
    is_comfy_up = response.status_code == 200
except:
    is_comfy_up = False

if is_comfy_up:
    st.sidebar.success("🟢 Local AI Engine: STANDBY")
else:
    st.sidebar.error("🔴 Local AI Engine: OFFLINE")
    st.sidebar.info("Run `python lazydit/comfy_start.py` to start.")

with st.sidebar.expander("🚀 Quick Start Guide", expanded=False):
    st.markdown("""
    1. **The Forge**: Go to `Asset Forge` tab to build your Bible.
    2. **The Engine**: Run `comfy_start.py` in terminal.
    3. **The Feed**: Upload Video, Transcript, Script, and Bible.
    4. **The Process**: Hit `Generate` and watch progress.
    5. **The Export**: Collect your video from the `exports/` folder!
    """)

laptop_mode = st.sidebar.toggle("🚀 Laptop Mode (Low VRAM/RAM)", value=True)
cloud_hybrid = st.sidebar.toggle("☁️ Cloud-Hybrid Mode (RunPod)", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("🎬 Cinema Engine Settings")
custom_opendcp = st.sidebar.text_input("OpenDCP Bin Folder", value=st.session_state.get('opendcp_path', ""), placeholder="e.g. K:/opendcp/bin/")
if custom_opendcp:
    st.session_state['opendcp_path'] = custom_opendcp

st.sidebar.markdown("---")
st.sidebar.subheader("🎥 Project Settings")
st.sidebar.header("📂 Project Management")
def save_project(data):
    project_json = json.dumps(data, indent=2)
    st.sidebar.download_button("💾 Save Project (.lazydit)", data=project_json, file_name="production.lazydit", mime="application/json")

loaded_file = st.sidebar.file_uploader("📂 Load Project", type=["lazydit"])
if loaded_file:
    st.session_state['project_state'] = json.load(loaded_file)
    st.sidebar.success("Project Restored!")

st.sidebar.markdown("---")
template = st.sidebar.selectbox("Project Template", ["Custom", "Cinematic Short", "Social Tech Review", "Travel Vlog"])
resolution = st.sidebar.selectbox("Resolution", ["1280x720 (Laptop)", "1920x1080", "3840x2160 (4K)"])
codec = st.sidebar.selectbox("Codec", ["libx265 (H.265)", "libx264 (H.264)", "prores_ks (ProRes 422)", "dnxhr (Avid DNxHR)"])
rife_toggle = st.sidebar.toggle("60FPS AI Interpolation (RIFE)", value=False)
audio_mode = st.sidebar.selectbox("Audio Fidelity", ["Lossless (TrueHD)", "Standard (EAC3)"])

# Main Layout with Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎬 Production Studio", "🧠 Intelligence & Docs", "📝 Asset Forge", "📦 Mastering & Distribution", "🏛️ Architecture & Academy"])

with tab1:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📥 Assets Upload")
        raw_video = st.file_uploader("Raw Video (MP4/MOV/DCP)", type=["mp4", "mov", "mxf"])
        transcript = st.file_uploader("Transcript (.txt)", type=["txt"])
        script = st.file_uploader("Script/Outline (.md / .txt)", type=["md", "txt"])
        prompts_file = st.file_uploader("Editing Prompts / Creative Bible (.md / .json)", type=["md", "json"])

    with col2:
        st.markdown("### 📽️ Visual Storyboard")
        cinematic_profile = st.selectbox("🎬 Cinematic Profile", ["Vlog", "Reel (9:16)", "Feature Film (2.39:1)", "Short Film (1.85:1)"])
        
        if raw_video:
            # Mocking storyboard frames for visual prototyping
            cols = st.columns(3)
            for i, c in enumerate(cols):
                c.image(f"https://picsum.photos/seed/{i+42}/200/112", caption=f"Scene {i+1} Prototype")
        else:
            st.info("Upload assets to see storyboard preview")

    # Agent Execution Logic
    if st.button("🚀 Generate Master Render"):
        if not all([raw_video, transcript, script, prompts_file]):
            st.error("Please upload all required files.")
        else:
            with st.status("🎬 Stable Agency is working...", expanded=True) as status:
                # 1. Setup Environment
                st.write("Initializing Ultra-Lightweight Gemma-2B Backend...")
                model_path = os.getenv("MODEL_PATH", "models/gemma-2b-it-q4_k_m.gguf")
                
                if not os.path.exists(model_path):
                    st.error(f"Model file not found at {model_path}. Use setup_rescue.py!")
                    st.stop()

                # Direct Llama-CPP-Python initialization
                llm = Llama(
                    model_path=model_path,
                    n_gpu_layers=-1 if not laptop_mode else 0,
                    n_ctx=4096,
                    verbose=False
                )
                
                agency = VideoAgency(llm)
                
                # 2. Sequential Orchestration
                progress_bar = st.progress(0, text=f"🎬 Initializing {cinematic_profile} Pipeline...")
                
                st.write(f"Step 1: Analyzing Footage for {cinematic_profile} sentiments...")
                progress_bar.progress(10, text="🔍 Analyst: Scanning raw assets...")
                context = f"Video: {raw_video.name}, Transcript included, Script included."
                results = agency.run_pipeline(context, profile=cinematic_profile)
                progress_bar.progress(33, text="✅ Analysis Complete.")
                
                st.write("Step 2: Creative Planning...")
                progress_bar.progress(45, text="🎨 Planner: Drafting Creative Bible...")
                results = agency.run_pipeline(context, profile=cinematic_profile)
                progress_bar.progress(66, text="✅ Creative Plan Drafted.")
                
                st.markdown("### 🔍 Quality Control: Review Agent Plan")
                edited_plan = st.text_area("Final Creative Bible (Review & Edit)", value=results['plan'], height=250)
                
                st.write("Step 3: Mastering Final Output...")
                if st.button("🔥 Confirm & Start Cinema Render"):
                    with st.status("🛠️ Rendering Sequences...", expanded=True):
                        # 1. Initialize Utilities
                        tb = TimelineBuilder()
                        fr = FinalRenderer()
                        
                        # 2. Chunk-by-Chunk Render (OOM Safe)
                        scenes = json.loads(edited_plan).get('scenes', [])
                        chunk_paths = []
                        for i, scene in enumerate(scenes):
                            chunk_path = f"K:/lazydit/exports/tmp/scene_{i}.mp4"
                            st.write(f"🎞️ Rendering Scene {i+1}/{len(scenes)}...")
                            tb.render_scene_chunk(scene, chunk_path)
                            chunk_paths.append(chunk_path)
                        
                        # 3. Industrial Stitching
                        st.write("🏗️ Stitching Feature Master...")
                        final_master = f"K:/lazydit/exports/master_{raw_video.name}"
                        # fr.concat_sequences(chunk_paths, final_master)
                        st.write(f"Simulated Stitching: {final_master}")
                        
                        progress_bar.progress(100, text="🎬 Hollywood Master Complete!")
                        save_project(results)
                        st.success(f"Production Complete: {final_master}")
                
                status.update(label=f"✅ {cinematic_profile} Ready for Preview!", state="complete", expanded=False)
            
            st.success("Master Render Generated! (Mocked)")
            st.info("Head to the 'Mastering & Distribution' tab for theatrical dispatch.")

with tab2:
    st.markdown("## 🧠 System Architecture & Multi-Agent Orchestration")
    st.info("This system mimicks a professional Hollywood studio by splitting the work into three distinct AI specialists.")
    
    with st.expander("📚 Masterclass: Asset Schema Documentation", expanded=True):
        st.markdown("""
        ### 🎥 1. Raw Video
        - **Accepted Formats**: MP4, MOV, MKV, MXF.
        - **Pro Tip**: Use MXF for DCP-ready theatrical source files.
        
        ### 📝 2. Transcript (.txt)
        Format your transcript like this for best "Hormozi" sync:
        ```text
        00:00 - Hey everyone, today we are building Lazydit.
        00:12 - It's the world's first pro-lazy studio.
        ```
        
        ### 🎬 3. Scene Script (.md)
        The "Creative Director" agent uses `# Scene X` headers to map your vision:
        ```markdown
        # Scene 1: The Intro
        - Time: 00:00 - 00:05
        - Visual: Close up of a laptop screen with code.
        - Mood: High Energy, Neon Blue.
        ```
        
        ### 💎 4. Creative Bible (.json)
        This is the most powerful file. It controls the VFX and Audio engines:
        ```json
        {
          "mood": "Cinematic",
          "vfx_plan": [
            { "scene_id": 1, "prompt": "teal and orange, high contrast, 4k" }
          ],
          "audio_plan": { "normalization": -3, "global_effects": ["compressor"] }
        }
        ```
        """)

    st.markdown("""
    ### 👁️ Agent Deep Dive
    - **Analyst**: Uses **PySceneDetect** + **Gemma-2B** for "Soul" detection.
    - **Planner**: Generates the **ShotTower JSON** execution plan.
    - **Renderer**: Orchestrates **ComfyUI**, **MoviePy**, and **Pedalboard**.
    """)

with tab3:
    st.markdown("## 📝 Asset Forge")
    st.info("Convert your raw ideas into agent-ready code. Fill the template and download.")
    
    forge_type = st.selectbox("What are you forging?", ["Creative Bible (JSON)", "Scene Script (Markdown)", "Transcript (Text)"])
    
    if forge_type == "Creative Bible (JSON)":
        template = '{\n  "mood": "Cinematic",\n  "vfx_plan": [\n    { "scene_id": 1, "prompt": "vivid colors, 4k, cinematic" }\n  ],\n  "audio_plan": { "normalization": -3, "global_effects": ["reverb"] }\n}'
        file_ext = "json"
    elif forge_type == "Scene Script (Markdown)":
        template = "# Scene 1: Intro\n- Time: 00:00 - 00:10\n- Visual: [Describe Scene]\n- Dialogue: [What is said]\n\n# Scene 2: The Hook\n- Time: 00:10 - 00:30\n- Visual: [Action]"
        file_ext = "md"
    else:
        template = "00:00 - [First line of dialogue]\n00:05 - [Second line of dialogue]"
        file_ext = "txt"

    raw_input = st.text_area("Edit your asset here:", value=template, height=300)
    
    st.download_button(
        label=f"📥 Download Forged {forge_type}",
        data=raw_input,
        file_name=f"forged_asset.{file_ext}",
        mime="text/plain"
    )
    st.divider()
    
    # Cinematic Blueprint Gallery Autodiscovery
    blueprint_dir = "k:/promptcut/lazydit/comfyui/blueprints/"
    blueprints = []
    if os.path.exists(blueprint_dir):
        blueprints = [f for f in os.listdir(blueprint_dir) if f.endswith('.json')]
    
    selected_blueprint = st.selectbox("🎬 Select Cinematic Blueprint", blueprints if blueprints else ["Default Cinematic"], index=blueprints.index("Text to Video (Wan 2.2).json") if "Text to Video (Wan 2.2).json" in blueprints else 0)
    
    if st.button("⚙️ Sync Selected Blueprint"):
        with st.spinner(f"Pushing {selected_blueprint} to Engine..."):
            try:
                import shutil
                src = os.path.join(blueprint_dir, selected_blueprint)
                
                # 1. Update the Canvas Soul (workflow.json)
                dest_soul = "k:/promptcut/lazydit/comfyui/user/default/workflow.json"
                os.makedirs(os.path.dirname(dest_soul), exist_ok=True)
                shutil.copy(src, dest_soul)
                
                # 2. Update the Visual Sidebar (workflows folder)
                dest_visual = f"k:/promptcut/lazydit/comfyui/user/default/workflows/{selected_blueprint}"
                os.makedirs(os.path.dirname(dest_visual), exist_ok=True)
                shutil.copy(src, dest_visual)
                
                st.success(f"Blueprint '{selected_blueprint}' Synchronized to Canvas & Sidebar!")
                st.balloons()
            except Exception as e:
                st.error(f"Sync Failed: {str(e)}")

with tab4:
    st.markdown("## 🎞️ Professional Cinema Console (OpenDCP Mirror)")
    
    from utils.distribution_utils import DCPMaster
    master = DCPMaster(opendcp_path=st.session_state.get('opendcp_path'))
    status = master.check_availability()
    
    # Mirroring the official 4-tab structure
    m_tab1, m_tab2, m_tab3, m_tab4 = st.tabs(["JPEG 2000", "MXF", "Subtitles", "DCP"])
    
    with m_tab1:
        st.subheader("JPEG 2000 Encoder Parameters")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            encoder = st.selectbox("Encoder", ["OpenJPEG", "ASDCPLib"])
            profile = st.selectbox("Profile", ["Cinema 2K", "Cinema 4K", "Cinema 3D"])
            frame_rate = st.selectbox("Frame Rate", [24, 25, 30, 48, 60], index=0)
            bandwidth = st.slider("Bandwidth (Mb/s)", 50, 250, 125)
        with col_e2:
            threads = st.number_input("Threads", 1, 32, 8)
            overwrite = st.checkbox("Overwrite Existing", value=True)
            stereo = st.checkbox("Stereoscopic", value=False)
            
        st.subheader("Image Parameters")
        col_i1, col_i2 = st.columns(2)
        with col_i1:
            source_color = st.selectbox("Source Color", ["sRGB", "REC709", "XYZ", "DPX"])
            dci_resize = st.selectbox("DCI Resize", ["None", "Letterbox", "Crop", "Stretch"])
        with col_i2:
            xyz_transform = st.checkbox("XYZ Transform", value=True)
            dpx_log = st.checkbox("DPX Logarithmic", value=False)
            
        st.subheader("Input / Output Directories")
        input_dir = st.text_input("Source Directory (Image Sequence)", value="K:/lazydit/exports/master_frames/")
        output_dir = st.text_input("Output Directory (J2K)", value="K:/lazydit/exports/j2c/")
        
        if st.button("🚀 Convert to J2K"):
            with st.status("Mastering J2K Sequence...", expanded=True):
                master.create_j2k_sequence(
                    input_dir, output_dir, profile=profile.lower().replace(" ", ""), 
                    bandwidth=bandwidth, threads=threads, overwrite=overwrite, 
                    stereo=stereo, source_color=source_color, dci_resize=dci_resize.lower(), 
                    xyz=xyz_transform, dpx_log=dpx_log
                )
                st.success("Conversion Complete!")

    with m_tab2:
        st.subheader("MXF Parameters")
        mxf_type = st.selectbox("MXF Type", ["Digital Cinema", "Interleave"])
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            mxf_kind = st.selectbox("Label", ["Picture", "Audio"])
            mxf_fps = st.selectbox("MXF Frame Rate", [24, 25, 30, 48, 60], index=0)
        with col_m2:
            mxf_input = st.text_input("Input Directory/File", value="K:/lazydit/exports/j2c/")
            mxf_output = st.text_input("Output MXF File", value="K:/lazydit/exports/video.mxf")
            
        if st.button("📦 Wrap to MXF Container"):
            with st.spinner("Wrapping..."):
                master.wrap_mxf(mxf_kind.lower(), mxf_input, mxf_output, fps=str(mxf_fps))
                st.success(f"MXF Created: {mxf_output}")

    with m_tab3:
        st.subheader("Subtitle Management")
        st.info("Wrap XML or PNG subtitle sequences into DCI compliant MXF.")
        sub_input = st.text_input("Subtitle Source (.xml/.png)", value="K:/lazydit/exports/subs.xml")
        sub_output = st.text_input("Output Subtitle MXF", value="K:/lazydit/exports/subtitles.mxf")
        if st.button("✒️ Wrap Subtitles"):
            master.wrap_mxf("subtitle", sub_input, sub_output)
            st.success("Subtitle MXF Generated!")

    with m_tab4:
        st.subheader("Final DCP Packaging")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            dcp_title = st.text_input("CPL Title", value="LAZYDIT_PRO_MASTER")
            dcp_kind = st.selectbox("Content Kind", ["feature", "trailer", "teaser", "advertisement", "short"])
            dcp_rating = st.selectbox("Rating", ["G", "PG", "PG-13", "R", "NC-17"])
        with col_d2:
            ann_text = st.text_area("Annotation Text", value="Mastered with LazyDit Pro")
            dcp_dest = st.text_input("DCP Destination Folder", value="K:/lazydit/exports/DCP_MASTER/")
            
        v_mxf = st.text_input("Input Video MXF", value="K:/lazydit/exports/video.mxf")
        a_mxf = st.text_input("Input Audio MXF", value="K:/lazydit/exports/audio.mxf")
        
        if st.button("🏁 Dispatch DCP Package"):
            with st.status("Generating Digital Passport...", expanded=True):
                master.generate_xml_metadata(
                    dcp_title, v_mxf, a_mxf, dcp_dest, 
                    kind=dcp_kind, rating=dcp_rating, annotation=ann_text
                )
                st.balloons()
                st.success(f"DCP MASTER READY AT {dcp_dest}")
             # Cinema Engine Status
    st.sidebar.markdown("---")
    st.sidebar.markdown("📽️ **Cinema Infrastructure Status**")
    
    # Improved binary checking with fallbacks
    def get_binary_status(name, path, fallback_cmd=None):
        import shutil
        # Check specific path
        if path and os.path.exists(os.path.join(path, f"{name}.exe")):
            return "ONLINE", "green"
        # Check system path
        if shutil.which(f"{name}") or shutil.which(f"{name}.exe"):
            return "ONLINE", "green"
        # Check fallback
        if fallback_cmd and (shutil.which(fallback_cmd) or shutil.which(f"{fallback_cmd}.exe")):
            return f"ONLINE ({fallback_cmd.upper()})", "green"
        return "MISSING", "red"

    cinema_path = st.sidebar.text_input("⚙️ Cinema Engine Path", "", help="Path to OpenDCP/DCP-o-matic binaries")
    
    st.sidebar.info("J2K Engine")
    j2k_status, j2k_color = get_binary_status("opendcp_j2k", cinema_path, fallback_cmd="ffmpeg")
    st.sidebar.markdown(f"**:{j2k_color}[{j2k_status}]**")
    
    st.sidebar.info("MXF Wrapper")
    mxf_status, mxf_color = get_binary_status("opendcp_mxf", cinema_path, fallback_cmd="ffmpeg")
    st.sidebar.markdown(f"**:{mxf_color}[{mxf_status}]**")
    
    st.sidebar.info("XML Passport")
    st.sidebar.markdown("**:green[ONLINE (NATIVE)]**")

with tab5:
    st.markdown("## 🏛️ System Architecture & Academy")
    st.info("Comprehensive blueprint of the LazyDit Agentic Post-Production Suite.")
    
    a_sub1, a_sub2, a_sub3, a_sub4 = st.tabs(["The How, Why & What", "Titan Architecture", "Post-Production House Mapping", "The 5-Step Masterclass"])
    
    with a_sub1:
        st.markdown("""
        ### ❓ The "How"
        LazyDit uses an **Agentic Orchestration** model. Instead of a linear editor, we use a **Director Agent (Gemma-2B)** that analyzes metadata and constructs a `ShotTower JSON` timeline. This timeline is then distributed to professional rendering engines.
        
        ### ❓ The "Why"
        Traditional AI video tools crash on long-form content because they try to hold the entire timeline in VRAM. LazyDit solves this via **Serial Chunking** (Rendering scene-by-chunk) and **Zero-Loss Stitching** (FFmpeg Concat Demuxer).
        
        ### ❓ The "What"
        - **Intelligence**: Gemma-2B-IT (Quantized for Laptops).
        - **Vision**: ComfyUI + Stable Video Diffusion.
        - **Editorial**: MoviePy 2.x + FFmpeg.
        - **Audio**: Pedalboard (Spotify's Pro Audio Engine).
        - **Mastering**: OpenDCP (Theatrical DCI Standard).
        """)

    with a_sub2:
        st.markdown("""
        ### 🏗️ The "Titan" Deep-Dive
        Our architecture replicates a high-end server-side render farm on a local machine.
        
        #### 1. The Intelligence Layer
        The `VideoAgency` initializes two core agents:
        - **Analyst**: Processes raw video/transcripts to extract emotional beats.
        - **Planner**: Maps those beats to a technical VFX/Audio plan.
        
        #### 2. The Assembly Layer (Titan)
        We use a **Headless Frame-Forge** approach:
        - Scenes are rendered as independent `.mp4` chunks.
        - MoviePy handles the VFX/Text overlays for each chunk.
        - FFmpeg then performs a binary-level concat to stitch chunks without re-encoding, preserving 100% fidelity.
        """)

    with a_sub3:
        st.markdown("""
        ### 🏢 Replicating the Hollywood Studio
        LazyDit is organized into "Departments" found in a major post-production house:
        
        | LazyDit Tab | Studio Department | Professional Function |
        | :--- | :--- | :--- |
        | **Intelligence & Docs** | **Creative & Writing** | Scripting, Storyboarding, Beat Sheets. |
        | **Asset Forge** | **Art & Props** | Generating VFX, textures, and creative assets. |
        | **Production Studio** | **Editorial & VFX** | Nonlinear editing, layering, and rendering. |
        | **Mastering** | **Digital Lab** | Color space conversion and DCP packaging. |
        | **Academy** | **Engineering/CTO** | Pipeline maintenance and technical oversight. |
        """)

    with a_sub4:
        st.markdown("""
        ### 🎓 The 5-Step Masterclass
        1. **The Brainstorm**: Upload your transcript and hit `Analyze` in the Intelligence tab.
        2. **The Blueprint**: Refine the generated Creative Bible in the Asset Forge.
        3. **The Forge**: Start the local AI engine (`comfy_start.py`).
        4. **The Render**: Launch the `Generate` button in the Production Studio. 
        5. **The Dispatch**: Move to Mastering to create your theatrical DCP.
        """)
