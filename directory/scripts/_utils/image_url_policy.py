from __future__ import annotations

# Shared policy constants used by multiple scripts (`validate.py`, `enrich_images.py`).

DISALLOWED_IMAGE_HOSTS = {
    # GitHub's image proxy URLs are often brittle and not the canonical image source.
    "camo.githubusercontent.com",
}

# Keys are compared case-insensitively.
DISALLOWED_IMAGE_QUERY_KEYS = {
    # AWS SigV4
    "x-amz-algorithm",
    "x-amz-credential",
    "x-amz-date",
    "x-amz-expires",
    "x-amz-signature",
    "x-amz-signedheaders",
    # GCS signed URLs
    "x-goog-algorithm",
    "x-goog-credential",
    "x-goog-date",
    "x-goog-expires",
    "x-goog-signature",
    # CloudFront (common)
    "expires",
    "signature",
    "key-pair-id",
    "policy",
}

