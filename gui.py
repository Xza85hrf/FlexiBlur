import sys
import os
import shutil

# Check if OpenCV is installed and accessible
try:
    import cv2

    print("OpenCV is installed and accessible.")
except ModuleNotFoundError:
    print("OpenCV is not installed in the current environment.")
    exit(1)

# Import necessary libraries for GUI and image processing
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import sv_ttk
import threading
import logging
from PIL import Image, ImageTk
from moviepy.editor import VideoFileClip

# Import custom processing functions from FlexiBlur
from FlexiBlur import process_media_in_parallel, save_processed_images

# Setup detailed logging configuration
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class FlexiBlurApp:
    """
    The main application class for the FlexiBlur GUI.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("FlexiBlur")
        self.root.geometry("600x800")
        self.root.resizable(True, True)

        # Set the initial theme to light
        sv_ttk.set_theme("light")

        # Configure the grid to make the window layout flexible
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(list(range(20)), weight=1)

        # Initialize variables
        self.media_paths = []
        self.tmp_media_paths = []
        self.output_directory = ""
        self.roi = None
        self.blur_mode = tk.StringVar(value="Heavy")  # Initialize blur mode variable
        self.custom_blur_settings = {
            "ksize": 25,
            "sigma": 5,
            "direction": "horizontal",
            "angle": 45,
        }
        self.video_blur_full = tk.BooleanVar(value=True)  # Blur full video by default
        self.start_time = tk.DoubleVar(value=0.0)
        self.end_time = tk.DoubleVar(value=0.0)

        # Create and configure the UI elements
        self.create_widgets()

    def create_widgets(self):
        """
        Create and configure the UI elements.
        """
        # Toggle theme button
        self.toggle_theme_button = ttk.Button(
            self.root, text="Toggle Theme", command=self.toggle_theme
        )
        self.toggle_theme_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Load media button
        self.load_media_button = ttk.Button(
            self.root, text="Load Media", command=self.load_media
        )
        self.load_media_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Select ROI button
        self.select_roi_button = ttk.Button(
            self.root, text="Select ROI", command=self.select_roi
        )
        self.select_roi_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Blur mode dropdown
        self.blur_mode_dropdown = ttk.Combobox(
            self.root,
            textvariable=self.blur_mode,
            values=["Heavy", "Slight", "Custom", "Motion", "Radial"],
        )
        self.blur_mode_dropdown.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.blur_mode_dropdown.bind("<<ComboboxSelected>>", self.on_blur_mode_change)

        # Video blur options
        self.blur_full_video_checkbox = ttk.Checkbutton(
            self.root,
            text="Blur Full Video",
            variable=self.video_blur_full,
            command=self.toggle_video_blur_options,
        )
        self.blur_full_video_checkbox.grid(
            row=4, column=0, padx=10, pady=10, sticky="ew"
        )

        # Start time
        self.start_time_label = ttk.Label(self.root, text="Start Time (s):")
        self.start_time_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.start_time_entry = ttk.Entry(self.root, textvariable=self.start_time)
        self.start_time_entry.grid(row=5, column=0, padx=10, pady=5, sticky="e")

        # End time
        self.end_time_label = ttk.Label(self.root, text="End Time (s):")
        self.end_time_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.end_time_entry = ttk.Entry(self.root, textvariable=self.end_time)
        self.end_time_entry.grid(row=6, column=0, padx=10, pady=5, sticky="e")

        # Start processing button
        self.process_media_button = ttk.Button(
            self.root, text="Start Processing", command=self.start_processing
        )
        self.process_media_button.grid(row=7, column=0, padx=10, pady=10, sticky="ew")

        # Save processed media button
        self.save_media_button = ttk.Button(
            self.root, text="Save Processed Media", command=self.save_processed_media
        )
        self.save_media_button.grid(row=8, column=0, padx=10, pady=10, sticky="ew")

        # Log display
        self.log_text = tk.Text(self.root, height=10, state="disabled")
        self.log_text.grid(row=9, column=0, padx=10, pady=10, sticky="nsew")

        # Media display
        self.media_label = ttk.Label(self.root)
        self.media_label.grid(row=10, column=0, padx=10, pady=10, sticky="nsew")

        # Redirect logging to the log display
        self.log_handler = TextHandler(self.log_text)
        logging.getLogger().addHandler(self.log_handler)

    def toggle_theme(self):
        """
        Toggle between light and dark themes.
        """
        if sv_ttk.get_theme() == "light":
            sv_ttk.set_theme("dark")
        else:
            sv_ttk.set_theme("light")

    def load_media(self):
        """
        Load media files (images and videos) into the application.
        """
        file_types = [
            ("Media files", "*.jpg *.jpeg *.png *.mp4 *.avi"),
            ("All files", "*.*"),
        ]
        self.media_paths = filedialog.askopenfilenames(
            title="Select Media", filetypes=file_types
        )
        if self.media_paths:
            # Create temporary directory for media copies
            self.tmp_media_dir = os.path.join(os.getcwd(), "tmp_media")
            os.makedirs(self.tmp_media_dir, exist_ok=True)

            self.tmp_media_paths = []
            for path in self.media_paths:
                tmp_path = os.path.join(self.tmp_media_dir, os.path.basename(path))
                shutil.copy(path, tmp_path)
                self.tmp_media_paths.append(tmp_path)

            messagebox.showinfo(
                "Media Loaded",
                f"{len(self.media_paths)} media files loaded successfully.",
            )
            self.display_media(self.tmp_media_paths[0])  # Display the first media
        else:
            messagebox.showwarning("No Media Selected", "No media files were selected.")

    def select_roi(self):
        """
        Select a region of interest (ROI) for applying the blur.
        """
        if not self.tmp_media_paths:
            messagebox.showwarning(
                "No Media", "Please load media files before selecting ROI."
            )
            return

        media_path = self.tmp_media_paths[0]
        if media_path.lower().endswith((".jpg", ".jpeg", ".png")):
            self.image = Image.open(media_path)
            self.roi_window = tk.Toplevel(self.root)
            self.roi_window.title("Select ROI")

            self.canvas = tk.Canvas(
                self.roi_window, width=self.image.width, height=self.image.height
            )
            self.canvas.pack()

            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

            self.rect = None
            self.start_x = None
            self.start_y = None

            self.canvas.bind("<ButtonPress-1>", self.on_button_press)
            self.canvas.bind("<B1-Motion>", self.on_move_press)
            self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        elif media_path.lower().endswith((".mp4", ".avi")):
            self.video_path = media_path
            self.video_clip = VideoFileClip(media_path)
            frame = self.video_clip.get_frame(0)
            self.image = Image.fromarray(frame)
            self.roi_window = tk.Toplevel(self.root)
            self.roi_window.title("Select ROI")

            self.canvas = tk.Canvas(
                self.roi_window, width=self.image.width, height=self.image.height
            )
            self.canvas.pack()

            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

            self.rect = None
            self.start_x = None
            self.start_y = None

            self.canvas.bind("<ButtonPress-1>", self.on_button_press)
            self.canvas.bind("<B1-Motion>", self.on_move_press)
            self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        """
        Handle the button press event for selecting ROI.
        """
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="red"
        )

    def on_move_press(self, event):
        """
        Handle the mouse movement event for selecting ROI.
        """
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        """
        Handle the button release event to finalize the ROI selection.
        """
        self.roi = (
            self.start_x,
            self.start_y,
            event.x - self.start_x,
            event.y - self.start_y,
        )
        self.roi_window.destroy()
        messagebox.showinfo("ROI Selected", f"ROI selected: {self.roi}")

    def on_blur_mode_change(self, event):
        """
        Handle the blur mode change event.
        """
        if self.blur_mode.get() == "Custom":
            self.show_custom_blur_settings()

    def show_custom_blur_settings(self):
        """
        Show the custom blur settings window.
        """
        self.custom_blur_window = tk.Toplevel(self.root)
        self.custom_blur_window.title("Custom Blur Settings")

        ttk.Label(self.custom_blur_window, text="Kernel Size:").grid(
            row=0, column=0, padx=10, pady=5
        )
        self.ksize_entry = ttk.Entry(self.custom_blur_window)
        self.ksize_entry.grid(row=0, column=1, padx=10, pady=5)
        self.ksize_entry.insert(0, str(self.custom_blur_settings["ksize"]))

        ttk.Label(self.custom_blur_window, text="Sigma:").grid(
            row=1, column=0, padx=10, pady=5
        )
        self.sigma_entry = ttk.Entry(self.custom_blur_window)
        self.sigma_entry.grid(row=1, column=1, padx=10, pady=5)
        self.sigma_entry.insert(0, str(self.custom_blur_settings["sigma"]))

        ttk.Label(self.custom_blur_window, text="Direction (for Motion Blur):").grid(
            row=2, column=0, padx=10, pady=5
        )
        self.direction_entry = ttk.Entry(self.custom_blur_window)
        self.direction_entry.grid(row=2, column=1, padx=10, pady=5)
        self.direction_entry.insert(0, self.custom_blur_settings["direction"])

        ttk.Label(self.custom_blur_window, text="Angle (for Radial Blur):").grid(
            row=3, column=0, padx=10, pady=5
        )
        self.angle_entry = ttk.Entry(self.custom_blur_window)
        self.angle_entry.grid(row=3, column=1, padx=10, pady=5)
        self.angle_entry.insert(0, str(self.custom_blur_settings["angle"]))

        save_button = ttk.Button(
            self.custom_blur_window, text="Save", command=self.save_custom_blur_settings
        )
        save_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def save_custom_blur_settings(self):
        """
        Save the custom blur settings entered by the user.
        """
        self.custom_blur_settings["ksize"] = int(self.ksize_entry.get())
        if self.custom_blur_settings["ksize"] % 2 == 0:
            self.custom_blur_settings["ksize"] += 1  # Ensure kernel size is odd
        self.custom_blur_settings["sigma"] = float(self.sigma_entry.get())
        self.custom_blur_settings["direction"] = self.direction_entry.get()
        self.custom_blur_settings["angle"] = int(self.angle_entry.get())
        self.custom_blur_window.destroy()

    def toggle_video_blur_options(self):
        """
        Toggle the start and end time entry states based on the full video blur option.
        """
        if self.video_blur_full.get():
            self.start_time_entry.config(state="disabled")
            self.end_time_entry.config(state="disabled")
        else:
            self.start_time_entry.config(state="normal")
            self.end_time_entry.config(state="normal")

    def start_processing(self):
        """
        Start the media processing in a separate thread.
        """
        if not self.tmp_media_paths:
            messagebox.showwarning(
                "No Media", "Please load media files before starting processing."
            )
            return

        threading.Thread(target=self.process_media, daemon=True).start()

    def process_media(self):
        """
        Process the loaded media files with the selected blur options.
        """
        try:
            start_time = (
                self.start_time.get() if not self.video_blur_full.get() else 0.0
            )
            end_time = self.end_time.get() if not self.video_blur_full.get() else None

            output_paths = process_media_in_parallel(
                self.tmp_media_paths,
                self.roi,
                self.blur_mode.get(),
                self.custom_blur_settings,
                start_time,
                end_time,
            )
            if output_paths:
                self.processed_paths = output_paths
                messagebox.showinfo(
                    "Processing Complete", "Media processing completed successfully."
                )
                self.display_media(
                    self.processed_paths[0]
                )  # Display the first processed media
            else:
                logging.warning("No media files were processed.")
                messagebox.showwarning(
                    "Processing Incomplete", "No media files were processed."
                )
        except Exception as e:
            logging.error(f"Error during processing: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")

    def save_processed_media(self):
        """
        Save the processed media files to the specified output directory.
        """
        if not hasattr(self, "processed_paths") or not self.processed_paths:
            messagebox.showwarning(
                "No Processed Media", "Please process media before saving."
            )
            return

        self.output_directory = filedialog.askdirectory(title="Select Output Directory")
        if not self.output_directory:
            messagebox.showwarning(
                "No Directory Selected", "No output directory was selected."
            )
            return

        output_names = [
            simpledialog.askstring(
                "Output Name", f"Enter output name for {os.path.basename(path)}"
            )
            for path in self.media_paths
        ]

        threading.Thread(
            target=self.save_media, args=(output_names,), daemon=True
        ).start()

    def save_media(self, output_names):
        """
        Save the processed media files with the specified names.
        """
        try:
            save_processed_images(
                self.processed_paths, output_names, self.output_directory
            )
            messagebox.showinfo("Save Complete", "Processed media saved successfully.")
        except Exception as e:
            logging.error(f"Error during saving: {e}")
            messagebox.showerror("Error", f"An error occurred while saving: {e}")

    def display_media(self, media_path):
        """
        Display the selected media (image or video) in the GUI.
        """
        if media_path.lower().endswith((".jpg", ".jpeg", ".png")):
            image = Image.open(media_path)
            image.thumbnail((400, 400))  # Resize image to fit the display area
            self.tk_image = ImageTk.PhotoImage(image)
            self.media_label.config(image=self.tk_image)
            self.media_label.image = self.tk_image
        elif media_path.lower().endswith((".mp4", ".avi")):
            self.media_label.config(
                text="Video loaded: " + os.path.basename(media_path)
            )


class TextHandler(logging.Handler):
    """
    Custom logging handler to display log messages in a Tkinter Text widget.
    """

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text_widget.configure(state="normal")
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.configure(state="disabled")
            self.text_widget.yview(tk.END)

        self.text_widget.after(0, append)


if __name__ == "__main__":
    # Initialize and start the Tkinter application
    root = tk.Tk()
    app = FlexiBlurApp(root)
    root.mainloop()
