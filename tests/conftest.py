import os
import tempfile

# Must be set before backend.config is imported anywhere.
_TMP = tempfile.mkdtemp(prefix="cs-test-")
os.environ.setdefault("DATA_DIR", _TMP + "/data")
os.environ.setdefault("RUN_DIR", _TMP + "/run")
os.environ.setdefault("USAGE_PLAN_TOKENS", "100000000")
