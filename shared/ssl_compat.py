"""
ssl_compat.py — one canonical place for the Zscaler/ABB TLS workaround.

Why this exists
---------------
On the ABB laptop, Zscaler intercepts TLS. `requests` honours SSL_CERT_FILE /
REQUESTS_CA_BUNDLE, but httpx (used internally by fal_client) builds its own
SSL context and ignores those env vars. The old workaround monkey-patched
httpx to default `verify=False` — which DISABLES certificate verification.
That's a security downgrade, and it must never reach the Hetzner box.

This replaces it. On a machine where ~/combined_cacert.pem exists (the laptop),
point httpx at that bundle so it TRUSTS Zscaler's cert rather than trusting
nothing. On any clean machine (the Hetzner VPS) the bundle is absent, no patch
is applied, and httpx uses normal, correct TLS verification.

Usage
-----
Call once at the very top of any module that uses httpx-based clients
(fal_client), BEFORE those clients are imported/constructed:

    from ssl_compat import trust_zscaler_if_present
    trust_zscaler_if_present()
    import fal_client   # now safe on both laptop and VPS

(`recreation_pipeline.py` / `upload.py` already gate the `requests` side on the
same cert file and need no change. This module is for the httpx side. A future
refactor could route all four files through here — that's a refactor-at-four
item, not today's work.)
"""

import os
from pathlib import Path

_CERT_BUNDLE = Path.home() / "combined_cacert.pem"
_PATCHED = False


def trust_zscaler_if_present() -> bool:
    """If the Zscaler cert bundle exists, make httpx + requests trust it.

    Returns True if the patch was applied (laptop), False on a clean box (VPS).
    Idempotent — safe to call multiple times in one process.
    """
    global _PATCHED
    if _PATCHED:
        return True
    if not _CERT_BUNDLE.exists():
        # Clean machine (Hetzner): default, correct TLS verification. Do nothing.
        return False

    bundle = str(_CERT_BUNDLE)

    # requests and anything that honours these env vars.
    os.environ.setdefault("SSL_CERT_FILE", bundle)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", bundle)

    # httpx ignores those env vars and builds its own context, so patch its
    # clients to DEFAULT verify to the bundle (never False). Callers that pass
    # their own verify= still win, because we only setdefault.
    import httpx

    for _cls in (httpx.Client, httpx.AsyncClient):
        _orig_init = _cls.__init__

        def _make(orig):
            def _patched(self, *args, **kwargs):
                kwargs.setdefault("verify", bundle)
                orig(self, *args, **kwargs)
            return _patched

        _cls.__init__ = _make(_orig_init)

    _PATCHED = True
    return True
