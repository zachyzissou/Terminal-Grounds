"""
CI Validation Script for Terminal Grounds
Validates that no placeholder assets remain in the repository
"""
import sys
import json
from pathlib import Path
import argparse

# Add validation tools to path
sys.path.append(str(Path(__file__).parent))

# Import the scanner
try:
    from scan_placeholders import PlaceholderScanner
except ImportError:
    print("Error: Could not import PlaceholderScanner")
    print("Ensure scan_placeholders.py is in the same directory")
    sys.exit(1)


def validate_no_placeholders(repo_root, allowed_exceptions=None):
    """
    Validate that no placeholder assets exist
    Returns 0 if validation passes, 1 if placeholders found
    """
    if allowed_exceptions is None:
        allowed_exceptions = ['Screenshot TODO']
    
    scanner = PlaceholderScanner(repo_root)
    placeholders = scanner.scan()
    
    # Filter out allowed exceptions
    filtered = []
    for item in placeholders:
        # Check if this item should be excepted
        skip = False
        for exception in allowed_exceptions:
            if exception in item['path']:
                skip = True
                break
        
        if not skip:
            filtered.append(item)
    
    # Generate report
    report = scanner.generate_report()
    
    # Print results
    print("=" * 60)
    print("TERMINAL GROUNDS - PLACEHOLDER VALIDATION")
    print("=" * 60)
    
    if not filtered:
        print("✅ PASSED: No placeholder assets found")
        print(f"   Scanned {len(placeholders)} assets total")
        if len(placeholders) > len(filtered):
            print(f"   Allowed exceptions: {len(placeholders) - len(filtered)}")
        return 0
    else:
        print("❌ FAILED: Placeholder assets detected")
        print(f"   Found {len(filtered)} placeholder assets")
        print("\nPlaceholder Summary by Class:")
        
        by_class = {}
        for item in filtered:
            cls = item['class']
            by_class[cls] = by_class.get(cls, 0) + 1
        
        for cls, count in by_class.items():
            print(f"   - {cls}: {count}")
        
        print("\nFirst 10 Placeholders:")
        for item in filtered[:10]:
            print(f"   ⚠️ {item['path']}")
            print(f"      Flags: {', '.join(item['flags'])}")
        
        if len(filtered) > 10:
            print(f"   ... and {len(filtered) - 10} more")
        
        print("\n📄 Full report: Docs/.placeholder_report.json")
        print("\nTo fix:")
        print("1. Run: python Tools/Comfy/generate.py --recipe Tools/ArtGen/recipes/comfy_vertical_slice.yml")
        print("2. Or manually replace placeholder assets")
        print("3. Or quarantine: python Tools/Validation/scan_placeholders.py --quarantine")
        
        return 1


def validate_manifest_exists(repo_root):
    """Validate that asset manifest exists and is valid"""
    manifest_path = Path(repo_root) / "Docs" / "Concepts" / "ASSET_MANIFEST.json"
    
    if not manifest_path.exists():
        print("⚠️ WARNING: Asset manifest not found")
        print(f"   Expected at: {manifest_path}")
        return 1
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        if not isinstance(manifest, list):
            print("❌ ERROR: Manifest is not a valid list")
            return 1
        
        print(f"✅ Manifest valid: {len(manifest)} assets registered")
        return 0
        
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Manifest is not valid JSON: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(description='CI validation for placeholder assets')
    parser.add_argument('--root', default=r'C:\Users\Zachg\Terminal-Grounds',
                      help='Repository root path')
    parser.add_argument('--strict', action='store_true',
                      help='No exceptions allowed')
    parser.add_argument('--check-manifest', action='store_true',
                      help='Also validate asset manifest')
    
    args = parser.parse_args()
    
    # Determine allowed exceptions
    exceptions = [] if args.strict else ['Screenshot TODO', 'temp_ref', 'WIP_']
    
    # Run placeholder validation
    result = validate_no_placeholders(args.root, exceptions)
    
    # Check manifest if requested
    if args.check_manifest:
        manifest_result = validate_manifest_exists(args.root)
        if manifest_result != 0:
            result = manifest_result
    
    # Exit with appropriate code
    sys.exit(result)


if __name__ == '__main__':
    main()
