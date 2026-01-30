from PIL import Image
import numpy as np

def solve_with_formula(img_path):
    # Open the image
    img = Image.open(img_path).convert('RGB')
    
    # Convert to numpy array for easier channel manipulation
    img_array = np.array(img)
    
    # Extract R, G, B channels
    R = img_array[:, :, 0].astype(np.int16)
    G = img_array[:, :, 1].astype(np.int16)
    B = img_array[:, :, 2].astype(np.int16)
    
    # Apply the formula: ||R-G|-B|
    step1 = np.abs(R - G)  # |R-G|
    step2 = np.abs(step1 - B)  # ||R-G|-B|
    
    # Clip values to 0-255 range
    result = np.clip(step2, 0, 255).astype(np.uint8)
    
    # Create grayscale image from result
    result_img = Image.fromarray(result, mode='L')
    result_img.save('flag_formula.png')
    
    print("[+] Applied formula ||R-G|-B|")
    print("[+] Created flag_formula.png")
    print("[+] Check this file for your flag!")

# Try the formula on the main challenge image
solve_with_formula('chall.png')