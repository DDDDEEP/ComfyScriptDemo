import sys
import random
import os
import re
from PIL import Image, ImageDraw, ImageFont
from playsound import playsound
from typing import List, Optional, Union, Tuple
from enum import Enum
from utils.settings import *


def sanitize_path_for(path: str) -> str:
    """
    Sanitize a file path for use in a filename by removing or replacing characters 
    that are not allowed in filenames.

    :param path: The file path to sanitize
    :return: A string suitable for use as part of a filename
    """
    components = path.split('\\')

    # Take the last two elements and join them with double backslashes
    path = '\\'.join(components[-2:])

    # Replace backslashes with underscores to flatten the path
    path = path.replace('\\', '_')

    # Define characters that are not allowed in filenames (this can vary by OS but includes common ones)
    illegal_chars = r'[<>:"/\\|?*]'

    # Replace illegal characters with underscores
    sanitized = re.sub(illegal_chars, '_', path)

    # Optionally, you might want to remove leading/trailing underscores
    sanitized = sanitized.strip('_')

    # If the string ends up empty or only underscores after sanitization, provide a default name
    if not sanitized or sanitized == '_':
        sanitized = "unknown_path"

    return sanitized


def check_file_exists(folder_path: str, match_prefix: str = "") -> bool:
    """
    Check if there is any file in the specified folder that starts with the given prefix.

    :param folder_path: Path to the folder to check
    :param match_prefix: Prefix to match file names, defaults to an empty string (match all files)
    :return: True if a matching file exists, False otherwise
    """
    # Check if the folder exists
    if not os.path.isdir(folder_path):
        return False

    # Traverse all files in the folder
    for filename in os.listdir(folder_path):
        # Check if the filename matches the prefix, case-insensitive
        if filename.lower().startswith(match_prefix.lower()):
            return True

    # Return False if no matching file is found
    return False


def read_images_from_folder(folder_path: str, match_prefix: str = "", start_index: int = 0, max_count: Optional[int] = None) -> List[Tuple[Image.Image, str]]:
    """
    Read JPG and PNG images from the specified folder. Optionally return only files with names 
    matching a prefix, limit the number of returned images, and start reading from a specified index.

    :param folder_path: Path to the folder containing image files
    :param match_prefix: String prefix to match filenames, defaults to an empty string (match all images)
    :param max_count: Maximum number of images to return, default is None (return all matching images)
    :param start_index: Start reading from this index when sorting by name, default is 0
    :return: A list of tuples containing an image object and its filename without extension
    """
    images = []

    # Get filenames that match the criteria and sort them by name
    matching_files = [f for f in os.listdir(folder_path) if f.lower().startswith(
        match_prefix.lower()) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    sorted_files = sorted(matching_files)

    # Process files starting from the specified index
    for filename in sorted_files[start_index:]:
        file_path = os.path.join(folder_path, filename)
        try:
            with Image.open(file_path) as img:
                # Separate filename from extension, keep only the filename
                name_without_extension = os.path.splitext(filename)[0]
                images.append((img.copy(), name_without_extension))

                # Stop reading if the maximum count is reached
                if max_count is not None and len(images) >= max_count:
                    break
        except IOError as e:
            print(f'Unable to read file {filename}: {e}')

    return images


def danbooru_tag_to_sd(src_tag: str) -> str:
    """
    Convert Danbooru tags to SD tags with the following transformations:
    - Replace '_' with ' '
    - Replace '(' with '\(' and ')' with '\)'
    - Replace multiple spaces with a single space
    - Replace multiple newlines with a single newline
    - Replace multiple commas with a single comma

    :param src_tag: Original Danbooru tag
    :return: Converted SD tag
    """
    # Replace '_' with ' '
    result = src_tag.replace('_', ' ')

    # Replace '(' with '\(' and ')' with '\)'
    result = result.replace('(', '\(').replace(')', '\)')

    # Replace multiple spaces with a single space
    result = re.sub(r' +', ' ', result)

    # Replace multiple newlines with a single newline
    result = re.sub(r'\n+', '\n', result)

    # Replace multiple commas with a single comma
    result = re.sub(r',+', ',', result)

    return result


class Orientation(Enum):
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'


def create_title_images(titles: List[str], orientation: Orientation, width: int, height: int) -> Image.Image:
    """
    Create a white background image for each title with specified width and height, 
    center the title text on it, then arrange these images according to the given orientation.

    :param titles: List of strings to create title images for
    :param orientation: Direction to arrange images, either 'horizontal' or 'vertical'
    :param width: Width of each title image
    :param height: Height of each title image
    :return: A single PIL.Image object containing all title images
    """
    # Load a default font
    try:
        font = ImageFont.truetype("arial.ttf", 60)  # Assumes the system has Arial font
    except IOError:
        font = ImageFont.load_default()

    # Function to create a single title image
    def create_single_image(title):
        img = Image.new('RGB', (width, height), color='white')
        d = ImageDraw.Draw(img)

        # Use textbbox instead of textsize
        bbox = d.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]  # Right minus left for width
        text_height = bbox[3] - bbox[1]  # Bottom minus top for height

        # Calculate text position to center it
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        d.text((x, y), title, fill='black', font=font)
        return img

    # Create images for each title
    title_images = [create_single_image(title) for title in titles]

    # Decide how to arrange images based on orientation
    if orientation == Orientation.HORIZONTAL:
        total_width = sum(img.width for img in title_images)
        max_height = max(img.height for img in title_images)
        new_im = Image.new('RGB', (total_width, max_height), color='white')

        x_offset = 0
        for img in title_images:
            new_im.paste(img, (x_offset, 0))
            x_offset += img.width
    elif orientation == Orientation.VERTICAL:
        max_width = max(img.width for img in title_images)
        total_height = sum(img.height for img in title_images)
        new_im = Image.new('RGB', (max_width, total_height), color='white')

        y_offset = 0
        for img in title_images:
            new_im.paste(img, (0, y_offset))
            y_offset += img.height
    else:
        raise ValueError(
            "Orientation must be either 'horizontal' or 'vertical'")

    return new_im


def concat_images(images: List[Image.Image], orientation: Orientation) -> Image:
    """
    Concatenate multiple image objects.

    :param images: List of image objects (Image objects)
    :param orientation: Concatenation direction, 'horizontal' for horizontal, 'vertical' for vertical
    :return: Concatenated image object
    """
    if orientation == Orientation.HORIZONTAL:
        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths)
        max_height = max(heights)
        new_im = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        return new_im

    elif orientation == Orientation.VERTICAL:
        widths, heights = zip(*(i.size for i in images))
        max_width = max(widths)
        total_height = sum(heights)
        new_im = Image.new('RGB', (max_width, total_height))

        y_offset = 0
        for im in images:
            new_im.paste(im, (0, y_offset))
            y_offset += im.size[1]
        return new_im
    else:
        raise ValueError("unsupport orientation")


def resize_images(images: List[Image.Image], width: int, height: int) -> List[Image.Image]:
    """
    Resize each image in the list to specified dimensions while maintaining aspect ratio or stretching and padding.

    :param images: List of images to resize
    :param width: Target width
    :param height: Target height
    :return: List of resized images
    """
    resized_images = []
    target_width, target_height = width, height

    for img in images:
        original_width, original_height = img.size
        aspect_ratio = original_width / original_height

        # Calculate scaled dimensions while maintaining aspect ratio
        if original_width / original_height > target_width / target_height:  # Scale to match width
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
        else:  # Scale to match height
            new_height = target_height
            new_width = int(target_height * aspect_ratio)

        # Resize image
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)

        # Create new image with target size and black background
        new_img = Image.new(
            'RGB', (target_width, target_height), (0, 0, 0))  # Black background

        # Calculate offset to center the resized image
        offset = ((target_width - new_width) // 2,
                  (target_height - new_height) // 2)
        new_img.paste(img_resized, offset)

        resized_images.append(new_img)

    return resized_images


def create_images_row(*image_lists: List[Image.Image], titles: Optional[List[str]] = None, title_height: Optional[int] = None, width: int, height: int) -> Image.Image:
    """
    Create a row of images.
    A small area is vertically distributed as "title+image_list1[i]+image_list2[i]+...", and then each small area is connected horizontally to form a row of images.

    :param titles: List of titles, can be None if there are no titles
    :param title_height: Height of the titles, can be None if there are no titles
    :param *image_lists: Variable number of image lists, each list's images are sequentially added to the small area
    :param width: Width of each image
    :param height: Height of each image
    :return: A single concatenated Image object
    """
    rows = []

    # Determine the number of small areas based on the shortest image list length
    num_areas = min(len(lst) for lst in image_lists)

    for i in range(num_areas):
        small_area = []

        if titles is not None and title_height is not None and i < len(titles):
            # Create title image
            title_img = create_title_images([titles[i]], Orientation.HORIZONTAL, width, title_height)
            small_area.append(title_img)

        # Add images from each image list to the small area
        for image_list in image_lists:
            small_area.append(image_list[i])

        # If the small area doesn't have enough images, fill with blank images
        min_length = len(image_lists) + \
            (1 if titles is not None else 0)  # Title + all list images
        while len(small_area) < min_length:
            small_area.append(Image.new('RGB', (width, height), color='black'))

        # Vertically concatenate images in the small area
        rows.append(concat_images(small_area, Orientation.VERTICAL))

    # Horizontally concatenate all small areas
    return concat_images(rows, Orientation.HORIZONTAL)


def add_titles_for_image(image: Image.Image, x_titles: List[str] = [], y_titles: List[str] = [], font_size: int = 26) -> Image:
    """
    Add titles above and to the left of an image, centering x-titles with padding and evenly spacing y-titles.

    :param image: The base image to add titles to.
    :param x_titles: List of titles to be placed horizontally above each image segment with padding.
    :param y_titles: List of titles to be placed vertically to the left of the image, with automatic line wrapping.
    :return: Image with titles added.
    """
    font = ImageFont.truetype("arial.ttf", font_size)

    # Vertical padding for x titles and horizontal padding for y titles
    x_vertical_padding = 10  # Increased padding for x titles
    y_vertical_padding = 5
    x_horizontal_padding = 10

    # Calculate title dimensions with padding
    max_x_title_width, x_title_height = 0, 0
    for title in x_titles:
        bbox = font.getbbox(title)
        max_x_title_width = max(max_x_title_width, bbox[2] - bbox[0])
        x_title_height = max(x_title_height, bbox[3] - bbox[1] + y_vertical_padding)

    # For y titles, we use a smaller width to force wrapping
    wrap_width = 100  # Adjust this value based on your needs
    max_y_title_width, y_total_height = 0, 0
    y_titles_with_wrapping = []
    for title in y_titles:
        wrapped_lines = []
        words = title.split()
        current_line = []
        for word in words:
            if font.getbbox(" ".join(current_line + [word]))[2] <= wrap_width:
                current_line.append(word)
            else:
                wrapped_lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            wrapped_lines.append(" ".join(current_line))
        y_titles_with_wrapping.extend(wrapped_lines)

        for line in wrapped_lines:
            bbox = font.getbbox(line)
            max_y_title_width = max(max_y_title_width, bbox[2] - bbox[0] + x_horizontal_padding)
            y_total_height += bbox[3] - bbox[1] + y_vertical_padding

    # New image dimensions
    new_width = image.width + max_y_title_width
    new_height = image.height + x_title_height + x_vertical_padding  # Add padding for x titles
    new_image = Image.new("RGB", (new_width, new_height), color="white")

    draw = ImageDraw.Draw(new_image)

    # Paste original image below the x titles space
    new_image.paste(image, (max_y_title_width, x_title_height + x_vertical_padding))

    # Place x titles, centered within each segment with vertical padding
    if x_titles:
        segment_width = image.width // len(x_titles)
        for i, title in enumerate(x_titles):
            bbox = font.getbbox(title)
            x_position = max_y_title_width + i * segment_width + (segment_width - bbox[2]) // 2
            draw.text((x_position, x_vertical_padding // 2), title, font=font, fill="black")

    # Place y titles, evenly spaced and vertically centered within their segment
    if y_titles:
        y_segment_height = image.height // len(y_titles)
        y_offset = x_title_height + x_vertical_padding  # Start below x titles
        current_y = 0
        for i, title in enumerate(y_titles_with_wrapping):
            bbox = font.getbbox(title)
            if i % (len(y_titles_with_wrapping) // len(y_titles)) == 0:  # New y title segment
                current_y = y_offset + i * (y_segment_height // (len(y_titles_with_wrapping) // len(y_titles)))
                # Center y title within its segment
                current_y += (y_segment_height // (len(y_titles_with_wrapping) // len(y_titles)) - (bbox[3] - bbox[1])) // 2
            x_position = (max_y_title_width - bbox[2]) // 2
            draw.text((x_position, current_y), title, font=font, fill="black")
            current_y += bbox[3] - bbox[1] + y_vertical_padding

    return new_image
