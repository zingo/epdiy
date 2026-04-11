#!/usr/bin/env python3
"""
Download and convert weather icons for EPDiy e-ink display
Uses simple SVG to PNG conversion and then converts to EPDiy format
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Weather icon definitions - using Unicode symbols
# Using BMP (Basic Multilingual Plane) symbols that NotoSansSymbols2 supports
# For symbols not in NotoSansSymbols2, FreeSerif is used as fallback
WEATHER_ICONS = {
    'sunny': '☀️',
    'clear_night': '🌙',
    'cloudy': '☁️',
    'partlycloudy': '⛅',
    'rainy': '🌧️',
    'pouring': '⛈️',
    'snowy': '❄️',
    'fog': '🌫️',
    'windy': '💨',
    'hail': '🌨️',
    'lightning': '⚡',
}


def validate_image_content(image_path, icon_name):
    """
    Check if the image contains actual content (not just a single color)
    Returns True if valid, False if the image is all one color
    """
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        print("Warning: Cannot validate image - PIL/numpy not available")
        return True

    img = Image.open(image_path)
    img_array = np.array(img)

    # Check if all pixels are the same value
    unique_values = np.unique(img_array)

    if len(unique_values) == 1:
        print(
            f"[WARNING] {icon_name}: Image contains only a single color value ({unique_values[0]})"
        )
        print(f"          This might be intentional for simple icons")
        return False

    # Check if the image is mostly one color (more than 95% same value)
    total_pixels = img_array.size
    for value in unique_values:
        count = np.sum(img_array == value)
        percentage = (count / total_pixels) * 100
        if percentage > 95:
            print(
                f"[WARNING] {icon_name}: Image is {percentage:.1f}% single color value ({value})"
            )
            print(f"          This might be intentional for simple icons")
            return False

    return True


def print_ascii_art(image_path, icon_name, emoji, width=64):
    """
    Print the image as ASCII art
    """
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        print("Warning: Cannot print ASCII art - PIL/numpy not available")
        return

    # ASCII characters from dark to light
    ascii_chars = "@%#*+=-:. "

    img = Image.open(image_path)

    # Resize to fit terminal while maintaining aspect ratio
    aspect_ratio = img.height / img.width
    new_width = width
    new_height = int(
        width * aspect_ratio * 0.5
    )  # 0.5 because chars are taller than wide

    img = img.resize((new_width, new_height))
    img = img.convert("L")  # Ensure grayscale

    print(f"\n{icon_name} ({emoji}):")
    print("┌" + "─" * new_width + "┐")

    for y in range(new_height):
        line = "│"
        for x in range(new_width):
            pixel = img.getpixel((x, y))
            # Map 0-255 to 0-9 (index into ascii_chars)
            char_index = int(pixel / 256 * len(ascii_chars))
            char_index = min(char_index, len(ascii_chars) - 1)
            line += ascii_chars[char_index]
        line += "│"
        print(line)

    print("└" + "─" * new_width + "┘")

    img = Image.open(image_path)
    img_array = np.array(img)

    # Check if all pixels are the same value
    unique_values = np.unique(img_array)

    if len(unique_values) == 1:
        print(
            f"[WARNING] {icon_name}: Image contains only a single color value ({unique_values[0]})"
        )
        print(f"          This might be intentional for simple icons")
        return False

    # Check if the image is mostly one color (more than 95% same value)
    total_pixels = img_array.size
    for value in unique_values:
        count = np.sum(img_array == value)
        percentage = (count / total_pixels) * 100
        if percentage > 95:
            print(
                f"[WARNING] {icon_name}: Image is {percentage:.1f}% single color value ({value})"
            )
            print(f"          This might be intentional for simple icons")
            return False

    return True

    img = Image.open(image_path)
    img_array = np.array(img)

    # Check if all pixels are the same value
    unique_values = np.unique(img_array)

    if len(unique_values) == 1:
        print(
            f"[ERROR] {icon_name}: Image contains only a single color value ({unique_values[0]})"
        )
        print(f"        This suggests the icon rendering failed!")
        return False

    # Check if the image is mostly one color (more than 95% same value)
    total_pixels = img_array.size
    for value in unique_values:
        count = np.sum(img_array == value)
        percentage = (count / total_pixels) * 100
        if percentage > 95:
            print(
                f"[WARNING] {icon_name}: Image is {percentage:.1f}% single color value ({value})"
            )
            print(f"          This might indicate a rendering issue")
            return False

    return True


def create_simple_weather_icon(
    icon_name, emoji, output_path, size=128, use_emoji=False
):
    """
    Create a simple weather icon using PIL
    use_emoji: If True, render emoji; if False, draw geometric shapes
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("PIL not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image, ImageDraw, ImageFont

    # Create a white background image
    img = Image.new("L", (size, size), color=255)
    draw = ImageDraw.Draw(img)

    if use_emoji:
        # Try to render emoji
        try:
            # Try fonts that support Unicode weather symbols
            # NotoSansSymbols2 has the best coverage for weather symbols
            emoji_fonts = [
                # Best Unicode fonts for weather symbols (in order of preference)
                "/usr/share/fonts/truetype/noto/NotoSansSymbols2-Regular.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
                "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
                # JetBrains Mono (limited weather symbol support)
                "/home/zingo/.local/share/fonts/jetbrains-mono/JetBrainsMono-Regular.ttf",
                # macOS fonts
                "/System/Library/Fonts/Menlo.ttc",
                "/System/Library/Fonts/Monaco.ttf",
                # Windows fonts
                "Segoe UI Symbol",
                "Arial Unicode MS",
            ]

            font = None
            font_path_used = None
            for font_path in emoji_fonts:
                try:
                    if os.path.exists(font_path):
                        # Use a much larger font size for better quality
                        test_font = ImageFont.truetype(font_path, size=int(size * 2))
                        font = test_font
                        font_path_used = font_path
                        break
                except Exception as e:
                    continue

            if font is None:
                # Fallback to default font
                font = ImageFont.load_default()
                print(
                    f"Warning: No suitable font found for {icon_name}, using default font"
                )
                print(
                    "         Install Noto fonts for best emoji support: sudo apt install fonts-noto"
                )
            else:
                # Print which font is being used
                font_name = os.path.basename(font_path_used)
                print(f"  Using font: {font_name}")

            # Create a larger temporary image for better emoji rendering
            temp_size = size * 3
            temp_img = Image.new("L", (temp_size, temp_size), color=255)
            temp_draw = ImageDraw.Draw(temp_img)

            # Draw emoji centered on larger canvas
            bbox = temp_draw.textbbox((0, 0), emoji, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (temp_size - text_width) // 2
            y = (temp_size - text_height) // 2
            temp_draw.text((x, y), emoji, fill=0, font=font)

            # Resize down to target size with high quality
            img = temp_img.resize((size, size), Image.Resampling.LANCZOS)
            draw = ImageDraw.Draw(img)

        except Exception as e:
            print(f"Warning: Could not render emoji for {icon_name}: {e}")
            print("Falling back to drawn icon")
            use_emoji = False

    if not use_emoji:
        # Draw geometric shapes
        # Define simple geometric representations
        if icon_name == "sunny":
            # Draw a sun (circle with rays)
            center = size // 2
            radius = size // 4
            draw.ellipse(
                [center - radius, center - radius, center + radius, center + radius],
                fill=0,
            )
            # Rays
            for angle in range(0, 360, 45):
                import math

                rad = math.radians(angle)
                x1 = center + int((radius + 10) * math.cos(rad))
                y1 = center + int((radius + 10) * math.sin(rad))
                x2 = center + int((radius + 25) * math.cos(rad))
                y2 = center + int((radius + 25) * math.sin(rad))
                draw.line([x1, y1, x2, y2], fill=0, width=3)

        elif icon_name == "cloudy":
            # Draw clouds (overlapping circles)
            y_base = size * 2 // 3
            draw.ellipse([size // 6, y_base - 30, size // 3, y_base], fill=0)
            draw.ellipse([size // 4, y_base - 40, size * 2 // 3, y_base], fill=0)
            draw.ellipse([size // 2, y_base - 35, size * 5 // 6, y_base], fill=0)

        elif icon_name == "rainy":
            # Draw cloud + rain drops
            y_base = size // 2
            draw.ellipse([size // 6, y_base - 30, size // 3, y_base], fill=0)
            draw.ellipse([size // 4, y_base - 40, size * 2 // 3, y_base], fill=0)
            draw.ellipse([size // 2, y_base - 35, size * 5 // 6, y_base], fill=0)
            # Rain drops
            for x in range(size // 4, 3 * size // 4, 20):
                draw.line([x, y_base + 10, x, y_base + 30], fill=0, width=2)
                draw.line([x + 10, y_base + 20, x + 10, y_base + 40], fill=0, width=2)

        elif icon_name == "snowy":
            # Draw cloud + snowflakes
            y_base = size // 2
            draw.ellipse([size // 6, y_base - 30, size // 3, y_base], fill=0)
            draw.ellipse([size // 4, y_base - 40, size * 2 // 3, y_base], fill=0)
            draw.ellipse([size // 2, y_base - 35, size * 5 // 6, y_base], fill=0)
            # Snowflakes (asterisks)
            for x in range(size // 4, 3 * size // 4, 25):
                for y in [y_base + 15, y_base + 35]:
                    draw.line([x - 5, y, x + 5, y], fill=0, width=2)
                    draw.line([x, y - 5, x, y + 5], fill=0, width=2)
                    draw.line([x - 3, y - 3, x + 3, y + 3], fill=0, width=2)
                    draw.line([x - 3, y + 3, x + 3, y - 3], fill=0, width=2)

        elif icon_name == "partlycloudy":
            # Draw sun + cloud
            center = size // 3
            radius = size // 6
            draw.ellipse(
                [center - radius, center - radius, center + radius, center + radius],
                fill=0,
            )
            # Cloud
            y_base = size * 2 // 3
            draw.ellipse([size // 3, y_base - 25, size // 2, y_base], fill=0)
            draw.ellipse([size // 2 - 10, y_base - 30, size * 3 // 4, y_base], fill=0)

        elif icon_name == "fog":
            # Draw horizontal lines (fog)
            y_start = size // 3
            for i in range(5):
                y = y_start + i * 15
                draw.line([size // 6, y, size * 5 // 6, y], fill=0, width=3)

        elif icon_name == "clear_night":
            # Draw moon (crescent)
            center = size // 2
            radius = size // 4
            draw.ellipse(
                [center - radius, center - radius, center + radius, center + radius],
                fill=0,
            )
            # Overlay white circle to create crescent
            offset = radius // 2
            draw.ellipse(
                [
                    center - radius + offset,
                    center - radius,
                    center + radius + offset,
                    center + radius,
                ],
                fill=255,
            )

        elif icon_name in ["windy", "pouring", "hail", "lightning"]:
            # Default cloud for unimplemented
            y_base = size // 2
            draw.ellipse([size // 6, y_base - 30, size // 3, y_base], fill=0)
            draw.ellipse([size // 4, y_base - 40, size * 2 // 3, y_base], fill=0)
            draw.ellipse([size // 2, y_base - 35, size * 5 // 6, y_base], fill=0)

        else:
            # Default: question mark
            try:
                font = ImageFont.truetype("arial.ttf", size // 2)
            except:
                font = ImageFont.load_default()
            draw.text((size // 3, size // 4), "?", fill=0, font=font)

    img.save(output_path)

    # Validate the image content
    is_valid = validate_image_content(output_path, icon_name)

    print(f"Created {icon_name} icon: {output_path}")
    return is_valid


def main():
    parser = argparse.ArgumentParser(
        description="Download and convert weather icons for EPDiy e-ink display",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --drawn        # Use drawn geometric shapes (default)
  %(prog)s --emoji        # Use emoji characters
  %(prog)s --ascii        # Show ASCII art preview of generated icons
  %(prog)s --emoji --ascii  # Use emoji and show preview
  %(prog)s                # Same as --drawn
""",
    )
    parser.add_argument(
        "--emoji", action="store_true", help="Use emoji characters for icons"
    )
    parser.add_argument(
        "--drawn",
        action="store_true",
        help="Use drawn geometric shapes for icons (default)",
    )
    parser.add_argument(
        "--ascii",
        action="store_true",
        help="Print ASCII art preview of generated icons",
    )
    parser.add_argument(
        "--ascii-width",
        type=int,
        default=64,
        help="Width of ASCII art output (default: 64)",
    )

    args = parser.parse_args()

    # Determine mode: emoji takes precedence if both are specified
    use_emoji = args.emoji and not args.drawn

    script_dir = Path(__file__).parent
    icons_dir = script_dir / "weather_icons"
    icons_dir.mkdir(exist_ok=True)

    mode = "emoji" if use_emoji else "drawn"
    print(f"Creating weather icons (mode: {mode})...")

    # Create PNG icons
    single_color_icons = []
    valid_icons = []
    for icon_name, emoji in WEATHER_ICONS.items():
        png_path = icons_dir / f"{icon_name}.png"
        if create_simple_weather_icon(icon_name, emoji, png_path, use_emoji=use_emoji):
            valid_icons.append(icon_name)
        else:
            single_color_icons.append(icon_name)

        # Print ASCII art if requested
        if args.ascii:
            print_ascii_art(png_path, icon_name, emoji, width=args.ascii_width)

    # Only exit with error if ALL icons are single color
    if len(single_color_icons) == len(WEATHER_ICONS):
        print(
            f"\n[ERROR] ALL icons are single color - this indicates a rendering failure!"
        )
        print("Please check:")
        print("  - For emoji mode: Are emoji fonts installed?")
        print("  - For drawn mode: Is PIL working correctly?")
        sys.exit(1)
    elif single_color_icons:
        print(
            f"\n[INFO] {len(single_color_icons)} icon(s) are single color (may be intentional): {', '.join(single_color_icons)}"
        )
        print(f"[INFO] {len(valid_icons)} icon(s) have valid content")

    print("\nConverting icons to EPDiy format...")

    # Path to imgconvert.py
    imgconvert = script_dir / "imgconvert.py"
    output_header = script_dir.parent / "weather_icons.h"

    # Start header file
    with open(output_header, "w") as f:
        f.write("#pragma once\n")
        f.write("// Weather icons for EPDiy - Auto-generated\n")
        f.write(f"// Mode: {mode}\n")
        f.write("// Icons: " + ", ".join(WEATHER_ICONS.keys()) + "\n\n")

    # Convert each icon
    for icon_name in WEATHER_ICONS.keys():
        png_path = icons_dir / f"{icon_name}.png"
        temp_header = icons_dir / f"{icon_name}_temp.h"

        # Run imgconvert.py
        result = subprocess.run(
            [
                sys.executable,
                str(imgconvert),
                "-i",
                str(png_path),
                "-n",
                f"weather_{icon_name}",
                "-o",
                str(temp_header),
                "-maxw",
                "128",
                "-maxh",
                "128",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Append to main header
            with open(temp_header, "r") as tf:
                with open(output_header, "a") as f:
                    f.write(tf.read())
                    f.write("\n")
            temp_header.unlink()  # Remove temp file
            print(f"[OK] Converted {icon_name}")
        else:
            print(f"[FAIL] Failed to convert {icon_name}: {result.stderr}")

    print(f"\n[SUCCESS] All icons converted to: {output_header}")
    print(f"\nTo use in ESPHome, add this to your configuration:")
    print(f"  external_files:")
    print(f"    - {output_header}")


if __name__ == "__main__":
    main()
