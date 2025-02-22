"""
Test script to verify the setup and configuration of the dataset generator.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_environment():
    """Test environment setup and dependencies"""
    print("Testing environment setup...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"\nPython version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python version must be 3.8 or higher")
        return False
    print("✅ Python version check passed")
    
    # Check required directories
    required_dirs = ['src', 'data', 'output', 'logs']
    missing_dirs = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        return False
    print("✅ Directory structure check passed")
    
    # Check .env file
    if not Path('.env').exists():
        print("❌ .env file not found")
        return False
    
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        print("❌ GEMINI_API_KEY not properly configured in .env")
        return False
    print("✅ Environment variables check passed")
    
    # Check dependencies
    try:
        import google.generativeai
        import numpy
        import tqdm
        import aiofiles
        import sklearn
        import nltk
        print("✅ Dependencies check passed")
    except ImportError as e:
        print(f"❌ Missing dependency: {str(e)}")
        return False
    
    # Check source files
    required_files = [
        'src/main.py',
        'src/__init__.py',
        'src/utils/config.py',
        'src/utils/logger.py',
        'src/utils/progress_tracker.py',
        'src/generator/conversation_generator.py',
        'src/generator/topic_manager.py',
        'src/generator/quality_validator.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing source files: {', '.join(missing_files)}")
        return False
    print("✅ Source files check passed")
    
    return True

def test_imports():
    """Test importing key components"""
    print("\nTesting imports...")
    try:
        from src import (
            ConversationGenerator,
            TopicManager,
            QualityValidator,
            Config,
            logger,
            ProgressTracker
        )
        print("✅ Package imports check passed")
        return True
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

def test_config():
    """Test configuration validation"""
    print("\nTesting configuration...")
    try:
        from src import Config
        
        if not Config.validate_config():
            print("❌ Configuration validation failed")
            return False
        
        print("✅ Configuration validation passed")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Running setup verification tests...\n")
    
    tests_passed = 0
    tests_total = 3
    
    if test_environment():
        tests_passed += 1
    
    if test_imports():
        tests_passed += 1
    
    if test_config():
        tests_passed += 1
    
    print("\nTest Summary:")
    print(f"Tests passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("\n✅ All tests passed! The system is properly configured.")
        print("\nYou can now generate datasets using:")
        print("python src/main.py --total-conversations 1000")
    else:
        print("\n❌ Some tests failed. Please fix the issues above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
