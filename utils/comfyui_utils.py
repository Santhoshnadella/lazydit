import requests
import json
import time
import os

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

    def process_clip(self, input_path, workflow_json, output_dir):
        """
        Injects input_path into the workflow JSON and triggers rendering.
        This assumes the workflow has a LoadVideo node that can be targeted.
        """
        # Logic to update workflow JSON with input_path would go here
        # For now, we'll assume the workflow is pre-configured or updated as a template
        prompt_res = self.queue_prompt(workflow_json)
        prompt_id = prompt_res['prompt_id']
        
        print(f"Queued ComfyUI job: {prompt_id}")
        result = self.wait_for_completion(prompt_id)
        
        # Download output logic
        # ...
        return result
