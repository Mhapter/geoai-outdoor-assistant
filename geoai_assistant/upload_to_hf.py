"""
Hugging Face Hub Sync Script for Deliverable #2
GeoAI Hackathon @ CSRE, IIT Bombay

Usage:
  python upload_to_hf.py --repo-id <your-hf-username>/geoai-slm-qwen2.5-3b --token <hf_token>
"""

import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Upload GeoAI Model Card & Config to Hugging Face Hub")
    parser.add_argument("--repo-id", type=str, required=True, help="HF Repo ID, e.g. username/geoai-slm-qwen2.5-3b")
    parser.add_argument("--token", type=str, default=os.getenv("HF_TOKEN"), help="Hugging Face API Token")
    args = parser.parse_args()

    if not args.token:
        print("ERROR: Hugging Face token is required. Pass --token <hf_token> or set HF_TOKEN environment variable.")
        sys.exit(1)

    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError:
        print("ERROR: huggingface_hub package not installed. Run: pip install huggingface-hub")
        sys.exit(1)

    api = HfApi(token=args.token)
    print(f"Creating / verifying Hugging Face repository '{args.repo_id}'...")
    create_repo(repo_id=args.repo_id, token=args.token, repo_type="model", exist_ok=True)

    here = os.path.dirname(os.path.abspath(__file__))
    card_dir = os.path.join(here, "hf_model_card")

    print(f"Uploading model card and metadata from {card_dir} to {args.repo_id}...")
    api.upload_folder(
        folder_path=card_dir,
        repo_id=args.repo_id,
        repo_type="model",
        commit_message="Add GeoAI Outdoor Intelligence Model Card & config (CSRE IIT Bombay)"
    )

    print("\n✅ Successfully published model repository to Hugging Face Hub!")
    print(f"   URL: https://huggingface.co/{args.repo_id}")

if __name__ == "__main__":
    main()
