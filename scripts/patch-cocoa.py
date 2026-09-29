#!/usr/bin/env python3
"""Repair duplicate, stale scrollbar updates in the exact 2.40.5 Cocoa sources."""

import hashlib
from pathlib import Path
import re
import sys


def patch(root):
    directory = root / "Source/WebKit/UIProcess/RemoteLayerTree/mac"
    hashes = {
        "Frame": "00f60364f1868ee6e3913bbf2c96f50b1d5cee9235f3cd24aa503f76e32b6f2d",
        "Overflow": "361815bbf2f27826fc01b283d3b99643f88fb9b39bf00b4849c9a9d3611d347a",
    }
    changes = []
    for kind, expected in hashes.items():
        name = f"ScrollingTree{kind}ScrollingNodeRemoteMac"
        path = directory / f"{name}.cpp"
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Unexpected source revision: {path}")
        source = data.decode("utf-8")
        signature = f"bool {name}::commitStateBeforeChildren(const ScrollingStateNode& stateNode)"
        # The base class invokes m_delegate->updateFromStateNode, which already
        # sets the scrollbar host layers and updates the ScrollerPairMac values.
        # These derived classes still refer to the removed m_scrollerPair member.
        replacement = (
            signature + "\n{\n"
            f"    return ScrollingTree{kind}ScrollingNodeMac::commitStateBeforeChildren(stateNode);\n"
            "}"
        )
        result, count = re.subn(re.escape(signature) + r"\n\{.*?\n\}",
                                lambda _: replacement, source, flags=re.DOTALL)
        if count != 1 or "m_scrollerPair" in result:
            raise ValueError(f"Unexpected scrollbar implementation: {path}")
        changes.append((path, result))
    # Validate both inputs before modifying either file.
    for path, result in changes:
        path.write_text(result, encoding="utf-8")
        print(f"Patched {path}")


if __name__ == "__main__":
    patch(Path(sys.argv[1]))
