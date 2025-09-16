#!/usr/bin/env python3
"""
Deployment Configuration Test Script
Tests the deployment setup before pushing to Railway
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def test_deployment_files():
    """Test that all required deployment files exist"""
    print("🔍 Testing deployment files...")
    
    required_files = [
        'Procfile',
        'runtime.txt', 
        'requirements.txt',
        'app.py',
        'client_secret.json',
        'Barrana-Merged-Prompt-Library-v3.1.json'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True

def test_procfile():
    """Test Procfile content"""
    print("\n🔍 Testing Procfile...")
    
    try:
        with open('Procfile', 'r') as f:
            content = f.read().strip()
        
        if content == 'web: python app.py':
            print("✅ Procfile content correct")
            return True
        else:
            print(f"❌ Procfile content incorrect: {content}")
            return False
    except Exception as e:
        print(f"❌ Error reading Procfile: {e}")
        return False

def test_runtime():
    """Test runtime.txt content"""
    print("\n🔍 Testing runtime.txt...")
    
    try:
        with open('runtime.txt', 'r') as f:
            content = f.read().strip()
        
        if content == 'python-3.11':
            print("✅ runtime.txt content correct")
            return True
        else:
            print(f"❌ runtime.txt content incorrect: {content}")
            return False
    except Exception as e:
        print(f"❌ Error reading runtime.txt: {e}")
        return False

def test_requirements():
    """Test requirements.txt"""
    print("\n🔍 Testing requirements.txt...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        required_packages = [
            'flask',
            'flask-cors', 
            'google-auth',
            'google-auth-oauthlib',
            'google-api-python-client',
            'openai',
            'python-dotenv'
        ]
        
        installed_packages = [req.split('==')[0] for req in requirements]
        
        missing_packages = []
        for package in required_packages:
            if package not in installed_packages:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages: {missing_packages}")
            return False
        
        print("✅ All required packages present")
        return True
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def test_app_configuration():
    """Test app.py configuration"""
    print("\n🔍 Testing app.py configuration...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for production-ready configurations
        checks = [
            ('PORT environment variable', 'os.environ.get(\'PORT\', 5050)' in content),
            ('Host 0.0.0.0', 'host=\'0.0.0.0\'' in content),
            ('CORS origins', 'allowed_origins' in content),
            ('Railway domain support', 'RAILWAY_PUBLIC_DOMAIN' in content)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def test_environment_variables():
    """Test environment variable setup"""
    print("\n🔍 Testing environment variables...")
    
    required_env_vars = [
        'OPENAI_API_KEY',
        'GOOGLE_SHEETS_TOPICS_ID', 
        'GOOGLE_SHEETS_PROMPTS_ID'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {missing_vars}")
        print("   These will need to be set in Railway dashboard")
        return True  # Not a failure, just a warning
    else:
        print("✅ All required environment variables are set")
        return True

def test_json_library():
    """Test JSON library file"""
    print("\n🔍 Testing JSON library...")
    
    try:
        with open('Barrana-Merged-Prompt-Library-v3.1.json', 'r') as f:
            data = json.load(f)
        
        # Check for required sections
        required_sections = ['meta', 'seo', 'voice_rules', 'globals', 'platforms']
        
        missing_sections = []
        for section in required_sections:
            if section not in data:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing JSON sections: {missing_sections}")
            return False
        
        # Count platforms
        platform_count = len(data.get('platforms', {}))
        print(f"✅ JSON library loaded with {platform_count} platforms")
        
        return True
    except Exception as e:
        print(f"❌ Error reading JSON library: {e}")
        return False

def main():
    """Run all deployment tests"""
    print("🚀 AI Content Agent - Deployment Configuration Test")
    print("=" * 60)
    
    tests = [
        test_deployment_files,
        test_procfile,
        test_runtime,
        test_requirements,
        test_app_configuration,
        test_environment_variables,
        test_json_library
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your app is ready for Railway deployment.")
        print("\n📋 Next steps:")
        print("1. Commit your changes: git add . && git commit -m 'Ready for deployment'")
        print("2. Push to GitHub: git push origin main")
        print("3. Deploy to Railway: https://railway.app")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
