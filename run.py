#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import importlib

def check_and_install_packages():
    """Check and install required packages only if missing"""
    required_packages = {
        'Pillow': 'PIL',
        'jdatetime': 'jdatetime',
        'reportlab': 'reportlab',
        'arabic_reshaper': 'arabic_reshaper',
        'python_bidi': 'bidi'
    }
    
    missing = []
    for package, import_name in required_packages.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing packages: {missing}")
        response = input("Do you want to install them? (y/n): ")
        if response.lower() == 'y':
            for package in missing:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
            print("All packages installed successfully!")
            return True
        else:
            print("Please install required packages manually.")
            return False
    return True

if __name__ == "__main__":
    if check_and_install_packages():
        # Run main application
        from main import WarehouseApplication
        app = WarehouseApplication()