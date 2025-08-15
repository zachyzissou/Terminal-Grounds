import os
import sys
import subprocess
import urllib.request
import zipfile
import time
from pathlib import Path

class ComfyUIInstaller:
    def __init__(self):
        self.base_dir = Path(r"C:\Users\Zachg\Terminal-Grounds")
        self.comfy_dir = self.base_dir / "ComfyUI"
        self.output_dir = self.base_dir / "Generations"
        
    def print_header(self):
        print("=" * 60)
        print("   COMFYUI AUTOMATED INSTALLER FOR TERMINAL GROUNDS")
        print("   RTX 3090 Ti Optimized Setup")
        print("=" * 60)
        print()
    
    def check_prerequisites(self):
        print("Checking prerequisites...")
        
        # Check Python
        try:
            result = subprocess.run(["python", "--version"], capture_output=True, text=True)
            print(f"✓ Python found: {result.stdout.strip()}")
        except:
            print("✗ Python not found. Please install Python 3.10+")
            return False
        
        # Check Git
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            print(f"✓ Git found: {result.stdout.strip()}")
        except:
            print("⚠ Git not found (optional)")
        
        return True
    
    def create_directories(self):
        print("\nCreating directories...")
        self.comfy_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {self.comfy_dir}")
        print(f"✓ Created: {self.output_dir}")
    
    def clone_comfyui(self):
        print("\nCloning ComfyUI from GitHub...")
        os.chdir(self.base_dir)
        
        if (self.comfy_dir / ".git").exists():
            print("ComfyUI already cloned, updating...")
            os.chdir(self.comfy_dir)
            subprocess.run(["git", "pull"])
        else:
            # Clone fresh
            subprocess.run(["git", "clone", "https://github.com/comfyanonymous/ComfyUI.git", "ComfyUI"])
        
        print("✓ ComfyUI repository ready")
    
    def install_dependencies(self):
        print("\nInstalling Python dependencies...")
        os.chdir(self.comfy_dir)
        
        # Upgrade pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install PyTorch with CUDA for RTX 3090 Ti
        print("Installing PyTorch with CUDA support (this may take a few minutes)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", 
                       "--index-url", "https://download.pytorch.org/whl/cu121"])
        
        # Install ComfyUI requirements
        if (self.comfy_dir / "requirements.txt").exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✓ Dependencies installed")
    
    def install_manager(self):
        print("\nInstalling ComfyUI Manager...")
        custom_nodes = self.comfy_dir / "custom_nodes"
        custom_nodes.mkdir(exist_ok=True)
        
        os.chdir(custom_nodes)
        if not (custom_nodes / "ComfyUI-Manager").exists():
            subprocess.run(["git", "clone", "https://github.com/ltdrdata/ComfyUI-Manager.git"])
            print("✓ ComfyUI Manager installed")
        else:
            print("✓ ComfyUI Manager already installed")
    
    def create_launcher(self):
        print("\nCreating optimized launcher for RTX 3090 Ti...")
        
        launcher_content = f'''@echo off
title Terminal Grounds - ComfyUI (RTX 3090 Ti)
echo ================================================
echo   TERMINAL GROUNDS COMFYUI
echo   RTX 3090 Ti - 24GB VRAM Mode
echo ================================================
echo.

cd /d "{self.comfy_dir}"

echo Starting ComfyUI with optimizations...
python main.py --highvram --use-pytorch-cross-attention --output-directory "{self.output_dir}"

pause
'''
        
        launcher_path = self.base_dir / "Launch_ComfyUI.bat"
        launcher_path.write_text(launcher_content)
        print(f"✓ Launcher created: {launcher_path}")
    
    def download_model(self):
        print("\n" + "=" * 60)
        print("IMPORTANT: Model Download Required")
        print("=" * 60)
        print("\nComfyUI needs at least one model to work.")
        print("\nRecommended model for your RTX 3090 Ti:")
        print("  SDXL Base 1.0 (6.9 GB)")
        print("  URL: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0")
        print("\nDownload and place in:")
        print(f"  {self.comfy_dir / 'models' / 'checkpoints'}")
        print("\nOpening download page...")
        
        import webbrowser
        webbrowser.open("https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/main")
    
    def run(self):
        self.print_header()
        
        if not self.check_prerequisites():
            print("\nPlease install missing prerequisites and run again.")
            return
        
        self.create_directories()
        
        try:
            self.clone_comfyui()
            self.install_dependencies()
            self.install_manager()
            self.create_launcher()
            
            print("\n" + "=" * 60)
            print("✅ INSTALLATION COMPLETE!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Download a model (browser opening...)")
            print(f"2. Run: {self.base_dir / 'Launch_ComfyUI.bat'}")
            print("3. Open browser to: http://127.0.0.1:8188")
            print("\nYour RTX 3090 Ti is ready to generate assets at maximum quality!")
            
            self.download_model()
            
        except Exception as e:
            print(f"\n❌ Error during installation: {e}")
            print("Please try manual installation or check the error above.")

if __name__ == "__main__":
    installer = ComfyUIInstaller()
    installer.run()
    input("\nPress Enter to exit...")
