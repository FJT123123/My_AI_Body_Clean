import os
print("Current working directory:", os.getcwd())
print("All files in current directory:")
for f in os.listdir('.'):
    print(f"  {f}")
print("\nChecking test_image.png:")
print(f"  Exists: {os.path.exists('test_image.png')}")
print(f"  Is file: {os.path.isfile('test_image.png')}")
print(f"  Size: {os.path.getsize('test_image.png') if os.path.exists('test_image.png') else 'N/A'}")