"""
Hugging Face Model Repository Publisher for Fieldwise.
Publishes the configuration, model card, and metadata to Hugging Face Hub.
"""

import os
import sys

def upload_model_card(repo_id: str, hf_token: str = None):
    token = hf_token or os.getenv("HF_TOKEN")
    if not token:
        print("[Error] HF_TOKEN environment variable not found.")
        print("Please set your Hugging Face write token:")
        print("  set HF_TOKEN=hf_your_token_here (Windows)")
        print("  export HF_TOKEN=hf_your_token_here (Linux/macOS)")
        return False

    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError:
        print("Installing huggingface_hub...")
        os.system("pip install huggingface_hub")
        from huggingface_hub import HfApi, create_repo

    api = HfApi(token=token)
    print(f"Creating/verifying Hugging Face repository '{repo_id}'...")
    create_repo(repo_id=repo_id, repo_type="model", token=token, exist_ok=True)

    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        print(f"Uploading README.md to {repo_id}...")
        api.upload_file(
            path_or_fileobj=readme_path,
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model"
        )
        print(f"Successfully published model card to: https://huggingface.co/{repo_id}")
        return True
    else:
        print(f"[Error] {readme_path} not found.")
        return False


if __name__ == "__main__":
    target_repo = sys.argv[1] if len(sys.argv) > 1 else os.getenv("HF_REPO_ID", "your-username/fieldwise-geoai-slm")
    upload_model_card(target_repo)
