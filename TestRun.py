import os
from moviepy.editor import VideoFileClip  # For handling video files
import cv2  # For image processing
import numpy as np  # For numerical operations


def apply_blur(image, roi, blur_mode, custom_settings):
    """
    Apply a blur effect to a specified region of interest (ROI) in the image.

    Args:
        image (numpy.ndarray): The input image.
        roi (tuple): The region of interest specified as (x, y, width, height).
        blur_mode (str): The type of blur to apply (currently only 'Heavy' is implemented).
        custom_settings (dict): Additional settings for custom blur (not used in this example).

    Returns:
        numpy.ndarray: The image with the blurred ROI.
    """
    if image is None:
        return None

    # Ensure the image is writable by creating a copy
    image = image.copy()

    # Extract the region of interest (ROI)
    x, y, w, h = roi
    roi_section = image[y : y + h, x : x + w].copy()

    # Apply Gaussian blur to the ROI
    blurred_roi = cv2.GaussianBlur(roi_section, (51, 51), 0)

    # Replace the ROI in the original image with the blurred ROI
    image[y : y + h, x : x + w] = blurred_roi
    return image


def blur_region(frame):
    """
    Apply a blur effect to a specific region of each frame.

    Args:
        frame (numpy.ndarray): The input video frame.

    Returns:
        numpy.ndarray: The frame with the blurred region.
    """
    # Define the region of interest (ROI) and custom settings
    roi = (50, 50, 200, 200)  # Example ROI
    custom_settings = {}  # Custom settings are not used in this example

    # Apply the blur effect to the ROI
    return apply_blur(frame, roi, "Heavy", custom_settings)


# Path to the input video file
path = "dir/to/yourvideo"
# Path to the output video file
output_path = "dir/to/outputpath"

# Check if the input file exists
if not os.path.exists(path):
    print(f"Error: The file {path} does not exist.")
else:
    # Load the video file
    clip = VideoFileClip(path)

    # Apply the blur effect to each frame of the video
    blurred_clip = clip.fl_image(blur_region)

    # Preserve the audio if it exists
    if clip.audio is not None:
        blurred_clip = blurred_clip.set_audio(clip.audio)

    # Write the processed video to the output file
    blurred_clip.write_videofile(
        output_path,
        codec="libx264",  # Video codec
        audio_codec="aac",  # Audio codec
        temp_audiofile="temp-audio.m4a",  # Temporary audio file
        remove_temp=True,  # Remove the temporary audio file after processing
    )
