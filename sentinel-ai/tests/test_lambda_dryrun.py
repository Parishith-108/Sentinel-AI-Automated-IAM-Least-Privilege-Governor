import json
import os
import sys
import tempfile

# Ensure project root is on sys.path so tests can import iam_logic
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from iam_logic import lambda_handler, call_bedrock


def test_call_bedrock_dummy():
    out = call_bedrock("test prompt that cannot be sent to bedrock")
    assert isinstance(out, str)
    assert 'Version' in out or out.strip().startswith('{')


def test_lambda_dryrun_writes_file(tmp_path, monkeypatch):
    sample_event = {
        "detail": {
            "resource": {
                "policy": {"Statement": []}
            }
        }
    }

    # Ensure no GITHUB_TOKEN in env
    monkeypatch.delenv('GITHUB_TOKEN', raising=False)

    res = lambda_handler(sample_event)
    body = json.loads(res['body'])
    assert 'pr_url' in body
    assert body['pr_url'].startswith('file://')