import os
import requests
from tqdm import tqdm

def download_model():
    model_dir = "lazydit/models"
    model_path = os.path.join(model_dir, "gemma-2-2b-it-q4_k_m.gguf")
    url = "https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q4_K_M.gguf?download=true"
    
    print("🎬 PromptForge Rescue: Model Downloader")
    print("-" * 40)
    print("Gemma 2B is a gated model. If the download fails, please visit:")
    print("https://huggingface.co/google/gemma-2b-it and accept the terms.")
    
    token = input("\nEnter your Hugging Face Token (leave blank for public attempt): ").strip()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    os.makedirs(model_dir, exist_ok=True)
    
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}. You likely need a valid HF Token.")
        return

    total_size = int(response.headers.get('content-length', 0))
    
    with open(model_path, "wb") as f, tqdm(
        desc="Downloading Gemma 2B",
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            bar.update(size)

    print(f"\n✅ Ready! Model saved to {model_path}")

if __name__ == "__main__":
    download_model()
