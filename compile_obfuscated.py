"""
Script to compile Python files to bytecode (.pyc)
This makes the code harder to read and reverse-engineer
"""
import py_compile
import os
import shutil

# Files to compile
files_to_compile = [
    'game.py',
    'player.py',
    'level.py'
]

# Create obfuscated directory
obfuscated_dir = 'obfuscated_game'
if os.path.exists(obfuscated_dir):
    shutil.rmtree(obfuscated_dir)
os.makedirs(obfuscated_dir)

print("🔒 Compiling Python files to bytecode...")

for file in files_to_compile:
    if os.path.exists(file):
        # Compile to .pyc
        compiled_file = py_compile.compile(file, doraise=True)
        print(f"✅ Compiled: {file} → {compiled_file}")

        # Copy to obfuscated directory
        dest_file = os.path.join(obfuscated_dir, file + 'c')
        shutil.copy(compiled_file, dest_file)
    else:
        print(f"❌ File not found: {file}")

# Copy necessary files
print("\n📋 Copying other necessary files...")
files_to_copy = [
    'api.py',
    'setup_database.py',
    'requirements.txt',
    'README.md',
    '.gitignore'
]

for file in files_to_copy:
    if os.path.exists(file):
        shutil.copy(file, os.path.join(obfuscated_dir, file))
        print(f"✅ Copied: {file}")

# Copy database-ui folder
if os.path.exists('database-ui'):
    shutil.copytree('database-ui', os.path.join(obfuscated_dir, 'database-ui'))
    print(f"✅ Copied: database-ui/")

print(f"\n🎉 Done! Obfuscated game is in '{obfuscated_dir}/' directory")
print(f"\n⚠️  Note: To run the obfuscated version, you'll need to create a launcher script")
