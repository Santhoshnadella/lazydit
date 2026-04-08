import os
import subprocess
import sys

def launch_comfy():
    print("🎬 Lazydit: Local AI Engine")
    print("-" * 40)
    
    comfy_dir = os.path.join(os.getcwd(), "lazydit", "comfyui")
    main_path = os.path.join(comfy_dir, "main.py")
    
    if not os.path.exists(main_path):
        print("❌ Error: ComfyUI was not found in the project folder.")
        return

    # Use the High-Capacity virtual environment on K:
    interpreter = r"K:\lazydit_venv\Scripts\python.exe"
    
    # Optimization Flags for Laptop Mode
    flags = [
        interpreter,
        main_path,
        "--lowvram",
        "--use-split-cross-attention",
        "--fast",
        "--port", "8188"
    ]
    
    print("\n🚀 Starting ComfyUI with Laptop Optimizations...")
    print(f"Flags: {' '.join(flags[2:])}")
    
    try:
        subprocess.run(flags, cwd=comfy_dir)
    except KeyboardInterrupt:
        print("\n👋 ComfyUI Stopped.")

if __name__ == "__main__":
    launch_comfy()
