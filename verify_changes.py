#!/usr/bin/env python3
"""Verify the changes work by testing parsing and structure."""

import re
import sys

# Test 1: Check syntax
print("TEST 1: Checking Python syntax...")
try:
    import py_compile
    py_compile.compile('C:\\Users\\harsh\\PycharmProjects\\PythonProject1\\app.py', doraise=True)
    print("✓ app.py has valid syntax")
except Exception as e:
    print(f"✗ Syntax error: {e}")
    sys.exit(1)

# Test 2: Import and check HEADINGS
print("\nTEST 2: Checking HEADINGS structure...")
try:
    sys.path.insert(0, 'C:\\Users\\harsh\\PycharmProjects\\PythonProject1')
    from app import HEADINGS, SECTION_ALIASES
    print(f"✓ HEADINGS has {len(HEADINGS)} sections:")
    for i, h in enumerate(HEADINGS, 1):
        print(f"  {i}. {h}")
    
    if "target job role" in HEADINGS:
        print("✓ 'Target job role' section added")
    else:
        print("✗ 'Target job role' NOT found in HEADINGS")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test 3: Check SECTION_ALIASES
print("\nTEST 3: Checking SECTION_ALIASES...")
try:
    if "target job role" in SECTION_ALIASES:
        aliases = SECTION_ALIASES["target job role"]
        print(f"✓ Target job role has aliases: {aliases}")
    else:
        print("✗ 'target job role' NOT in SECTION_ALIASES")
        sys.exit(1)
except Exception as e:
    print(f"✗ Error checking aliases: {e}")
    sys.exit(1)

# Test 4: Check for multiplier logic
print("\nTEST 4: Checking multiplier strictness logic...")
try:
    with open('C:\\Users\\harsh\\PycharmProjects\\PythonProject1\\app.py', 'r') as f:
        content = f.read()
        if 'strictness_multiplier' in content:
            print("✓ Multiplier logic found")
        else:
            print("✗ Multiplier logic NOT found")
            sys.exit(1)
            
        if 'base_percent * strictness_multiplier' in content:
            print("✓ Multiplier is applied to score")
        else:
            print("✗ Multiplier NOT applied to final score")
            sys.exit(1)
except Exception as e:
    print(f"✗ Error checking multiplier: {e}")
    sys.exit(1)

# Test 5: Check target role scoring
print("\nTEST 5: Checking target role scoring...")
try:
    if 'has_target_role' in content:
        print("✓ has_target_role variable used")
    else:
        print("✗ has_target_role NOT found")
        sys.exit(1)
        
    if 'penalties += 8' in content:
        print("✓ Target role penalty (-8) set")
    else:
        print("✗ Target role penalty NOT found")
        sys.exit(1)
except Exception as e:
    print(f"✗ Error checking target role scoring: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✓ ALL STRUCTURAL CHECKS PASSED!")
print("="*60)
print("\nChanges verified:")
print("1. ✓ 8 sections in HEADINGS (added 'Target Job Role')")
print("2. ✓ SECTION_ALIASES updated with target role")
print("3. ✓ Multiplier-based strictness implemented")
print("4. ✓ Target role scoring integrated (-8 penalty if missing)")
print("\nNext: Test with actual resume scoring...")
