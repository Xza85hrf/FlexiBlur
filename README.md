# FlexiBlur

FlexiBlur is a Python application that allows users to apply various blur effects to images and videos through a graphical user interface. It supports multiple blur modes, custom settings, and region of interest (ROI) selection for targeted blurring.

## Features

- GUI for easy interaction and media processing
- Support for both image and video blurring
- Multiple blur modes: Heavy, Slight, Custom, Motion, Radial
- Region of Interest (ROI) selection for targeted blurring
- Custom blur settings for advanced users
- Parallel processing of media files for improved performance
- Video processing with time range selection
- Theme toggling (light/dark)
- Logging of processing steps and errors

## Installation

### Prerequisites

- Python 3.x
- OpenCV
- tkinter
- PIL (Pillow)
- moviepy
- sv_ttk
- tqdm
- numpy

### Setting Up the Environment

1. Clone the repository:

    ```bash
    git clone https://github.com/Xza85hrf/FlexiBlur.git
    cd FlexiBlur
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the application:

    ```bash
    python FlexiBlur.py
    ```

2. Use the GUI to:

- Load media files (images or videos)
- Select a Region of Interest (ROI)
- Choose a blur mode
- Set custom blur settings if needed
- Process the media
- Save the processed files



## File Structure

flexiblur_app.py: Main application file with GUI implementation
FlexiBlur.py: Core processing functions for applying blur effects
TestRun.py: Example script for processing a video file
requirements.txt: List of required Python packages

Contributing
Contributions to FlexiBlur are welcome. Please feel free to submit pull requests, report bugs, or suggest features.

## Example Usage

Example usage of the processing functions without a config file:

```python
media_paths = ["example.jpg", "example.mp4"]
roi = (50, 50, 200, 200)  # Example ROI
blur_mode = "Heavy"
custom_settings = {"ksize": 25, "sigma": 5, "direction": "horizontal", "angle": 45}
start_time = 0.0
end_time = None
process_media_in_parallel(
    media_paths, roi, blur_mode, custom_settings, start_time, end_time
)
```



## License

This project is licensed under the MIT License - see the LICENSE file for details.
