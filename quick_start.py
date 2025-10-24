"""
Quick start script for Disaster Relief Resource Optimizer.
Automatically sets up and launches the application.
"""

import subprocess
import sys
import os
import time

def run_command(command, description):
    """Run a command and print status."""
    print(f"\n📋 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ Error!")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Main quick start function."""
    print("🚨 DISASTER RELIEF RESOURCE OPTIMIZER - QUICK START")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("src/data_preprocessing.py"):
        print("❌ Please run this script from the disaster-relief-optimizer directory")
        return
    
    # Step 1: Check if model exists, if not train it
    if not os.path.exists("models/model.pkl"):
        print("\n🤖 Training ML model...")
        success = run_command("python train_model.py", "Training Random Forest model")
        if not success:
            print("❌ Model training failed. Please check the error messages above.")
            return
    else:
        print("\n✅ ML model already exists")
    
    # Step 2: Display setup information
    print("\n" + "=" * 60)
    print("🚀 READY TO LAUNCH!")
    print("=" * 60)
    
    print("\n📋 AUTHENTICATION SETUP:")
    print("-" * 30)
    print("The app supports two modes:")
    print("1. 🎮 DEMO MODE (No setup required)")
    print("   - Uses local authentication")
    print("   - Demo accounts: admin@disaster.com / admin123")
    print("   - Demo accounts: user@disaster.com / user123")
    print("\n2. 🔒 SUPABASE MODE (Full features)")
    print("   - Requires Supabase project setup")
    print("   - Update credentials in src/auth.py")
    print("   - Copy SQL schema to Supabase SQL Editor")
    
    print("\n📊 SUPABASE SQL SCHEMA:")
    print("-" * 30)
    print("If using Supabase, copy this SQL to your Supabase SQL Editor:")
    print("👉 Run: python src/auth.py")
    
    print("\n🌐 LAUNCH OPTIONS:")
    print("-" * 30)
    print("1. With Authentication: streamlit run app_with_auth.py")
    print("2. Basic Version: streamlit run app.py")
    
    # Ask user what they want to do
    print("\n" + "=" * 60)
    choice = input("Choose an option:\n1. Launch with Authentication\n2. Launch Basic App\n3. Show SQL Schema\n4. Exit\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🚀 Launching application with authentication...")
        print("🌐 App will open at: http://localhost:8501")
        print("🎮 Demo Mode: Use admin@disaster.com / admin123 to login")
        print("\n📝 Note: Press Ctrl+C to stop the application")
        time.sleep(2)
        subprocess.run("streamlit run app_with_auth.py", shell=True)
    
    elif choice == "2":
        print("\n🚀 Launching basic application...")
        print("🌐 App will open at: http://localhost:8501")
        print("\n📝 Note: Press Ctrl+C to stop the application")
        time.sleep(2)
        subprocess.run("streamlit run app.py", shell=True)
    
    elif choice == "3":
        print("\n📋 Displaying Supabase SQL Schema...")
        run_command("python src/auth.py", "Showing SQL Schema")
    
    elif choice == "4":
        print("\n👋 Goodbye!")
    
    else:
        print("\n❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()