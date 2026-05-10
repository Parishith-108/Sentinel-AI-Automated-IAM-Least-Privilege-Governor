"""
Sentinel-AI Lambda handler (prototype).

This file provides a Lambda handler that:
- Parses an EventBridge event (Access Analyzer finding)
- Extracts the offending policy and CloudTrail clues (pseudo)
- Calls Amazon Bedrock with a system prompt to rewrite the policy
- Commits the fixed policy to a GitHub branch and opens a PR

This is a prototype and contains placeholders where direct AWS/Bedrock/GitHub secrets are required.
"""

import argparse
import json
import os
import tempfile
from datetime import datetime

import requests
import boto3
from botocore.exceptions import ClientError
from github import Github

# Constants
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.txt")


def load_system_prompt():
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def call_bedrock(prompt: str, model_id: str = None) -> str:
    """Call Amazon Bedrock (via boto3) to invoke the model and return model output.

    model_id: optional; if not provided, attempts to read from environment variable BEDROCK_MODEL_ID.
    Falls back to local dummy response if Bedrock call fails or credentials are missing.
    """
    model = model_id or os.environ.get('BEDROCK_MODEL_ID') or 'claude-3.5-sonnet'

    try:
        client = boto3.client('bedrock-runtime')
        payload = json.dumps({"input": prompt})
        # This example uses a generic invoke_model signature; please adjust to your Bedrock SDK version
        resp = client.invoke_model(modelId=model, contentType='application/json', accept='application/json', body=payload)
        # boto3 may return a streaming body depending on SDK; try to read
        body = resp.get('body')
        if hasattr(body, 'read'):
            result = body.read().decode('utf-8')
        else:
            result = resp.get('body')
        return result
    except Exception as e:
        # Graceful fallback for local testing
        print(f"Bedrock call failed or not configured: {e}. Using local dummy response.")
        dummy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:GetObject"],
                    "Resource": ["arn:aws:s3:::example-bucket/specific-prefix/*"]
                }
            ]
        }
        return json.dumps(dummy, indent=2)


def create_github_pr(repo_full_name: str, branch_name: str, file_path: str, file_contents: str, pr_title: str, pr_body: str, token: str):
    g = Github(token)
    repo = g.get_repo(repo_full_name)

    # Create a branch from default branch
    source = repo.get_branch(repo.default_branch)
    try:
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)
    except Exception as e:
        # If branch exists, continue
        print(f"Branch creation skipped or failed: {e}")

    try:
        repo.create_file(path=file_path, message=f"chore: add fixed policy {file_path}", content=file_contents, branch=branch_name)
    except Exception as e:
        # If file exists, update it
        print(f"Create file failed, try update: {e}")
        contents = repo.get_contents(file_path, ref=branch_name)
        repo.update_file(path=file_path, message=f"chore: update fixed policy {file_path}", content=file_contents, sha=contents.sha, branch=branch_name)

    pr = repo.create_pull(title=pr_title, body=pr_body, head=branch_name, base=repo.default_branch)
    return pr.html_url


def lambda_handler(event, context=None):
    # Extract finding - this is a simplified example
    finding = event.get('detail', {})
    policy = finding.get('resource', {}).get('policy') or finding.get('policy') or "{\n}\n"

    system_prompt = load_system_prompt()
    prompt = system_prompt + "\n\n" + "Here is the IAM policy to fix:\n" + json.dumps(policy, indent=2)

    print("Calling Bedrock with prompt length:", len(prompt))
    fixed_policy = call_bedrock(prompt)

    # Create a GitHub PR
    github_repo = os.environ.get('GITHUB_REPO') or 'your-org/your-repo'
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        # Dry-run mode: write the fixed policy to a temp file and return a file URL instead of creating a PR.
        print('GITHUB_TOKEN environment variable not set. Running in dry-run mode; no PR will be created.')
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.json', prefix='fixed-policy-')
        tmp.write(fixed_policy.encode('utf-8'))
        tmp.close()
        pr_url = f"file://{tmp.name}"
    else:
        branch_name = f"sentinel/fix-policy-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        file_path = f"fixed-policies/fixed-policy-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
        pr_title = "chore(security): apply least-privilege policy suggestion"
        pr_body = "This PR was created by Sentinel-AI. Please review the suggested policy changes."

        pr_url = create_github_pr(repo_full_name=github_repo, branch_name=branch_name, file_path=file_path, file_contents=fixed_policy, pr_title=pr_title, pr_body=pr_body, token=github_token)

    return {
        'statusCode': 200,
        'body': json.dumps({'pr_url': pr_url})
    }


def local_test(sample_event_path: str):
    with open(sample_event_path, 'r', encoding='utf-8') as f:
        event = json.load(f)

    # For local testing use GH token from env or prompt
    if 'GITHUB_TOKEN' not in os.environ:
        print('Set GITHUB_TOKEN in environment to actually create PRs. Will proceed in dry-run mode.')

    result = lambda_handler(event)
    print('Result:', result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--local-test', help='Path to sample event JSON to run locally')
    args = parser.parse_args()

    if args.local_test:
        local_test(args.local_test)
    else:
        print('No --local-test provided. To test locally, provide a sample EventBridge event JSON.')
