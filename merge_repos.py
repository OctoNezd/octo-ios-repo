#!/usr/bin/env python3
"""
AltStore Repository Merger
Merges multiple AltStore manifest files into a single repository.
"""

import json
import urllib.request
import sys
from typing import Dict, List, Any


def fetch_manifest(url: str) -> Dict[str, Any]:
    """
    Fetch an AltStore manifest from a URL.
    
    Args:
        url: The URL to fetch the manifest from
        
    Returns:
        The parsed JSON manifest as a dictionary
    """
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            return json.loads(data)
    except urllib.error.URLError as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        raise
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {url}: {e}", file=sys.stderr)
        raise


def merge_manifests(manifests: List[Dict[str, Any]], output_name: str = "Repository") -> Dict[str, Any]:
    """
    Merge multiple AltStore manifests into one.
    
    Args:
        manifests: List of manifest dictionaries to merge
        output_name: Name for the merged repository
        
    Returns:
        A merged manifest dictionary
    """
    if not manifests:
        raise ValueError("No manifests provided to merge")
    
    # Start with the first manifest as a base
    merged = {
        "name": output_name,
        "identifier": "com.octonezd.merged-repo",
        "iconURL": "https://octonezd.me/octo-ios-repo/icon.jpg",
        "apps": [],
        "news": []
    }
    
    # Track unique apps by bundle identifier to avoid duplicates
    seen_apps = set()
    
    # Merge apps from all manifests
    for manifest in manifests:
        if "apps" in manifest:
            for app in manifest["apps"]:
                bundle_id = app.get("bundleIdentifier", "")
                
                # Only add if we haven't seen this app before
                if bundle_id and bundle_id not in seen_apps:
                    merged["apps"].append(app)
                    seen_apps.add(bundle_id)
                elif not bundle_id:
                    # If no bundle ID, add anyway (though this shouldn't happen)
                    merged["apps"].append(app)
        
        # Optionally merge news items
        if "news" in manifest:
            for news_item in manifest["news"]:
                if news_item not in merged["news"]:
                    merged["news"].append(news_item)
    
    # Copy over other metadata if present in first manifest
    if manifests:
        first_manifest = manifests[0]
        for key in ["sourceURL", "subtitle", "description", "iconURL", "headerURL", "website", "tintColor"]:
            if key in first_manifest:
                merged[key] = first_manifest[key]
    
    return merged


def main():
    """Main function to merge AltStore repositories."""
    
    # URLs to merge
    urls = [
        "https://github.com/OctoNezd/oldlander/releases/latest/download/altStoreManifest.json",
        "https://github.com/OctoNezd/VNDS-LOVE-TOUCH/releases/latest/download/altStoreManifest.json"
    ]
    
    print("Fetching manifests...")
    manifests = []
    
    for url in urls:
        try:
            print(f"  - Fetching {url}")
            manifest = fetch_manifest(url)
            manifests.append(manifest)
            app_count = len(manifest.get("apps", []))
            print(f"    ✓ Found {app_count} app(s)")
        except Exception as e:
            print(f"    ✗ Failed to fetch {url}: {e}", file=sys.stderr)
            continue
    
    if not manifests:
        print("Error: No manifests could be fetched", file=sys.stderr)
        sys.exit(1)
    
    print("\nMerging manifests...")
    merged = merge_manifests(manifests, "OctoNezd's Merged Repository")
    
    # Write output
    output_file = "merged_altstore.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Successfully merged {len(manifests)} manifest(s)")
    print(f"  Total apps in merged repository: {len(merged['apps'])}")
    print(f"  Output saved to: {output_file}")
    
    # Also print to stdout for easy piping
    print("\n" + "="*60)
    print("Merged Manifest:")
    print("="*60)
    print(json.dumps(merged, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
