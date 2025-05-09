from PIL import Image
import os
import sys
import shutil
from pathlib import Path

# Automatically use user's real Pictures folder
FINAL_BASE_FOLDER = Path.home() / "Pictures"

def resize_proportionally(img, target_ratio):
    width, height = img.size
    current_ratio = width / height

    if current_ratio > target_ratio:
        new_height = height
        new_width = int(height * target_ratio)
    else:
        new_width = width
        new_height = int(width / target_ratio)

    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    return resized_img

def pad_to_exact_ratio(img, target_x, target_y, padding_color=(0,0,0,0)):
    width, height = img.size
    target_ratio = target_x / target_y

    if width / height < target_ratio:
        new_width = int(height * target_ratio)
        new_height = height
    else:
        new_width = width
        new_height = int(width / target_ratio)

    padded_img = Image.new("RGBA", (new_width, new_height), padding_color)
    offset_x = (new_width - width) // 2
    offset_y = (new_height - height) // 2
    padded_img.paste(img, (offset_x, offset_y))

    return padded_img

def split_and_resize(img, tiles_x, tiles_y, tile_size, output_folder, base_filename):
    padded_width, padded_height = img.size
    tile_width = padded_width // tiles_x
    tile_height = padded_height // tiles_y

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    tile_count = 0
    for y in range(tiles_y):
        for x in range(tiles_x):
            left = x * tile_width
            upper = y * tile_height
            right = left + tile_width
            lower = upper + tile_height
            tile = img.crop((left, upper, right, lower))
            tile = tile.resize((tile_size, tile_size), Image.LANCZOS)

            row_num = y + 1
            col_num = x + 1
            filename = f"{base_filename}_Split_R{row_num}C{col_num}.png"
            tile.save(os.path.join(output_folder, filename))
            tile_count += 1

    print(f"Done! {tile_count} tiles saved to '{output_folder}'.")

def suggest_aspect_ratios(width, height, top_n=3):
    """Suggest the top N nearest common aspect ratios"""
    aspect_ratio = width / height

    common_ratios = {
        (1, 1): "1:1",
        (4, 3): "4:3",
        (3, 2): "3:2",
        (16, 9): "16:9",
        (3, 4): "3:4",
        (2, 3): "2:3",
        (9, 16): "9:16",
        (5, 4): "5:4",
        (4, 5): "4:5",
        (5, 7): "5:7",
        (7, 5): "7:5",
    }

    matches = []

    for (w, h), name in common_ratios.items():
        ratio = w / h
        diff = abs(aspect_ratio - ratio)
        matches.append((diff, w, h, ratio, name))

    matches.sort()
    return matches[:top_n]

def process_image(image_path, tiles_x, tiles_y, tile_size=64, padding_color=(0,0,0,0)):
    if not os.path.isfile(image_path):
        print(f"Error: The file '{image_path}' does not exist.")
        input("Press Enter to exit...")
        sys.exit(1)

    supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
    if not image_path.lower().endswith(supported_formats):
        print(f"Error: Unsupported file type.")
        input("Press Enter to exit...")
        sys.exit(1)

    img = Image.open(image_path).convert('RGBA')
    temp_converted = False

    if not image_path.lower().endswith('.png'):
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        new_path = os.path.join(os.getcwd(), base_name + "_converted.png")
        img.save(new_path)
        print(f"Converted '{image_path}' to PNG: '{new_path}'")
        image_path = new_path
        temp_converted = True

    target_ratio = tiles_x / tiles_y

    base_filename = os.path.splitext(os.path.basename(image_path))[0]
    output_folder = os.path.join(FINAL_BASE_FOLDER, f"{base_filename}_split_{tiles_x}x{tiles_y}")

    if os.path.exists(output_folder):
        response = input(f"Output folder '{output_folder}' already exists. Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("Aborted by user. No tiles created.")
            input("Press Enter to exit...")
            sys.exit(0)
        else:
            shutil.rmtree(output_folder)
            print(f"Old output folder '{output_folder}' deleted.")

    resized_img = resize_proportionally(img, target_ratio)
    padded_img = pad_to_exact_ratio(resized_img, tiles_x, tiles_y, padding_color)

    preview_path = os.path.join(os.getcwd(), "preview_padded.png")
    padded_img.save(preview_path)
    print(f"Preview saved as '{preview_path}'. Opening preview...")

    padded_img.show()

    response = input("Is the preview okay? (y/n): ").strip().lower()

    if response != 'y':
        print("Aborted by user. No tiles created.")
        input("Press Enter to exit...")
        sys.exit(0)

    split_and_resize(padded_img, tiles_x, tiles_y, tile_size, output_folder, base_filename)

    # Cleanup temporary converted file
    if temp_converted and os.path.exists(image_path):
        try:
            os.remove(image_path)
            print(f"Temporary file '{image_path}' deleted.")
        except Exception as e:
            print(f"Warning: Could not delete temporary file. ({e})")

    # Cleanup preview padded image
    if os.path.exists(preview_path):
        try:
            os.remove(preview_path)
            print("Preview image deleted.")
        except Exception as e:
            print(f"Warning: Could not delete preview image. ({e})")

if __name__ == "__main__":
    if len(sys.argv) == 1 or (len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help")):
        print("""
Image Splitter Help
-------------------
Usage (manual mode):
    python splitter.py <image_path> <tiles_x> <tiles_y> [padding_color_hex]

    <image_path>         Path to the image you want to split (.png, .jpg, .jpeg, .bmp, .gif, .webp)
    <tiles_x>            Number of horizontal tiles (columns).
    <tiles_y>            Number of vertical tiles (rows).
    [padding_color_hex]  (Optional) 6-digit hex color for padding. Default is transparent.

Examples:
    python splitter.py my_image.png 3 4
    python splitter.py my_image.jpg 3 4 FFFFFF

Usage (drag-and-drop mode):
    Drag and drop an image file onto the executable.
    You'll be asked how many tiles horizontally and vertically.

Notes:
- JPG, BMP, GIF, WebP are auto-converted to PNG.
- A preview will be shown before creating tiles.
- Output tiles will be saved inside your Pictures folder under a subfolder like:
  <filename>_split_<tiles_x>x<tiles_y>
- Row and column numbering starts at 1.
""")
        input("Press Enter to exit...")
        sys.exit(0)

    if len(sys.argv) == 2:
        image_path = sys.argv[1]
        print("Single image detected. No tile settings provided.")

        try:
            img = Image.open(image_path)
            width, height = img.size
            suggestions = suggest_aspect_ratios(width, height)

            print("Suggested splits:")
            for _, w, h, ratio, name in suggestions:
                print(f" - {w}x{h} (aspect ratio ~{ratio:.3f})")

        except Exception as e:
            print(f"Warning: Could not read image for aspect suggestion. ({e})")

        try:
            tiles_x_input = input("Enter number of tiles horizontally (columns) [default 3]: ").strip()
            tiles_y_input = input("Enter number of tiles vertically (rows) [default 4]: ").strip()

            tiles_x = int(tiles_x_input) if tiles_x_input else 3
            tiles_y = int(tiles_y_input) if tiles_y_input else 4

        except ValueError:
            print("Error: You must enter valid integer numbers for tiles.")
            input("Press Enter to exit...")
            sys.exit(1)

        padding_color = (0, 0, 0, 0)
        print(f"Using settings: {tiles_x}x{tiles_y} tiles, transparent padding.")

    elif len(sys.argv) >= 4:
        image_path = sys.argv[1]
        tiles_x = int(sys.argv[2])
        tiles_y = int(sys.argv[3])

        padding_color = (0, 0, 0, 0)
        if len(sys.argv) == 5:
            hex_color = sys.argv[4]
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                padding_color = (r, g, b, 255)
    else:
        print("Usage error: Incorrect number of arguments. Use -h for help.")
        input("Press Enter to exit...")
        sys.exit(1)

    process_image(image_path, tiles_x, tiles_y, tile_size=64, padding_color=padding_color)
