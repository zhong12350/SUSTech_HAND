import os
import re
from bs4 import BeautifulSoup

# Path configuration
STEPS_DIR = r"./steps"
IMAGES_DIR = r"./assets/images"

# step10.html ~ step19.html
target_steps = list(range(10, 20))

# Template - structure for each image block
def generate_image_block(img_path, step, index):
    return f'''
    <div class="image-item">
        <img src="{img_path}" alt="Step {step} - Image {index}" class="step-image" data-image="{index}">
        <div class="image-caption">
            <h4>Figure {step}.{index}: Image {index} Description</h4>
            <p>Description for step {step} image {index}. Replace with actual description.</p>
        </div>
    </div>
    '''

# -------------------------------------------------------------------

print(f"Steps directory: {STEPS_DIR}")
print(f"Images directory: {IMAGES_DIR}")
print(f"Processing steps: {target_steps[0]} ~ {target_steps[-1]}")
print("-" * 50)

for step in target_steps:
    step_file = os.path.join(STEPS_DIR, f"step{step:02d}.html")
    
    if not os.path.exists(step_file):
        print(f"❌ File not found: {step_file}")
        continue

    print(f"Processing: {step_file}")

    try:
        # Read HTML with proper encoding detection
        with open(step_file, "r", encoding="utf-8") as f:
            html = f.read()

        # Use 'html.parser' for better compatibility
        soup = BeautifulSoup(html, "html.parser")

        # Find image-gallery div
        gallery = soup.find("div", class_="image-gallery")
        if gallery is None:
            print(f"⚠ Image gallery not found in: {step_file}")
            continue

        # Clear ALL children of gallery (not just text)
        for child in list(gallery.children):
            child.decompose()

        # Find images for this step
        image_files = []
        if os.path.exists(IMAGES_DIR):
            for fname in sorted(os.listdir(IMAGES_DIR)):
                # Match substep_xx_xx with any extension
                pattern = rf"^substep_{step}_\d+.*\.(png|jpg|jpeg|gif|webp)$"
                if re.match(pattern, fname, re.IGNORECASE):
                    image_files.append(fname)
        
        print(f"  - Found {len(image_files)} images: {image_files if image_files else 'None'}")

        # If no images found, check for any images in step10 directory
        if not image_files:
            step_img_dir = os.path.join(IMAGES_DIR, f"step{step}")
            if os.path.exists(step_img_dir):
                for fname in sorted(os.listdir(step_img_dir)):
                    if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        image_files.append(f"step{step}/{fname}")
                print(f"  - Found {len(image_files)} images in subdirectory")
        
        # Insert image blocks
        if image_files:
            for i, img in enumerate(image_files, start=1):
                img_path = f"../assets/images/{img}"
                # Create new soup for each block to avoid parsing issues
                block_soup = BeautifulSoup(generate_image_block(img_path, step, i), 'html.parser')
                gallery.append(block_soup)
        else:
            print(f"  ⚠ No images found. Gallery will be empty.")
        
        # Write back preserving original formatting as much as possible
        output = str(soup)
        
        # Ensure proper HTML structure
        output = output.replace('<html>', '<!DOCTYPE html>\n<html>')
        
        # Write to file
        with open(step_file, "w", encoding="utf-8") as f:
            f.write(output)
        
        print(f"  ✓ Updated successfully: step{step:02d}.html")
        
    except Exception as e:
        print(f"  ✗ Error processing {step_file}: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n🎉 Processing completed!")
print(f"Total steps processed: {len(target_steps)}")

# Summary
print("\n" + "="*50)
print("SUMMARY:")
print("="*50)
for step in target_steps:
    step_file = os.path.join(STEPS_DIR, f"step{step:02d}.html")
    if os.path.exists(step_file):
        # Count image blocks in the file
        with open(step_file, "r", encoding="utf-8") as f:
            content = f.read()
            image_count = content.count('class="image-item"')
            print(f"Step {step:02d}: {image_count} image blocks")