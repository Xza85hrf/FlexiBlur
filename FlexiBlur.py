import cv2
import numpy as np
from PIL import Image, ImageFilter
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import os
import shutil
from moviepy.editor import VideoFileClip, AudioFileClip

# Check for CUDA availability
cuda_available = cv2.cuda.getCudaEnabledDeviceCount() > 0

# Setup detailed logging configuration
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize list for selected ROIs (Regions of Interest)
selected_rois = []

# Configuration parameters directly in the code
config = {"output": {"directory": "output/"}, "parallel_processing": {"max_workers": 4}}


# Error handling and logging wrapper
def handle_exceptions(func):
    """
    Decorator to handle exceptions and log errors for the decorated function.
    """

    def wrapper(*args, **kwargs):
        try:
            logging.debug(f"Starting {func.__name__} for {args[0]}")
            result = func(*args, **kwargs)
            logging.debug(f"Completed {func.__name__} for {args[0]}")
            return result
        except Exception as e:
            logging.error(f"Error processing {args[0]}: {e}", exc_info=True)
            return None

    return wrapper


@handle_exceptions
def apply_blur(image, roi, blur_mode, custom_settings):
    """
    Apply blur to a specified region of interest (ROI) in the image.
    """
    logging.debug(f"Applying {blur_mode} blur to ROI: {roi}")
    if image is None:
        logging.error("Input image is empty")
        return None

    # Validate and process the ROI
    if roi is not None:
        x, y, w, h = roi
        if (
            x < 0
            or y < 0
            or w <= 0
            or h <= 0
            or x + w > image.shape[1]
            or y + h > image.shape[0]
        ):
            logging.error("Invalid ROI specified")
            return image

        roi_section = image[
            y : y + h, x : x + w
        ].copy()  # Ensure roi_section is writable
    else:
        roi_section = image.copy()  # Ensure the whole image is writable

    try:
        # Apply the specified blur mode
        if blur_mode == "Heavy":
            blurred_roi = cv2.GaussianBlur(roi_section, (51, 51), 0)
        elif blur_mode == "Slight":
            blurred_roi = cv2.GaussianBlur(roi_section, (15, 15), 0)
        elif blur_mode == "Custom":
            ksize = custom_settings["ksize"]
            sigma = custom_settings["sigma"]
            blurred_roi = cv2.GaussianBlur(roi_section, (ksize, ksize), sigma)
        elif blur_mode == "Motion":
            direction = custom_settings["direction"]
            if direction == "horizontal":
                kernel = np.zeros((1, 15))
                kernel[0, :] = np.ones(15)
            elif direction == "vertical":
                kernel = np.zeros((15, 1))
                kernel[:, 0] = np.ones(15)
            blurred_roi = cv2.filter2D(roi_section, -1, kernel)
        elif blur_mode == "Radial":
            angle = custom_settings["angle"]
            image_pil = Image.fromarray(cv2.cvtColor(roi_section, cv2.COLOR_BGR2RGB))
            blurred_roi = image_pil.filter(ImageFilter.GaussianBlur(radius=angle))
            blurred_roi = cv2.cvtColor(np.array(blurred_roi), cv2.COLOR_RGB2BGR)
        else:
            logging.error(f"Unknown blur mode: {blur_mode}")
            return None

        # Update the image with the blurred ROI
        if roi is not None:
            image[y : y + h, x : x + w] = blurred_roi
        else:
            image = blurred_roi
    except Exception as e:
        logging.error(f"Error applying blur: {e}")
        return None

    return image


@handle_exceptions
def process_image(path, roi, blur_mode, custom_settings):
    """
    Process an image by applying the specified blur to the ROI.
    """
    logging.info(f"Processing image: {path}")

    image = cv2.imread(path)  # Read the image
    processed_image = apply_blur(image, roi, blur_mode, custom_settings)  # Apply blur

    if processed_image is None:
        logging.error(f"Processing failed for image: {path}")
        return None

    output_path = path  # Save the processed image to the same path
    cv2.imwrite(output_path, processed_image)

    return output_path


@handle_exceptions
def process_video(path, roi, blur_mode, custom_settings, start_time, end_time):
    """
    Process a video by applying the specified blur to the ROI in each frame.
    """
    logging.info(f"Processing video: {path}")

    def blur_region(frame):
        frame = frame.copy()  # Ensure frame is writable
        logging.debug(f"Processing frame with shape: {frame.shape}")
        processed_frame = apply_blur(frame, roi, blur_mode, custom_settings)
        if processed_frame is None:
            logging.error("Frame processing failed.")
        return processed_frame

    clip = VideoFileClip(path)  # Read the video file
    if end_time is None:
        end_time = clip.duration

    logging.debug(
        f"Clip duration: {clip.duration}, start_time: {start_time}, end_time: {end_time}"
    )

    # Apply blur to the video frames
    if start_time == 0 and end_time == clip.duration:
        blurred_clip = clip.fl_image(blur_region)
    else:
        blurred_clip = clip.subclip(start_time, end_time).fl_image(blur_region)

    output_path = os.path.join(config["output"]["directory"], os.path.basename(path))

    # Add audio if present
    if clip.audio is not None:
        audio = clip.audio.subclip(start_time, end_time) if end_time else clip.audio
        blurred_clip = blurred_clip.set_audio(audio)

    logging.debug(f"Writing video file to: {output_path}")
    try:
        blurred_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
        )
    except Exception as e:
        logging.error(f"Error writing video file: {e}")
    logging.info(f"Processed video saved to: {output_path}")
    return output_path


def process_media_in_parallel(
    media_paths, roi, blur_mode, custom_settings, start_time, end_time
):
    """
    Process multiple media files (images and videos) in parallel, applying the specified blur to the ROI.
    """
    logging.info("Starting parallel media processing")
    output_paths = []
    with ThreadPoolExecutor(
        max_workers=config["parallel_processing"]["max_workers"]
    ) as executor:
        futures = [
            executor.submit(
                (
                    process_image
                    if path.lower().endswith((".jpg", ".jpeg", ".png"))
                    else process_video
                ),
                path,
                roi,
                blur_mode,
                custom_settings,
                start_time,
                end_time,
            )
            for path in media_paths
        ]
        for future in tqdm(
            as_completed(futures), total=len(media_paths), desc="Processing media"
        ):
            result = future.result()
            if result:
                output_paths.append(result)
    logging.info("Completed parallel media processing")
    return output_paths


def save_processed_images(processed_paths, output_names, output_directory):
    """
    Save processed images to the specified output directory with given names.
    """
    for processed_path, output_name in zip(processed_paths, output_names):
        ext = os.path.splitext(processed_path)[1]
        output_path = os.path.join(output_directory, f"{output_name}{ext}")
        if os.path.isfile(processed_path):
            shutil.copy(processed_path, output_path)
        else:
            Image.fromarray(processed_path).save(output_path)
        logging.info(f"Saved processed file to: {output_path}")


if __name__ == "__main__":
    # Example usage of processing without a config file
    media_paths = ["example.jpg", "example.mp4"]
    roi = (50, 50, 200, 200)  # Example ROI
    blur_mode = "Heavy"
    custom_settings = {"ksize": 25, "sigma": 5, "direction": "horizontal", "angle": 45}
    start_time = 0.0
    end_time = None
    process_media_in_parallel(
        media_paths, roi, blur_mode, custom_settings, start_time, end_time
    )
