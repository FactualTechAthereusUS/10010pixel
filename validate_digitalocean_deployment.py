#!/usr/bin/env python3
"""
Pre-deployment validation script for DigitalOcean
Checks if all dependencies and configurations are ready
"""
import os
import sys
import subprocess
from pathlib import Path

def check_required_files():
    """Check if all required files exist"""
    required_files = [
        '.do/app.yaml',
        'Dockerfile.digitalocean', 
        'digitalocean_start.py',
        'requirements.txt',
        'runtime.txt',
        'app.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present")
    return True

def validate_app_yaml():
    """Validate .do/app.yaml configuration"""
    try:
        with open('.do/app.yaml', 'r') as f:
            content = f.read()
        
        required_configs = [
            'dockerfile_path: Dockerfile.digitalocean',
            'instance_size_slug: professional-s',
            'http_port: 8080',
            'DIGITALOCEAN',
            'PLATFORM'
        ]
        
        missing_configs = []
        for config in required_configs:
            if config not in content:
                missing_configs.append(config)
        
        if missing_configs:
            print("❌ Missing configurations in .do/app.yaml:")
            for config in missing_configs:
                print(f"   - {config}")
            return False
        
        print("✅ DigitalOcean app.yaml configuration valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading .do/app.yaml: {e}")
        return False

def validate_dockerfile():
    """Validate Dockerfile.digitalocean"""
    try:
        with open('Dockerfile.digitalocean', 'r') as f:
            content = f.read()
        
        required_components = [
            'FROM python:3.11.7-slim',
            'ffmpeg',
            'libsm6',  # OpenCV dependencies
            'DIGITALOCEAN=true',
            'EXPOSE 8080',
            'digitalocean_start.py'
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print("❌ Missing components in Dockerfile.digitalocean:")
            for component in missing_components:
                print(f"   - {component}")
            return False
        
        print("✅ Dockerfile.digitalocean configuration valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading Dockerfile.digitalocean: {e}")
        return False

def validate_requirements():
    """Validate requirements.txt has all necessary packages"""
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        required_packages = [
            'streamlit>=1.28.0',
            'opencv-python>=4.8.0',
            'numpy>=1.24.0',
            'Pillow>=7.1.0',
            'python-multipart'
        ]
        
        missing_packages = []
        for package in required_packages:
            package_name = package.split('>=')[0].split('==')[0]
            if package_name not in content:
                missing_packages.append(package)
        
        if missing_packages:
            print("❌ Missing packages in requirements.txt:")
            for package in missing_packages:
                print(f"   - {package}")
            return False
        
        print("✅ Requirements.txt has all necessary packages")
        return True
        
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def check_potential_conflicts():
    """Check for potential deployment conflicts"""
    warnings = []
    
    # Check if nixpacks.toml might interfere (just a warning, not a failure)
    if Path('nixpacks.toml').exists():
        warnings.append("nixpacks.toml exists (Railway-specific, won't affect DigitalOcean Docker deployment)")
    
    # Check if there are multiple Dockerfiles (acceptable if they're platform-specific)
    dockerfiles = list(Path('.').glob('Dockerfile*'))
    if len(dockerfiles) > 1:
        dockerfile_names = [f.name for f in dockerfiles]
        if 'Dockerfile.digitalocean' in dockerfile_names:
            warnings.append(f"Multiple Dockerfiles found: {dockerfile_names} (acceptable for multi-platform deployment)")
        else:
            print(f"❌ Multiple Dockerfiles but no Dockerfile.digitalocean: {dockerfile_names}")
            return False
    
    if warnings:
        print("⚠️  Deployment notes:")
        for warning in warnings:
            print(f"   - {warning}")
    
    print("✅ No blocking deployment conflicts detected")
    return True

def validate_git_status():
    """Check if changes are committed to git"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("⚠️  Uncommitted changes detected:")
            print("   Remember to commit and push changes before DigitalOcean deployment")
            print("   (DigitalOcean deploys from GitHub, not local files)")
        else:
            print("✅ Git repository is clean")
        
        return True  # Don't fail validation for uncommitted changes
        
    except Exception as e:
        print(f"⚠️  Could not check git status: {e}")
        return True  # Don't fail deployment for git issues

def main():
    """Run all validation checks"""
    print("🔍 Validating DigitalOcean deployment configuration...\n")
    
    checks = [
        ("Required Files", check_required_files),
        ("App.yaml Configuration", validate_app_yaml),
        ("Dockerfile Configuration", validate_dockerfile),
        ("Requirements.txt", validate_requirements),
        ("Conflict Detection", check_potential_conflicts),
        ("Git Status", validate_git_status)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        if check_func():
            passed += 1
        
    print(f"\n📊 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All validations passed! Your app is ready for DigitalOcean deployment.")
        print("\n🚀 Next steps:")
        print("   1. Commit and push changes to GitHub")
        print("   2. Create new DigitalOcean App")
        print("   3. Connect to your GitHub repository")
        print("   4. Select 'main' branch") 
        print("   5. Choose Professional-S plan ($24/month)")
        print("   6. Deploy!")
        return 0
    else:
        print(f"\n❌ {total - passed} validation(s) failed. Please fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    exit(main())