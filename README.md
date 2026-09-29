# WebKit 2.40.5 for macOS Monterey

Manually dispatched GitHub Actions build of the **native macOS port** at
`webkitgtk-2.40.5` (`817d67af2ed9204a3a3be6750a06ac5425c9fe00`).
2.40.5 is a WebKitGTK release number, not an Apple WebKit framework version.
This does not build GTK for macOS or replace Safari/system WebKit.

The workflow uses the hosted `macos-14` runner with Xcode 15.0.1 and system Ruby
(the historical scripts require `File.exists?`, removed in Ruby 3.2+), targets
macOS **12.0 (Monterey)**, and builds **x86_64** frameworks and MiniBrowser.
Apple Silicon native binaries are not included. Products are unsigned development
builds, not notarized applications. A deployment-target check is not a runtime
compatibility test: execution on Monterey must be verified separately.

Debug information generation is disabled (`GCC_GENERATE_DEBUGGING_SYMBOLS=NO`,
`DEBUG_INFORMATION_FORMAT=dwarf` to avoid dSYM generation). Packaging additionally
strips debug symbols from Mach-O binaries and static archives with `strip -S`
and excludes any dSYM bundles. Runtime/export symbols and Release optimization
are preserved; source-level debugging and crash symbolication are unavailable.

The build sets `ENABLE_THREADED_ANIMATION_RESOLUTION=0`: this GTK release tag
enables the feature on Cocoa but calls the absent
`KeyframeEffect::threadedAnimationResolutionEnabled()` method.
`scripts/patch-cocoa.py` also removes stale, duplicate scrollbar updates from
two remote scrolling nodes: the base classes already perform those updates
through their delegates. The patch checks both source hashes before editing.
The exact source diff and its checksum are included in the products and logs.
These are compatibility-modified builds, not pristine upstream binaries.

## Run and download with `gh`

```sh
gh workflow run build-webkit.yml --repo ruiwai/webkit-build --ref main
gh run list --repo ruiwai/webkit-build --workflow build-webkit.yml
gh run watch RUN_ID --repo ruiwai/webkit-build --exit-status
gh run download RUN_ID --repo ruiwai/webkit-build \
  --name webkit-2.40.5-macos-monterey-x86_64 --dir artifacts
cd artifacts
shasum -a 256 -c SHA256SUMS
tar -xzf webkit-2.40.5-macos-monterey-x86_64.tar.gz
```

Artifacts expire after 14 days. The archive preserves framework symlinks and
executable permissions and contains the Release products and build provenance.
Build logs are uploaded even if compilation fails; a logs artifact alone is
**not** a successful WebKit build. No binary is uploaded unless compilation and
the framework/MiniBrowser architecture and deployment-target checks pass.

This historical release lacks subsequent security fixes. Do not use it for
untrusted browsing.
