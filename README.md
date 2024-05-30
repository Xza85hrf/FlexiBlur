# FlexiBlur

FlexiBlur is a Python GUI application that lets users apply various blur effects to images and videos. It supports simple and advanced blur techniques, including custom settings for motion and radial blurs. Designed for systems with OpenCV, FlexiBlur provides a user-friendly interface for easy and efficient media processing.

## Features

- Real-time temperature monitoring with visual feedback.
- Temperature logging with threshold-based activation.
- Automatic log rotation to manage disk space.
- Option to run as a daemon for background processing.
- Color-coded temperature display in the terminal for easy monitoring.
- Supports multiple blur modes: Heavy, Slight, Custom, Motion, Radial.
- Region of Interest (ROI) selection for targeted blurring.
- Parallel processing of media files for improved performance.

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
    python gui.py
    ```

2. Use the GUI to load media files, select the blur mode, and specify the region of interest (ROI) if necessary.

3. Start the processing and save the processed media files to your desired output directory.

## Configuration

Modify the configuration parameters directly in the code for customized behavior:

- `threshold`: The temperature threshold above which alerts will be logged.
- `log_file`: Path to the log file.
- `poll_interval`: Time interval in seconds between each temperature read.

## Code Overview

### flexiblur_app.py

This is the main application file that sets up the GUI and handles user interactions. The main class `FlexiBlurApp` initializes the interface, creates widgets, and manages media processing.

### temperature_monitor.h

This header file contains function declarations for temperature monitoring, logging, and daemonizing the process.

### FlexiBlur.py

This script contains the core processing functions for applying blur effects to images and videos. It handles parallel processing using ThreadPoolExecutor and includes custom blur implementations.

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

## Contributing

Contributions to the FlexiBlur project are welcome. Here’s how you can contribute:

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/my-new-feature`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/my-new-feature`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
