import requests
import json
import time
import os
import logging

logger = logging.getLogger(__name__)

class ComfyUIClient:
    def __init__(self, base_url="http://localhost:8188", cloud_url=None, cloud_token=None):
        self.local_url = base_url
        self.cloud_url = cloud_url
        self.cloud_token = cloud_token
        self.use_cloud = False

    def get_current_url(self):
        return self.cloud_url if self.use_cloud and self.cloud_url else self.local_url

    def queue_prompt(self, prompt_workflow):
        p = {"prompt": prompt_workflow}
        data = json.dumps(p).encode('utf-8')
        url = self.get_current_url()
        headers = {"Authorization": f"Bearer {self.cloud_token}"} if self.use_cloud else {}
        response = requests.post(f"{url}/prompt", data=data, headers=headers)
        return response.json()

    def get_history(self, prompt_id):
        response = requests.get(f"{self.base_url}/history/{prompt_id}")
        return response.json()

    def wait_for_completion(self, prompt_id, timeout=600):
        start_time = time.time()
        while time.time() - start_time < timeout:
            history = self.get_history(prompt_id)
            if prompt_id in history:
                return history[prompt_id]
            time.sleep(5)
        raise TimeoutError("ComfyUI workflow timed out")

    def _update_workflow_data(self, workflow, input_path):
        """Programmatically injects the input video path into the LoadVideo node."""
        for node_id in workflow:
            node = workflow[node_id]
            if node.get("class_type") == "VideoLinearCFGGuidance" or "Load" in node.get("class_type", ""):
                if "inputs" in node and ("video" in node["inputs"] or "image" in node["inputs"]):
                    # Target common input fields for video/image loading
                    if "video" in node["inputs"]:
                        node["inputs"]["video"] = input_path
                    elif "image" in node["inputs"]:
                        node["inputs"]["image"] = input_path
                    logger.info(f"✅ Injected path into ComfyUI Node {node_id} ({node['class_type']})")
        return workflow

    def download_output(self, prompt_id, output_dir):
        """Fetches the rendered files from the ComfyUI server."""
        history = self.get_history(prompt_id).get(prompt_id, {})
        outputs = history.get("outputs", {})
        
        saved_paths = []
        for node_id in outputs:
            node_output = outputs[node_id]
            if "images" in node_output:
                for img in node_output["images"]:
                    filename = img["filename"]
                    subfolder = img["subfolder"]
                    # Build URL to fetch the file
                    file_url = f"{self.get_current_url()}/view?filename={filename}&subfolder={subfolder}&type={img['type']}"
                    
                    local_path = os.path.join(output_dir, filename)
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Download
                    r = requests.get(file_url, stream=True)
                    if r.status_code == 200:
                        with open(local_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=1024):
                                f.write(chunk)
                        saved_paths.append(local_path)
                        logger.info(f"📥 Downloaded ComfyUI output: {local_path}")
        return saved_paths

    def process_clip(self, input_path, workflow_json, output_dir):
        """
        Executes a full ComfyUI render cycle with automated data injection.
        """
        # 1. Inject input
        updated_workflow = self._update_workflow_data(workflow_json, input_path)
        
        # 2. Queue and Wait
        prompt_res = self.queue_prompt(updated_workflow)
        prompt_id = prompt_res['prompt_id']
        
        logger.info(f"🚀 Queued ComfyUI job: {prompt_id}")
        self.wait_for_completion(prompt_id)
        
        # 3. Download results
        return self.download_output(prompt_id, output_dir)
