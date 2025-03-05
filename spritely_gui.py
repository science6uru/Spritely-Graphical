import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import math
import re

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)

def toggle_resize():
    state = 'normal' if resize_var.get() else 'disabled'
    width_entry.config(state=state)
    height_entry.config(state=state)

# Image processing functions adapted for Pillow - A crapton faster than ImageMagick for simple stuff like this
def calculate_trim(images):
    """Calculate the minimum bounding box capturing all content across images."""
    if not images:
        return {'left': 0, 'top': 0, 'width': 0, 'height': 0}
    # Get the bounding box of the first image
    left, top, right, bottom = images[0].getbbox()
    # Union of bounding boxes across all images
    for img in images[1:]:
        l, t, r, b = img.getbbox()
        left = min(left, l)
        top = min(top, t)
        right = max(right, r)
        bottom = max(bottom, b)  # NOTE::::: 'bottom' should replace 'custom'!!
    return {'left': left, 'top': top, 'width': right - left, 'height': bottom - top}

def trim_images(images, dimensions=None):
    """Crop each image to the calculated trim dimensions."""
    if dimensions is None:
        dimensions = calculate_trim(images)
    left = dimensions['left']
    top = dimensions['top']
    right = left + dimensions['width']
    bottom = top + dimensions['height']
    return [img.crop((left, top, right, bottom)) for img in images]

def smart_resize(image, width, height):
    """Resize image maintaining aspect ratio and center it on a transparent canvas."""
    iw, ih = image.size
    wr = width / iw
    hr = height / ih
    ratio = min(wr, hr)
    new_size = (int(iw * ratio), int(ih * ratio))
    resized = image.resize(new_size, Image.Resampling.LANCZOS)  # ANTIALIAS is deprecated... use LANCZOS.
    new_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paste_x = (width - new_size[0]) // 2
    paste_y = (height - new_size[1]) // 2
    new_image.paste(resized, (paste_x, paste_y))
    return new_image

def resample(items, target_count):
    """Reduce item count by evenly selecting from the list."""
    source_count = len(items)
    if source_count < target_count:
        messagebox.showerror("Error", "Not enough images to resample")
        raise ValueError("Not enough images to resample")
    skip_ratio = source_count / target_count
    indices = [0] + [round(i * skip_ratio) for i in range(1, target_count)]
    return [items[i] for i in indices]

def get_directory_images(directory):
    """Get and return a list of images from a directory."""
    source_files = [
        os.path.join(directory, f) for f in os.listdir(directory)
        if re.search(r"\.(png|jpg|jpeg|gif|tiff)", f, re.IGNORECASE)
    ]
    source_files.sort()
    return [Image.open(f) for f in source_files]

def create_spritesheet(images, rows, columns, filename):
    """Create a spritesheet from images."""
    if not images:
        return
    img_width, img_height = images[0].size
    sheet_width = img_width * columns
    sheet_height = img_height * rows
    sheet = Image.new("RGBA", (sheet_width, sheet_height), (0, 0, 0, 0))
    for i, img in enumerate(images):
        row = i // columns
        col = i % columns
        x = col * img_width
        y = row * img_height
        sheet.paste(img, (x, y))
    sheet.save(filename)

def create_animated_gif(images, filename):
    """Create an animated GIF from images with disposal."""
    if not images:
        return
    # Save with disposal=2 to restore to background, clear previous frames
    images[0].save(filename, save_all=True, append_images=images[1:], loop=0, duration=100, disposal=2)

def convert():
    folder = folder_path.get()
    if not folder:
        messagebox.showerror("Error", "Please select a folder.")
        return
    
    # Load images 
    try:
        images = get_directory_images(folder)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load images: {e}")
        return
    
    if not images:
        messagebox.showerror("Error", "No image files found in the selected folder.")
        return
    
    format = format_var.get()
    width = None
    height = None
    resize = resize_var.get()
    
    # Handle resizing if enabled
    if resize:
        width_str = width_var.get()
        height_str = height_var.get()
        if not width_str or not height_str:
            messagebox.showerror("Error", "Please provide width and height for resizing.")
            return
        try:
            width = int(width_str)
            height = int(height_str)
        except ValueError:
            messagebox.showerror("Error", "Width and height must be integers.")
            return
    
    if format == "Spritesheet":
        rows_str = rows_var.get()
        columns_str = columns_var.get()
        if not rows_str or not columns_str:
            messagebox.showerror("Error", "Please provide rows and columns for Spritesheet.")
            return
        try:
            rows = int(rows_str)
            columns = int(columns_str)
        except ValueError:
            messagebox.showerror("Error", "Rows and columns must be integers.")
            return
        
        try:
            images = resample(images, rows * columns)
        except ValueError:
            return  
        
        if trim_var.get():
            images = trim_images(images)
        
        if resize:
            images = [smart_resize(img, width, height) for img in images]
        
        filetypes = [("PNG files", "*.png")]
        defaultext = ".png"
        output_func = lambda filename: create_spritesheet(images, rows, columns, filename)
    
    elif format == "GIF":
        frames_str = frames_var.get()
        frames = None
        if frames_str:
            try:
                frames = int(frames_str)
                images = resample(images, frames)
            except ValueError:
                messagebox.showerror("Error", "Frame count must be an integer.")
                return
            except ValueError:
                return  
        
        if trim_var.get():
            images = trim_images(images)
        
        if resize:
            images = [smart_resize(img, width, height) for img in images]
        
        filetypes = [("GIF files", "*.gif")]
        defaultext = ".gif"
        output_func = lambda filename: create_animated_gif(images, filename)
    
    output_file = filedialog.asksaveasfilename(
        defaultextension=defaultext,
        filetypes=filetypes,
        title="Save Output As"
    )
    if output_file:
        try:
            output_func(output_file)
            status_label.config(text=f"Output saved to {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save output: {e}")

root = tk.Tk()
root.title("Spritely GUI")

tk.Label(root, text="Select input folder:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
folder_path = tk.StringVar()
folder_entry = tk.Entry(root, textvariable=folder_path, width=50)
folder_entry.grid(row=0, column=1, padx=5, pady=5)
browse_button = tk.Button(root, text="Browse...", command=select_folder)
browse_button.grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Select output format:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
format_var = tk.StringVar(value="Spritesheet")
tk.Radiobutton(root, text="Spritesheet", variable=format_var, value="Spritesheet").grid(row=1, column=1, sticky="w", padx=5)
tk.Radiobutton(root, text="GIF", variable=format_var, value="GIF").grid(row=2, column=1, sticky="w", padx=5)

tk.Label(root, text="Rows (for Spritesheet):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
rows_var = tk.StringVar()
tk.Entry(root, textvariable=rows_var).grid(row=4, column=1, padx=5, pady=5)

tk.Label(root, text="Columns (for Spritesheet):").grid(row=5, column=0, sticky="w", padx=5, pady=5)
columns_var = tk.StringVar()
tk.Entry(root, textvariable=columns_var).grid(row=5, column=1, padx=5, pady=5)

tk.Label(root, text="Frame Count (for GIF):").grid(row=6, column=0, sticky="w", padx=5, pady=5)
frames_var = tk.StringVar()
tk.Entry(root, textvariable=frames_var).grid(row=6, column=1, padx=5, pady=5)

resize_var = tk.BooleanVar(value=False)
resize_check = tk.Checkbutton(root, text="Resize frames", variable=resize_var, command=toggle_resize)
resize_check.grid(row=7, column=0, sticky="w", padx=5, pady=5)

tk.Label(root, text="Width:").grid(row=8, column=0, sticky="w", padx=5, pady=5)
width_var = tk.StringVar()
width_entry = tk.Entry(root, textvariable=width_var, state='disabled')
width_entry.grid(row=8, column=1, padx=5, pady=5)

tk.Label(root, text="Height:").grid(row=9, column=0, sticky="w", padx=5, pady=5)
height_var = tk.StringVar()
height_entry = tk.Entry(root, textvariable=height_var, state='disabled')
height_entry.grid(row=9, column=1, padx=5, pady=5)

# Add trimming checkbox
trim_var = tk.BooleanVar(value=True)
trim_check = tk.Checkbutton(root, text="Smart Trim", variable=trim_var)
trim_check.grid(row=10, column=0, sticky="w", padx=5, pady=5)

# Shift convert button and status label
convert_button = tk.Button(root, text="Convert", command=convert)
convert_button.grid(row=11, column=1, pady=10)

status_label = tk.Label(root, text="")
status_label.grid(row=12, column=0, columnspan=3, pady=5)

root.mainloop()