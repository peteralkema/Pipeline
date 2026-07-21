#!/usr/bin/env python3
"""patch_build_lego_probe_verb.py

Retire the probe-as-conversation problem permanently. Three edits to build_lego.py:

 1. Replace the whole cmd_stills region (drifted -- duplicate lines, stale
    comments -- from mid-session patching) with CLEAN canonical code:
      - shared _stills_render core (block-prefixed filenames option, G57 fix)
      - cmd_stills: block mode (grid-bNN, unchanged names -> pick/place safe) OR
        beats=b/c cross-film sample (grid-probe, block-prefixed -> no collisions)
      - cmd_probe: SELF-SELECTING. `probe [N]` auto-picks one beat per canon token
        (doubling the fail-hardest), spread across blocks, renders, prints the
        verdict card. Zero numbering decisions.
 2. Register "probe" in CMDS.
 3. main(): parse_args -> parse_known_args so argument ORDER never matters (G53).

Locates cmd_stills by boundary and swaps the whole span -- robust to drift.
Idempotent, .pre_ backup, py_compile before write, ASCII-only.

    cd ~/Projects/Pipeline
    python3 shared/patch_build_lego_probe_verb.py
"""
import argparse, base64, os, re, sys, py_compile, tempfile

CANON = base64.b64decode("ZGVmIF9zdGlsbHNfcmVuZGVyKGNmZywgYnJvd3MsIG91dF9kaXIsIHByZWZpeF9ibG9jaywgbGFiZWwpOgogICAgIiIiUmVuZGVyIHRoZSA0LXZhcmlhbnQgcGljay1zZXQgZm9yIGEgbGlzdCBvZiByb3dzIGludG8gb3V0X2Rpci4KCiAgICBQZXIgYmVhdDogNCByZWFsIHJlLXJvbGxzIGlmIGhlcm8sIGVsc2UgMiByZWFsICsgMiBza2lwLXRpbGVzLiBGaWxlbmFtZXMgYXJlCiAgICB7Y2xpcDowM2R9LXt2OjAyZH0ucG5nIG5vcm1hbGx5LCBvciB7YmxvY2s6MDJkfS17Y2xpcDowM2R9LXt2OjAyZH0ucG5nIHdoZW4KICAgIHByZWZpeF9ibG9jayBpcyBUcnVlIChjcm9zcy1maWxtIHByb2JlIC0tIGNsaXBfaW5kZXggcmVwZWF0cyBhY3Jvc3MgYmxvY2tzIGFuZAogICAgd291bGQgY29sbGlkZSkuIFJlc3VtZS1zYWZlLiBSZXR1cm5zIChyZWFsX2NvdW50LCBpbmRleF9yb3dzKS4KICAgICIiIgogICAgaW1wb3J0IHJlIGFzIF9yZSwgc2h1dGlsIGFzIF9zaAogICAgY2Fub24gPSBjYW5vbl9vZihjZmcpCiAgICBzaGFyZWQgPSBQYXRoKGNmZ1siX2NoYW5uZWxfZGlyIl0pLnBhcmVudCAvICJzaGFyZWQiCiAgICBzeXMucGF0aC5pbnNlcnQoMCwgc3RyKHNoYXJlZCkpCiAgICB0cnk6CiAgICAgICAgaW1wb3J0IHJlY3JlYXRpb25fcGlwZWxpbmUgYXMgcnAKICAgIGV4Y2VwdCBFeGNlcHRpb24gYXMgZToKICAgICAgICByYWlzZSBTeXN0ZW1FeGl0KCJjYW5ub3QgaW1wb3J0IHJlY3JlYXRpb25fcGlwZWxpbmUgZnJvbSAlczogJXMiICUgKHNoYXJlZCwgZSkpCiAgICByZWZfbW9kZSA9IGNmZy5nZXQoInJlbmRlcl9tb2RlIikgPT0gInJlZmVyZW5jZSIKICAgIHJlZl9tYXAgPSBjZmcuZ2V0KCJyZWZlcmVuY2VfbWFwIiwge30pIGlmIHJlZl9tb2RlIGVsc2Uge30KICAgIHJlZl9jaGRpciA9IFBhdGgoY2ZnWyJfY2hhbm5lbF9kaXIiXSkKICAgIF9zaGFyZWRfc2tpcCA9IHNoYXJlZCAvICJfc2tpcC5wbmciCiAgICBfY2hhbl9za2lwID0gcmVmX2NoZGlyIC8gImNoYXJhY3RlcnMiIC8gIl9za2lwLnBuZyIKICAgIHNraXBfdGlsZSA9IF9jaGFuX3NraXAgaWYgX2NoYW5fc2tpcC5leGlzdHMoKSBlbHNlIF9zaGFyZWRfc2tpcAogICAgb3V0X2Rpci5ta2RpcihwYXJlbnRzPVRydWUsIGV4aXN0X29rPVRydWUpCiAgICBpbmRleCA9IFtdCiAgICByZWFsID0gMAogICAgZm9yIHIgaW4gYnJvd3M6CiAgICAgICAgYiA9IGludChyWyJibG9ja19pZCJdKTsgY2kgPSBpbnQoclsiY2xpcF9pbmRleCJdKQogICAgICAgIHJhdyA9IHJbInBoZW5vbWVub24iXS5zdHJpcCgpCiAgICAgICAgcHJvbXB0ID0gcnAuX2V4cGFuZF9jYW5vbihyYXcsIGNhbm9uKQogICAgICAgIHJlZnMgPSBbXQogICAgICAgIGlmIHJlZl9tb2RlOgogICAgICAgICAgICBzZWVuID0gc2V0KCkKICAgICAgICAgICAgZm9yIHQgaW4gX3JlLmZpbmRhbGwociJceyhbYS16QS1aX11bYS16QS1aMC05X10qKVx9IiwgcmF3KToKICAgICAgICAgICAgICAgIGlmIHQgaW4gcmVmX21hcCBhbmQgdCBub3QgaW4gc2VlbjoKICAgICAgICAgICAgICAgICAgICBzZWVuLmFkZCh0KQogICAgICAgICAgICAgICAgICAgIGVudHJ5ID0gcmVmX21hcFt0XQogICAgICAgICAgICAgICAgICAgIGZvciBmIGluIChlbnRyeSBpZiBpc2luc3RhbmNlKGVudHJ5LCBsaXN0KSBlbHNlIFtlbnRyeV0pOgogICAgICAgICAgICAgICAgICAgICAgICByZWZzLmFwcGVuZChzdHIocmVmX2NoZGlyIC8gZikpCiAgICAgICAgbl9yZWFsID0gNCBpZiByWyJ3ZWlnaHQiXSA9PSAiaGVybyIgZWxzZSAyCiAgICAgICAgZm9yIHYgaW4gcmFuZ2UoMSwgNSk6CiAgICAgICAgICAgIG5hbWUgPSAoIiUwMmQtJTAzZC0lMDJkLnBuZyIgJSAoYiwgY2ksIHYpKSBpZiBwcmVmaXhfYmxvY2sgZWxzZSAoIiUwM2QtJTAyZC5wbmciICUgKGNpLCB2KSkKICAgICAgICAgICAgb3V0ID0gb3V0X2RpciAvIG5hbWUKICAgICAgICAgICAgaW5kZXguYXBwZW5kKChiLCBjaSwgdiwgInJlYWwiIGlmIHYgPD0gbl9yZWFsIGVsc2UgInNraXAiLCBuYW1lKSkKICAgICAgICAgICAgaWYgb3V0LmV4aXN0cygpOgogICAgICAgICAgICAgICAgY29udGludWUKICAgICAgICAgICAgaWYgdiA8PSBuX3JlYWw6CiAgICAgICAgICAgICAgICB0YWcgPSAoIltyZWY6JWRdICIgJSBsZW4ocmVmcykpIGlmIHJlZnMgZWxzZSAiIgogICAgICAgICAgICAgICAgcHJpbnQoIiAgWyVkLyVkIHYlZF0gJXMlcy4uLiIgJSAoYiwgY2ksIHYsIHRhZywgcHJvbXB0Wzo1MF0pKQogICAgICAgICAgICAgICAgcnAuZ2VuZXJhdGVfc3RpbGwocHJvbXB0LCBvdXQsIHJlZmVyZW5jZV9pbWFnZXM9KHJlZnMgb3IgTm9uZSkpCiAgICAgICAgICAgICAgICByZWFsICs9IDEKICAgICAgICAgICAgZWxzZToKICAgICAgICAgICAgICAgIGlmIHNraXBfdGlsZS5leGlzdHMoKToKICAgICAgICAgICAgICAgICAgICBfc2guY29weShza2lwX3RpbGUsIG91dCkKICAgICAgICAgICAgICAgIGVsc2U6CiAgICAgICAgICAgICAgICAgICAgb3V0LndyaXRlX2J5dGVzKGIiIikKICAgIHJldHVybiByZWFsLCBpbmRleAoKCmRlZiBfd3JpdGVfZ3JpZF9pbmRleChncmlkLCBpbmRleCk6CiAgICB3aXRoIG9wZW4oZ3JpZCAvICJHUklELUlOREVYLmNzdiIsICJ3IiwgbmV3bGluZT0iIikgYXMgZjoKICAgICAgICB3ID0gY3N2LndyaXRlcihmKQogICAgICAgIHcud3JpdGVyb3coWyJibG9ja19pZCIsICJjbGlwX2luZGV4IiwgInZhcmlhbnQiLCAia2luZCIsICJmaWxlIl0pCiAgICAgICAgdy53cml0ZXJvd3MoaW5kZXgpCgoKZGVmIGNtZF9zdGlsbHMoY2ZnLCBhcmd2KToKICAgICIiIlJlbmRlciB0aGUgdmFyaWFudCBncmlkLgoKICAgICAgYnVpbGRfbGVnby5weSBzdGlsbHMgLS1wcm9qZWN0IFAgW0JMT0NLIC4uLl0gICAgICMgd2hvbGUgYmxvY2socykgLT4gZ3JpZC1iTk4KICAgICAgYnVpbGRfbGVnby5weSBzdGlsbHMgYmVhdHM9MS8xLDIvMyAtLXByb2plY3QgUCAgICMgY3Jvc3MtZmlsbSBzYW1wbGUgLT4gZ3JpZC1wcm9iZQogICAgIiIiCiAgICByb3dzID0gbG9hZF9tYXN0ZXIoY2ZnKQogICAgaWYgbm90IGhhc19jb2wocm93cywgInBoZW5vbWVub24iKToKICAgICAgICByYWlzZSBTeXN0ZW1FeGl0KCJzdGlsbHMgbmVlZHMgYSAncGhlbm9tZW5vbicgY29sdW1uIC0tIGF1dGhvciBmaXJzdC4iKQogICAgcHJvaiA9IFBhdGgoY2ZnWyJfcHJvamVjdF9kaXIiXSkKICAgIGJlYXRzID0gTm9uZQogICAgZm9yIGEgaW4gbGlzdChhcmd2KToKICAgICAgICBpZiBhLnN0YXJ0c3dpdGgoImJlYXRzPSIpOgogICAgICAgICAgICBiZWF0cyA9IHNldCgpCiAgICAgICAgICAgIGZvciB0b2sgaW4gYS5zcGxpdCgiPSIsIDEpWzFdLnNwbGl0KCIsIik6CiAgICAgICAgICAgICAgICB0b2sgPSB0b2suc3RyaXAoKQogICAgICAgICAgICAgICAgaWYgbm90IHRvazoKICAgICAgICAgICAgICAgICAgICBjb250aW51ZQogICAgICAgICAgICAgICAgaWYgIi8iIG5vdCBpbiB0b2s6CiAgICAgICAgICAgICAgICAgICAgcmFpc2UgU3lzdGVtRXhpdCgiYmVhdHM9IG5lZWRzIGJsb2NrL2NsaXAgcGFpcnMsIGUuZy4gYmVhdHM9MS8xLDIvMyIpCiAgICAgICAgICAgICAgICBiYiwgY2MgPSB0b2suc3BsaXQoIi8iLCAxKQogICAgICAgICAgICAgICAgYmVhdHMuYWRkKChpbnQoYmIpLCBpbnQoY2MpKSkKICAgICAgICAgICAgYXJndiA9IFt4IGZvciB4IGluIGFyZ3YgaWYgeCAhPSBhXQogICAgICAgICAgICBicmVhawogICAgaWYgYmVhdHMgaXMgbm90IE5vbmU6CiAgICAgICAgaGF2ZSA9IHsoaW50KHJbImJsb2NrX2lkIl0pLCBpbnQoclsiY2xpcF9pbmRleCJdKSkgZm9yIHIgaW4gcm93c30KICAgICAgICBvb2IgPSBzb3J0ZWQocCBmb3IgcCBpbiBiZWF0cyBpZiBwIG5vdCBpbiBoYXZlKQogICAgICAgIGlmIG9vYjoKICAgICAgICAgICAgcmFpc2UgU3lzdGVtRXhpdCgiYmVhdHM9IG5vdCBpbiBtYXN0ZXI6ICIgKyAiLCAiLmpvaW4oIiVkLyVkIiAlIHAgZm9yIHAgaW4gb29iKSkKICAgICAgICBicm93cyA9IFtyIGZvciByIGluIHJvd3MgaWYgKGludChyWyJibG9ja19pZCJdKSwgaW50KHJbImNsaXBfaW5kZXgiXSkpIGluIGJlYXRzXQogICAgICAgIHJlYWwsIGluZGV4ID0gX3N0aWxsc19yZW5kZXIoY2ZnLCBicm93cywgcHJvaiAvICJncmlkLXByb2JlIiwgVHJ1ZSwgInByb2JlIikKICAgICAgICBfd3JpdGVfZ3JpZF9pbmRleChwcm9qIC8gImdyaWQtcHJvYmUiLCBpbmRleCkKICAgICAgICBwcmludCgiICBwcm9iZTogJWQgYmVhdHMgLT4gJXMgfCAlZCByZWFsIHN0aWxscyAoJCUuMmYpIiAlIChsZW4oYnJvd3MpLCBwcm9qIC8gImdyaWQtcHJvYmUiLCByZWFsLCByZWFsICogMC4wOCkpCiAgICAgICAgcmV0dXJuCiAgICB3YW50ZWQgPSBbaW50KGEpIGZvciBhIGluIGFyZ3ZdIG9yIHNvcnRlZCh7aW50KHJbImJsb2NrX2lkIl0pIGZvciByIGluIHJvd3N9KQogICAgZm9yIGJsb2NrIGluIHdhbnRlZDoKICAgICAgICBicm93cyA9IFtyIGZvciByIGluIHJvd3MgaWYgaW50KHJbImJsb2NrX2lkIl0pID09IGJsb2NrXQogICAgICAgIGdlcnJzID0gZ2F0ZV9ibG9jayhicm93cywgY2ZnLCBsb2FkX2Jhbm5lZChjZmcpKQogICAgICAgIGlmIGdlcnJzOgogICAgICAgICAgICBwcmludCgiXG4iLmpvaW4oIiAgR0FURSBGQUlMOiAiICsgZSBmb3IgZSBpbiBnZXJycykpOyByYWlzZSBTeXN0ZW1FeGl0KDEpCiAgICAgICAgZ3JpZCA9IHByb2ogLyAoImdyaWQtYiUwMmQiICUgYmxvY2spCiAgICAgICAgcmVhbCwgaW5kZXggPSBfc3RpbGxzX3JlbmRlcihjZmcsIGJyb3dzLCBncmlkLCBGYWxzZSwgImJsb2NrICVkIiAlIGJsb2NrKQogICAgICAgIF93cml0ZV9ncmlkX2luZGV4KGdyaWQsIGluZGV4KQogICAgICAgIHByaW50KCIgIGJsb2NrICVkOiBncmlkIC0+ICVzIHwgJWQgcmVhbCBzdGlsbHMgKCQlLjJmKSB8IEdSSUQtSU5ERVguY3N2IiAlIChibG9jaywgZ3JpZCwgcmVhbCwgcmVhbCAqIDAuMDgpKQogICAgcHJpbnQoIlxuTkVYVDogcmV2aWV3IGVhY2ggZ3JpZCBmb2xkZXIsIHByb21vdGUgT05FIHdpbm5lciBwZXIgYmVhdCB0byBzaG90X05OTi5wbmcgKHRoZSBwaWNrKS4iKQoKClBST0JFX1BSSU9SSVRZID0gKCJ3aXRuZXNzIiwgImRlc2NlbnQiLCAibGV2aWF0aGFuIiwgInJlbW5hbnQiLCAiZGVlcCIsICJjb2RleCIpCgpkZWYgX3ByaW1hcnlfdG9rZW4ocGhlbm9tZW5vbik6CiAgICBtID0gcmUubWF0Y2gociJccypceyhbYS16QS1aX11bYS16QS1aMC05X10qKVx9IiwgcGhlbm9tZW5vbiBvciAiIikKICAgIHJldHVybiBtLmdyb3VwKDEpIGlmIG0gZWxzZSBOb25lCgpkZWYgY21kX3Byb2JlKGNmZywgYXJndik6CiAgICAiIiJTZWxmLXNlbGVjdGluZyB2aXN1YWwgcHJvYmUgLS0gTk8gbnVtYmVyaW5nIGRlY2lzaW9ucy4KCiAgICAgIGJ1aWxkX2xlZ28ucHkgcHJvYmUgLS1wcm9qZWN0IFAgICAgICAgICMgMjAtYmVhdCByZWdpc3RlciBzcHJlYWQKICAgICAgYnVpbGRfbGVnby5weSBwcm9iZSAzMCAtLXByb2plY3QgUCAgICAgIyBOLWJlYXQgc3ByZWFkCgogICAgUGlja3Mgb25lIGJlYXQgcGVyIGNhbm9uIHRva2VuIHByZXNlbnQgKGRvdWJsaW5nIHRoZSBmYWlsLWhhcmRlc3QgdG9rZW5zKSwKICAgIHNwcmVhZCBhY3Jvc3MgYmxvY2tzLCByZW5kZXJzIHRoZSA0LXZhcmlhbnQgZ3JpZCBpbnRvIGdyaWQtcHJvYmUsIHByaW50cyB0aGUKICAgIHZlcmRpY3QgY2FyZC4gQmxvY2stcHJlZml4ZWQgZmlsZW5hbWVzIC0tIG5ldmVyIGNvbGxpZGVzLgogICAgIiIiCiAgICBuID0gMjAKICAgIGZvciBhIGluIGFyZ3Y6CiAgICAgICAgaWYgYS5pc2RpZ2l0KCk6CiAgICAgICAgICAgIG4gPSBpbnQoYSk7IGJyZWFrCiAgICByb3dzID0gbG9hZF9tYXN0ZXIoY2ZnKQogICAgaWYgbm90IGhhc19jb2wocm93cywgInBoZW5vbWVub24iKToKICAgICAgICByYWlzZSBTeXN0ZW1FeGl0KCJwcm9iZSBuZWVkcyBhICdwaGVub21lbm9uJyBjb2x1bW4gLS0gYXV0aG9yIGZpcnN0LiIpCiAgICBieV90b2sgPSB7fQogICAgZm9yIHIgaW4gcm93czoKICAgICAgICB0ID0gX3ByaW1hcnlfdG9rZW4oclsicGhlbm9tZW5vbiJdKQogICAgICAgIGlmIHQ6CiAgICAgICAgICAgIGJ5X3Rvay5zZXRkZWZhdWx0KHQsIFtdKS5hcHBlbmQocikKICAgIGZvciB0IGluIGJ5X3RvazoKICAgICAgICBieV90b2tbdF0uc29ydChrZXk9bGFtYmRhIHI6IChpbnQoclsiYmxvY2tfaWQiXSksIGludChyWyJjbGlwX2luZGV4Il0pKSkKICAgIHRva2VucyA9IHNvcnRlZChieV90b2spCiAgICBpZiBub3QgdG9rZW5zOgogICAgICAgIHJhaXNlIFN5c3RlbUV4aXQoInByb2JlOiBubyBjYW5vbiB0b2tlbnMgZm91bmQgaW4gcGhlbm9tZW5hLiIpCgogICAgZGVmIF9zcHJlYWQobHN0LCBrKToKICAgICAgICBrID0gbWluKGssIGxlbihsc3QpKQogICAgICAgIGlmIGsgPD0gMDoKICAgICAgICAgICAgcmV0dXJuIFtdCiAgICAgICAgaWYgayA9PSAxOgogICAgICAgICAgICByZXR1cm4gW2xzdFtsZW4obHN0KSAvLyAyXV0KICAgICAgICBzdGVwID0gKGxlbihsc3QpIC0gMSkgLyAoayAtIDEpCiAgICAgICAgcmV0dXJuIFtsc3Rbcm91bmQoaSAqIHN0ZXApXSBmb3IgaSBpbiByYW5nZShrKV0KCiAgICBwaWNrcyA9IFtdCiAgICBzZWVuID0gc2V0KCkKICAgIGZvciB0IGluIHRva2VuczoKICAgICAgICB3YW50ID0gMiBpZiB0IGluIFBST0JFX1BSSU9SSVRZIGVsc2UgMQogICAgICAgIGZvciByIGluIF9zcHJlYWQoYnlfdG9rW3RdLCB3YW50KToKICAgICAgICAgICAga2V5ID0gKGludChyWyJibG9ja19pZCJdKSwgaW50KHJbImNsaXBfaW5kZXgiXSkpCiAgICAgICAgICAgIGlmIGtleSBub3QgaW4gc2VlbjoKICAgICAgICAgICAgICAgIHNlZW4uYWRkKGtleSk7IHBpY2tzLmFwcGVuZChyKQogICAgb3JkZXIgPSBbdCBmb3IgdCBpbiBQUk9CRV9QUklPUklUWSBpZiB0IGluIGJ5X3Rva10gKyBbdCBmb3IgdCBpbiB0b2tlbnMgaWYgdCBub3QgaW4gUFJPQkVfUFJJT1JJVFldCiAgICBpID0gMgogICAgd2hpbGUgbGVuKHBpY2tzKSA8IG46CiAgICAgICAgYWRkZWQgPSBGYWxzZQogICAgICAgIGZvciB0IGluIG9yZGVyOgogICAgICAgICAgICBpZiBsZW4ocGlja3MpID49IG46CiAgICAgICAgICAgICAgICBicmVhawogICAgICAgICAgICBmb3IgciBpbiBfc3ByZWFkKGJ5X3Rva1t0XSwgaSk6CiAgICAgICAgICAgICAgICBrZXkgPSAoaW50KHJbImJsb2NrX2lkIl0pLCBpbnQoclsiY2xpcF9pbmRleCJdKSkKICAgICAgICAgICAgICAgIGlmIGtleSBub3QgaW4gc2VlbjoKICAgICAgICAgICAgICAgICAgICBzZWVuLmFkZChrZXkpOyBwaWNrcy5hcHBlbmQocik7IGFkZGVkID0gVHJ1ZTsgYnJlYWsKICAgICAgICBpICs9IDEKICAgICAgICBpZiBub3QgYWRkZWQ6CiAgICAgICAgICAgIGJyZWFrCiAgICBwaWNrcy5zb3J0KGtleT1sYW1iZGEgcjogKGludChyWyJibG9ja19pZCJdKSwgaW50KHJbImNsaXBfaW5kZXgiXSkpKQogICAgcGlja3MgPSBwaWNrc1s6bl0KCiAgICBwcm9qID0gUGF0aChjZmdbIl9wcm9qZWN0X2RpciJdKQogICAgcmVhbCwgaW5kZXggPSBfc3RpbGxzX3JlbmRlcihjZmcsIHBpY2tzLCBwcm9qIC8gImdyaWQtcHJvYmUiLCBUcnVlLCAicHJvYmUiKQogICAgX3dyaXRlX2dyaWRfaW5kZXgocHJvaiAvICJncmlkLXByb2JlIiwgaW5kZXgpCiAgICBzZWwgPSAiLCAiLmpvaW4oIiVkLyVkIiAlIChpbnQoclsiYmxvY2tfaWQiXSksIGludChyWyJjbGlwX2luZGV4Il0pKSBmb3IgciBpbiBwaWNrcykKICAgIG5ibG9ja3MgPSBsZW4oe2ludChyWyJibG9ja19pZCJdKSBmb3IgciBpbiBwaWNrc30pCiAgICBwcmludCgiXG4gIHByb2JlOiAlZCBiZWF0cyBhY3Jvc3MgJWQgYmxvY2tzIC0+ICVzIiAlIChsZW4ocGlja3MpLCBuYmxvY2tzLCBwcm9qIC8gImdyaWQtcHJvYmUiKSkKICAgIHByaW50KCIgIGJlYXRzOiAlcyIgJSBzZWwpCiAgICBwcmludCgiICAlZCByZWFsIHN0aWxscyAoJCUuMmYpIiAlIChyZWFsLCByZWFsICogMC4wOCkpCiAgICBwcmludCgiXG4gIFZFUkRJQ1QgQ0FSRCAtLSBleWViYWxsIGJlZm9yZSB0aGUgJDcxIGdyaWQ6IikKICAgIHByaW50KCIgICAgd2l0bmVzcyAgIDogZHJhcGVkLCBhdXN0ZXJlLCBzdGF0dWVzcXVlIC0tIE5PVCBzZXh1YWxpc2VkIikKICAgIHByaW50KCIgICAgZGVzY2VudCAgIDogc29saWQsIG9wYXF1ZSwgaGFyZCBzaGFkb3cgLS0gTk9UIGdsb3dpbmcvdHJhbnNsdWNlbnQiKQogICAgcHJpbnQoIiAgICBsZXZpYXRoYW4gOiBtYXNzaXZlLCBicmlnaHQtbGl0IGRlZXAgLS0gTk9UIG11cmsiKQogICAgcHJpbnQoIiAgICByZW1uYW50ICAgOiBnaWFudCB2cyB0aW55IGh1bWFuIC0tIHNjYWxlIHJlYWRzIikKICAgIHByaW50KCIgICAgZGVlcCAgICAgIDogZm9yZWdyb3VuZCBhbmNob3IgcmVhZHMgYWdhaW5zdCB0aGUgZGVwdGgiKQogICAgcHJpbnQoIiAgICBjb2RleCAgICAgOiBtb251bWVudGFsIGJvb2sgLS0gTk8gc2Nyb2xsLCBOTyBsZWN0ZXJuIikKICAgIHByaW50KCIgICAgcmVsaWVmICAgIDogc2hhcnAgY2FydmVkIHN0b25lLCBicmlnaHQgLS0gTk8gbXVyayIpCiAgICBwcmludCgiICBzcGVsbC1icmVha2VyczogdGV4dCwgd2F0ZXJtYXJrcywgZXh0cmEgbGltYnMsIG1vZGVybiBvYmplY3RzLiIp").decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=None)
    args = ap.parse_args()
    if args.target:
        target = os.path.abspath(args.target)
    else:
        d = os.path.abspath(os.getcwd()); root = None
        while d != os.path.dirname(d):
            if os.path.isdir(os.path.join(d, ".git")): root = d; break
            d = os.path.dirname(d)
        if not root:
            sys.stderr.write("ERROR: no .git; pass --target\n"); sys.exit(1)
        target = os.path.join(root, "build_lego.py")
    if not os.path.isfile(target):
        sys.stderr.write("ERROR: not found: %s\n" % target); sys.exit(1)
    src = open(target, encoding="utf-8").read()
    orig = src

    if "def cmd_probe(" in src:
        print("skip (already applied): canonical stills+probe")
    else:
        pat = re.compile(r"def cmd_stills\(cfg, argv\):.*?(?=\n# -{5,} clips )", re.DOTALL)
        m = pat.search(src)
        if not m:
            sys.stderr.write("ERROR: could not locate cmd_stills..clips-header region -- ABORT.\n"); sys.exit(1)
        if len(pat.findall(src)) != 1:
            sys.stderr.write("ERROR: cmd_stills region matched more than once -- ABORT.\n"); sys.exit(1)
        src = src[:m.start()] + CANON + "\n\n" + src[m.end():]
        print("applied: canonical stills+probe region")

    if '"probe": cmd_probe' in src:
        print("skip (already applied): CMDS probe entry")
    else:
        anchor = '"stills": cmd_stills,'
        if anchor not in src:
            sys.stderr.write("ERROR: CMDS stills anchor not found -- ABORT.\n"); sys.exit(1)
        src = src.replace(anchor, anchor + ' "probe": cmd_probe,', 1)
        print("applied: CMDS probe entry")

    if "parse_known_args" in src:
        print("skip (already applied): parse_known_args")
    else:
        old = ("    args = ap.parse_args()\n"
               "    cfg = load_config(args.project)\n"
               "    CMDS[args.command](cfg, args.rest)")
        new = ("    args, _extra = ap.parse_known_args()\n"
               "    rest = list(args.rest) + list(_extra)\n"
               "    cfg = load_config(args.project)\n"
               "    CMDS[args.command](cfg, rest)")
        if old not in src:
            sys.stderr.write("ERROR: main() parse_args block not found -- ABORT.\n"); sys.exit(1)
        src = src.replace(old, new, 1)
        print("applied: parse_known_args")

    if src == orig:
        print("no changes."); return
    if any(ord(c) > 127 for c in CANON):
        sys.stderr.write("ERROR: non-ASCII in canonical block\n"); sys.exit(1)

    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    tmp.write(src); tmp.close()
    try:
        py_compile.compile(tmp.name, doraise=True)
    except py_compile.PyCompileError as e:
        sys.stderr.write("ERROR: patched source fails to compile -- ABORT:\n%s\n" % e)
        os.unlink(tmp.name); sys.exit(1)
    os.unlink(tmp.name)

    bak = target + ".pre_probeverb"
    if not os.path.exists(bak):
        open(bak, "w", encoding="utf-8").write(orig); print("backup:", bak)
    open(target, "w", encoding="utf-8").write(src)
    print("OK: build_lego.py now has a self-selecting `probe` verb. py_compile passed.")


if __name__ == "__main__":
    main()
