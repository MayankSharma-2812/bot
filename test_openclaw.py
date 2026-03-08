#!/usr/bin/env python3
"""
Test script to verify OpenClaw integration with Jarvis bot
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot import is_openclaw_running, get_openclaw_response

def test_openclaw_connection():
    print("Testing OpenClaw integration...")
    
    # Test 1: Check if OpenClaw is running
    print("\n1. Checking OpenClaw gateway status...")
    if is_openclaw_running():
        print("✅ OpenClaw gateway is running")
    else:
        print("❌ OpenClaw gateway is not running")
        print("   Start it with: npx openclaw gateway")
        return False
    
    # Test 2: Try a simple query
    print("\n2. Testing OpenClaw AI response...")
    try:
        response = get_openclaw_response("What is 2+2?", timeout=10)
        if response:
            print(f"✅ OpenClaw AI responded: {response}")
        else:
            print("❌ No response from OpenClaw AI")
            return False
    except Exception as e:
        print(f"❌ Error testing OpenClaw AI: {e}")
        return False
    
    print("\n✅ All tests passed! OpenClaw integration is working.")
    return True

if __name__ == "__main__":
    test_openclaw_connection()
