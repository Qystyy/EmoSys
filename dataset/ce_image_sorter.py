import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import shutil
import sys
from pathlib import Path
import re
from collections import deque

class EmotionImageSorterGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Emotion Image Sorter")
        self.root.geometry("1600x1000")
        self.root.minsize(900, 700)
        
        # Configuration
        self.data_folder = "data"
        self.raw_folder = "data/raw"
        self.sorted_folder = "data/sorted"
        self.output_folder = "compound_emotions"
        
        # Game settings
        self.images_per_row = 8
        self.images_per_col = 4
        self.total_images_display = self.images_per_row * self.images_per_col  # 32 images
        self.thumbnail_size = 100  # Size of thumbnails in pixels
        
        # Compound emotion categories
        self.compound_emotions = [
            "Neutral",
            "Sad",
            "Surprised",
            "Disgusted",
            "Fearful",
            "Delighted",    #   "Happy-Surprised",
            "Thrilled",     #   "Happy-Fearful",
            #"Bittersweet",  #   "Happy-Sad",
            #"Smug",         #   "Happy-Disgusted",
            "Bitter",       #   "Sad-Angry",
            "Appalled",     #   "Sad-Surprised",
            #"Scornful",     #   "Sad-Disgusted",
            #"Agitated",     #   "Angry-Fearful", [drop bcs hard to sort data + no clear visual + better with video]
            "Outraged",     #   "Angry-Surprised",
            "Infuriated",   #   "Angry-Disgusted",
            "Startled",     #   "Fearful-Surprised",
            #"Horrified",    #   "Fearful-Disgusted",
            "to delete"
        ]
        
        # Data management
        self.all_images = deque()  # All images from raw folder
        self.display_images = []  # Current 20 images being displayed
        self.image_buttons = []  # Button references for grid
        self.image_cache = {}  # Cache for quick display
        self.rename_counter = {}
        self.emotion_counters = {}
        self.sorted_count = 0
        self.selected_images = set()  # Track selected image indices
        
        # Settings
        self.enable_renaming = tk.BooleanVar(value=True)
        self.rename_mode = tk.StringVar(value="auto")
        self.enable_resizing = tk.BooleanVar(value=True)
        self.resize_size = tk.IntVar(value=160)
        self.resize_mode = tk.StringVar(value="stretch")
        self.resize_color = tk.StringVar(value="black")
        self.common_sizes = [48, 64, 96, 128, 160, 224, 256, 512]
        
        self.setup_ui()
        self.load_all_images()
        self.create_output_folders()
        self.initialize_rename_counters()
        self.fill_display_images()
        self.refresh_grid()
        self.update_counters()
    
    def setup_ui(self):
        """Create the UI layout"""
        
        # Top control panel
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Title and stats
        title_frame = ttk.Frame(top_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Emotion Image Sorter", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        self.selection_label = ttk.Label(title_frame, text="", font=("Arial", 10, "bold"), foreground="green")
        self.selection_label.pack(side=tk.RIGHT, padx=(0, 20))
        
        self.status_label = ttk.Label(title_frame, text="", font=("Arial", 10))
        self.status_label.pack(side=tk.RIGHT)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(top_frame, text="Quick Settings", padding=10)
        settings_frame.pack(fill=tk.X)
        
        col1 = ttk.Frame(settings_frame)
        col1.pack(fill=tk.X, side=tk.LEFT, padx=10)
        
        ttk.Checkbutton(col1, text="Auto-resize (160x160)", variable=self.enable_resizing).pack(anchor=tk.W)
        ttk.Checkbutton(col1, text="Auto-rename", variable=self.enable_renaming).pack(anchor=tk.W)
        
        col2 = ttk.Frame(settings_frame)
        col2.pack(fill=tk.X, side=tk.LEFT, padx=10)
        
        ttk.Button(col2, text="🔄 Refresh Grid", command=self.refresh_grid).pack(side=tk.LEFT, padx=5)
        ttk.Button(col2, text="📂 Open Output", command=self.open_output_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(col2, text="📊 Statistics", command=self.show_statistics).pack(side=tk.LEFT, padx=5)
        
        # Selection control panel
        selection_control_frame = ttk.Frame(settings_frame)
        selection_control_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(selection_control_frame, text="✓ Clear Selection", command=self.clear_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(selection_control_frame, text="➕ Select All", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(selection_control_frame, text="😊 Choose Emotion for Selected", command=self.show_emotion_selection).pack(side=tk.LEFT, padx=5)
        
        # Main content - grid and counters
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side - Image grid
        grid_frame = ttk.LabelFrame(content_frame, text="Select Images to Sort (Click image → Choose emotion)", padding=5)
        grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 5))
        
        # Canvas for scrollable grid
        canvas = tk.Canvas(grid_frame, bg="gray20", highlightthickness=0)
        scrollbar = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create image grid
        self.grid_frame = scrollable_frame
        self.canvas = canvas
        for row in range(self.images_per_col):
            row_buttons = []
            for col in range(self.images_per_row):
                btn = tk.Button(
                    self.grid_frame,
                    width=self.thumbnail_size,
                    height=self.thumbnail_size,
                    bg="gray30",
                    activebackground="gray40",
                    command=lambda r=row, c=col: self.select_image(r, c)
                )
                btn.grid(row=row, column=col, padx=2, pady=2)
                row_buttons.append(btn)
            self.image_buttons.append(row_buttons)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right side - Counter and info
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)
        
        # Counter display with scrollbar
        counter_frame = ttk.LabelFrame(right_frame, text="Images per Emotion", padding=10)
        counter_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        counter_scrollbar = ttk.Scrollbar(counter_frame)
        counter_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.counter_label = tk.Text(
            counter_frame,
            height=18,
            width=32,
            font=("Courier", 9),
            yscrollcommand=counter_scrollbar.set,
            state=tk.DISABLED,
            bg="gray10",
            fg="white",
            wrap=tk.NONE
        )
        
        self.counter_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        counter_scrollbar.config(command=self.counter_label.yview)
        
        # Progress info
        info_frame = ttk.LabelFrame(right_frame, text="Progress", padding=10)
        info_frame.pack(fill=tk.X)
        
        self.progress_label = ttk.Label(info_frame, text="", font=("Arial", 9))
        self.progress_label.pack(anchor=tk.W, fill=tk.BOTH)
        
        # Bottom button
        def load_more_with_refresh():
            self.selected_images.clear()
            self.fill_display_images()
            self.refresh_grid()
            self.update_selection_label()
        
        ttk.Button(self.root, text="🔄 Load More Images", command=load_more_with_refresh).pack(fill=tk.X, padx=10, pady=10)
    
    def load_all_images(self):
        """Load all image filenames from raw folder"""
        if not os.path.exists(self.raw_folder):
            os.makedirs(self.raw_folder)
            messagebox.showwarning("Warning", f"Created '{self.raw_folder}' folder. Please add images there!")
            return
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
        images = [
            f for f in os.listdir(self.raw_folder)
            if os.path.splitext(f)[1].lower() in image_extensions
        ]
        
        self.all_images = deque(sorted(images))
        
        if not self.all_images:
            messagebox.showwarning("Warning", f"No images found in '{self.raw_folder}' folder!")
    
    def fill_display_images(self):
        """Fill display_images with up to 20 images from all_images"""
        while len(self.display_images) < self.total_images_display and len(self.all_images) > 0:
            self.display_images.append(self.all_images.popleft())
        
        # Clear old selections when loading new images
        self.selected_images.clear()
        self.update_progress()
    
    def refresh_grid(self):
        """Refresh the image grid display"""
        for row_idx, row_buttons in enumerate(self.image_buttons):
            for col_idx, btn in enumerate(row_buttons):
                idx = row_idx * self.images_per_row + col_idx
                
                if idx < len(self.display_images):
                    image_name = self.display_images[idx]
                    image_path = os.path.join(self.raw_folder, image_name)
                    
                    try:
                        # Load and resize image
                        img = Image.open(image_path)
                        img.thumbnail((self.thumbnail_size, self.thumbnail_size), Image.Resampling.LANCZOS)
                        
                        # Add padding to make square thumbnail
                        square_img = Image.new('RGB', (self.thumbnail_size, self.thumbnail_size), (40, 40, 40))
                        offset = ((self.thumbnail_size - img.width) // 2, (self.thumbnail_size - img.height) // 2)
                        square_img.paste(img, offset)
                        
                        photo = ImageTk.PhotoImage(square_img)
                        btn.config(image=photo, text="", compound=tk.CENTER)
                        btn.image = photo
                        
                        # Apply selection styling if selected
                        if idx in self.selected_images:
                            btn.config(relief=tk.SUNKEN, bd=3, bg="green")
                        else:
                            btn.config(relief=tk.RAISED, bd=2, bg="gray30")
                        
                    except Exception as e:
                        btn.config(text="❌\nError", bg="gray20")
                else:
                    # Empty slot
                    btn.config(image="", text="", bg="gray20", relief=tk.FLAT)
                    btn.image = None
    
    def select_image(self, row, col):
        """Toggle image selection"""
        idx = row * self.images_per_row + col
        
        if idx >= len(self.display_images):
            messagebox.showinfo("Info", "No image here. Load more images or refresh!")
            return
        
        # Toggle selection
        if idx in self.selected_images:
            self.selected_images.remove(idx)
        else:
            self.selected_images.add(idx)
        
        # Update button appearance
        self.update_selection_ui()
        self.update_selection_label()
    
    def update_selection_ui(self):
        """Update button appearance based on selection"""
        for row_idx, row_buttons in enumerate(self.image_buttons):
            for col_idx, btn in enumerate(row_buttons):
                idx = row_idx * self.images_per_row + col_idx
                
                if idx < len(self.display_images):
                    if idx in self.selected_images:
                        # Highlight selected
                        btn.config(relief=tk.SUNKEN, bd=3, bg="green")
                    else:
                        # Normal
                        btn.config(relief=tk.RAISED, bd=2, bg="gray30")
    
    def update_selection_label(self):
        """Update selection counter in title"""
        count = len(self.selected_images)
        if count > 0:
            self.selection_label.config(text=f"✓ {count} image(s) selected")
        else:
            self.selection_label.config(text="")
    
    def clear_selection(self):
        """Clear all selected images"""
        self.selected_images.clear()
        self.update_selection_ui()
        self.update_selection_label()
    
    def select_all(self):
        """Select all visible images"""
        self.selected_images = set(range(len(self.display_images)))
        self.update_selection_ui()
        self.update_selection_label()
    
    def show_emotion_selection(self):
        """Show emotion selection for selected images"""
        if not self.selected_images:
            messagebox.showwarning("Warning", "Please select at least one image first!")
            return
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Choose Emotion for Selected Images")
        popup.geometry("400x500")
        popup.grab_set()
        
        # Info
        count = len(self.selected_images)
        ttk.Label(popup, text=f"Sorting {count} image(s) to:", font=("Arial", 11, "bold")).pack(pady=10)
        
        # Emotion selection frame
        emotion_frame = ttk.LabelFrame(popup, text="Select ONE Emotion", padding=10)
        emotion_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create buttons for each emotion (grid layout)
        for idx, emotion in enumerate(self.compound_emotions):
            btn = ttk.Button(
                emotion_frame,
                text=emotion,
                command=lambda e=emotion: self.process_selected_images(e, popup)
            )
            btn.grid(row=idx // 3, column=idx % 3, padx=8, pady=8, sticky="ew")
        
        # Configure columns to expand
        for i in range(3):
            emotion_frame.columnconfigure(i, weight=1)
        # Calculate how many rows the emotions occupy
        emotion_rows = (len(self.compound_emotions) + 2) // 3

        # Delete button
        ttk.Button(
            emotion_frame,
            text="🗑 Delete Image",
            command=lambda: self.delete_and_close(popup)
        ).grid(
            row=emotion_rows,
            column=0,
            columnspan=3,
            padx=5,
            pady=10,
            sticky="ew"
        )

        # Cancel button
        ttk.Button(
            emotion_frame,
            text="Cancel",
            command=popup.destroy
        ).grid(
            row=emotion_rows + 1,
            column=0,
            columnspan=3,
            padx=5,
            pady=5,
            sticky="ew"
        )
        
    
    def process_selected_images(self, emotion, popup):
        """Process all selected images to one emotion"""
        popup.destroy()
        
        if not self.selected_images:
            messagebox.showwarning("Warning", "No images selected!")
            return
        
        selected_indices = sorted(self.selected_images, reverse=True)
        processed_count = 0
        failed_count = 0
        
        try:
            for idx in selected_indices:
                if idx >= len(self.display_images):
                    continue
                
                image_name = self.display_images[idx]
                image_path = os.path.join(self.raw_folder, image_name)
                
                if not os.path.exists(image_path):
                    failed_count += 1
                    continue
                
                try:
                    # Get new filename
                    new_filename = self.get_new_filename(emotion, image_name)
                    
                    if new_filename is None:
                        continue
                    
                    emotion_dest_path = os.path.join(self.output_folder, emotion, new_filename)
                    emotion_dest_path = self.get_next_available_filename(emotion_dest_path)
                    
                    # Apply resizing if enabled
                    if self.enable_resizing.get():
                        target_size = self.resize_size.get()
                        resize_mode = self.resize_mode.get()
                        resize_color = self.resize_color.get()
                        
                        resized_img = self.apply_resizing(image_path, target_size, resize_mode, resize_color)
                        if resized_img is None:
                            failed_count += 1
                            continue
                        
                        resized_img.save(emotion_dest_path, quality=95)
                    else:
                        shutil.copy2(image_path, emotion_dest_path)
                    
                    # Move to sorted folder
                    sorted_dest_path = os.path.join(self.sorted_folder, image_name)
                    sorted_dest_path = self.get_next_available_filename(sorted_dest_path)
                    shutil.move(image_path, sorted_dest_path)
                    
                    processed_count += 1
                    self.sorted_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    continue
            
            # Remove processed images from display (in reverse order to maintain indices)
            for idx in selected_indices:
                if idx < len(self.display_images):
                    self.display_images.pop(idx)
            
            # Fill with new images
            while len(self.display_images) < self.total_images_display and len(self.all_images) > 0:
                self.display_images.append(self.all_images.popleft())
            
            # Clear selection and refresh
            self.selected_images.clear()
            self.refresh_grid()
            self.update_counters()
            self.update_progress()
            self.update_selection_label()
            
            # Show result message
            result_msg = f"Successfully sorted {processed_count} image(s) to {emotion}!"
            if failed_count > 0:
                result_msg += f"\n({failed_count} image(s) failed)"
            
            messagebox.showinfo("Success", result_msg)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing images: {str(e)}")
    

    def process_and_close(self, emotion, row, col, popup):
        """Process the image and close popup"""
        popup.destroy()
        
        try:
            image_name = self.current_select_image
            image_path = os.path.join(self.raw_folder, image_name)
            
            if not os.path.exists(image_path):
                messagebox.showerror("Error", "Image file not found!")
                return
            
            # Get new filename
            new_filename = self.get_new_filename(emotion, image_name)
            
            if new_filename is None:
                return
            
            emotion_dest_path = os.path.join(self.output_folder, emotion, new_filename)
            emotion_dest_path = self.get_next_available_filename(emotion_dest_path)
            
            # Apply resizing if enabled
            if self.enable_resizing.get():
                target_size = self.resize_size.get()
                resize_mode = self.resize_mode.get()
                resize_color = self.resize_color.get()
                
                resized_img = self.apply_resizing(image_path, target_size, resize_mode, resize_color)
                if resized_img is None:
                    return
                
                resized_img.save(emotion_dest_path, quality=95)
            else:
                shutil.copy2(image_path, emotion_dest_path)
            
            # Move to sorted folder
            sorted_dest_path = os.path.join(self.sorted_folder, image_name)
            sorted_dest_path = self.get_next_available_filename(sorted_dest_path)
            shutil.move(image_path, sorted_dest_path)
            
            self.sorted_count += 1
            
            # Remove from display and load new image
            self.display_images.pop(self.current_select_idx)
            if len(self.all_images) > 0:
                self.display_images.append(self.all_images.popleft())
            
            self.refresh_grid()
            self.update_counters()
            self.update_progress()
            
            # Visual feedback
            self.image_buttons[row][col].config(relief=tk.SUNKEN, bg="green")
            self.root.after(200, lambda: self.refresh_grid())
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not process image: {str(e)}")
    
    def delete_and_close(self, popup):
        """Delete image and close popup"""
        if messagebox.askyesno("Confirm", "Delete this image? Cannot be undone!"):
            popup.destroy()
            
            try:
                image_path = os.path.join(self.raw_folder, self.current_select_image)
                os.remove(image_path)
                
                self.display_images.pop(self.current_select_idx)
                if len(self.all_images) > 0:
                    self.display_images.append(self.all_images.popleft())
                
                self.refresh_grid()
                self.update_progress()
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete image: {str(e)}")
    
    def get_new_filename(self, emotion, original_filename):
        """Generate new filename based on renaming mode"""
        file_extension = os.path.splitext(original_filename)[1].lower()
        
        if not self.enable_renaming.get():
            return original_filename
        
        if self.rename_mode.get() == "auto":
            if emotion not in self.rename_counter:
                self.rename_counter[emotion] = 1
            else:
                self.rename_counter[emotion] += 1
            
            new_name = f"{emotion}_{self.rename_counter[emotion]:04d}{file_extension}"
            return new_name
        else:
            while True:
                custom_name = simpledialog.askstring(
                    "Rename Image",
                    f"Enter new name for:\n{original_filename}",
                    parent=self.root
                )
                
                if custom_name is None:
                    return None
                
                if not custom_name.strip():
                    return original_filename
                
                clean_name = os.path.splitext(custom_name)[0]
                clean_name = re.sub(r'[<>:"/\\|?*]', '', clean_name)
                
                if not clean_name:
                    messagebox.showwarning("Invalid", "Please enter a valid filename!")
                    continue
                
                new_name = f"{clean_name}{file_extension}"
                return new_name
    
    def resize_image_with_padding(self, image_path, target_size, padding_color="black"):
        """Resize image with padding"""
        img = Image.open(image_path)
        
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (0, 0, 0) if padding_color == "black" else (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        
        bg_color = (0, 0, 0) if padding_color == "black" else (255, 255, 255)
        new_img = Image.new('RGB', (target_size, target_size), bg_color)
        
        offset_x = (target_size - img.width) // 2
        offset_y = (target_size - img.height) // 2
        new_img.paste(img, (offset_x, offset_y))
        
        return new_img
    
    def resize_image_stretch(self, image_path, target_size):
        """Resize image by stretching"""
        img = Image.open(image_path)
        
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (0, 0, 0))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        resized_img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        return resized_img
    
    def apply_resizing(self, image_path, target_size, resize_mode, resize_color):
        """Apply resizing based on mode"""
        try:
            if resize_mode == "pad":
                return self.resize_image_with_padding(image_path, target_size, resize_color)
            else:
                return self.resize_image_stretch(image_path, target_size)
        except Exception as e:
            messagebox.showerror("Resize Error", f"Could not resize image: {str(e)}")
            return None
    
    def get_next_available_filename(self, dest_path):
        """Get next available filename if file exists"""
        if not os.path.exists(dest_path):
            return dest_path
        
        base_path = os.path.splitext(dest_path)[0]
        extension = os.path.splitext(dest_path)[1]
        
        counter = 1
        while os.path.exists(f"{base_path}_{counter}{extension}"):
            counter += 1
        
        return f"{base_path}_{counter}{extension}"
    
    def create_output_folders(self):
        """Create output folder structure"""
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        if not os.path.exists(self.sorted_folder):
            os.makedirs(self.sorted_folder)
        
        for emotion in self.compound_emotions:
            emotion_path = os.path.join(self.output_folder, emotion)
            if not os.path.exists(emotion_path):
                os.makedirs(emotion_path)
    
    def initialize_rename_counters(self):
        """Initialize counters from existing files"""
        self.rename_counter = {}
        
        if not os.path.exists(self.output_folder):
            return
        
        for emotion_folder in os.listdir(self.output_folder):
            emotion_path = os.path.join(self.output_folder, emotion_folder)
            
            if os.path.isdir(emotion_path):
                max_count = 0
                
                for filename in os.listdir(emotion_path):
                    match = re.search(r'_(\d+)\.', filename)
                    if match:
                        number = int(match.group(1))
                        max_count = max(max_count, number)
                
                self.rename_counter[emotion_folder] = max_count
    
    def update_counters(self):
        """Update emotion category counters"""
        self.emotion_counters = {}
        
        if not os.path.exists(self.output_folder):
            return
        
        for emotion in self.compound_emotions:
            emotion_path = os.path.join(self.output_folder, emotion)
            if os.path.isdir(emotion_path):
                images = [f for f in os.listdir(emotion_path)
                         if os.path.splitext(f)[1].lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}]
                self.emotion_counters[emotion] = len(images)
            else:
                self.emotion_counters[emotion] = 0
        
        # Create counter display text
        counter_text = ""
        total = 0
        for emotion in sorted(self.compound_emotions):
            count = self.emotion_counters.get(emotion, 0)
            total += count
            bar_length = count // 5
            bar = "█" * min(bar_length, 10)
            counter_text += f"{emotion:12} {bar:10} {count:4}\n"
        
        counter_text += f"{'-'*32}\n"
        counter_text += f"{'TOTAL':12} {' '*10} {total:4}"
        
        self.counter_label.config(state=tk.NORMAL)
        self.counter_label.delete(1.0, tk.END)
        self.counter_label.insert(1.0, counter_text)
        self.counter_label.config(state=tk.DISABLED)
    
    def update_progress(self):
        """Update progress display"""
        raw_remaining = len(self.display_images) + len(self.all_images)
        progress_text = f"Sorted: {self.sorted_count}\nRemaining: {raw_remaining}\nOn Display: {len(self.display_images)}"
        self.progress_label.config(text=progress_text)
        self.status_label.config(text=f"Sorted: {self.sorted_count} | Remaining: {raw_remaining} | On Grid: {len(self.display_images)}/20")
    
    def open_output_folder(self):
        """Open output folder"""
        if not os.path.exists(self.output_folder):
            messagebox.showwarning("Warning", "Output folder doesn't exist yet!")
            return
        
        if os.name == 'nt':
            os.startfile(self.output_folder)
        elif os.name == 'posix':
            os.system(f"open '{self.output_folder}'" if sys.platform == "darwin" else f"xdg-open '{self.output_folder}'")
    
    def show_statistics(self):
        """Show statistics window"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistics")
        stats_window.geometry("400x300")
        
        text_widget = tk.Text(stats_window, font=("Courier", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        stats_text = "EMOTION DISTRIBUTION\n"
        stats_text += "=" * 40 + "\n\n"
        
        total = sum(self.emotion_counters.values())
        for emotion in sorted(self.compound_emotions):
            count = self.emotion_counters.get(emotion, 0)
            percentage = (count / total * 100) if total > 0 else 0
            stats_text += f"{emotion:15} : {count:3} ({percentage:5.1f}%)\n"
        
        stats_text += "\n" + "=" * 40 + "\n"
        stats_text += f"{'TOTAL':15} : {total:3} (100.0%)\n"
        stats_text += f"\nRemaining: {len(self.display_images) + len(self.all_images)}\n"
        
        text_widget.insert(1.0, stats_text)
        text_widget.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = EmotionImageSorterGame(root)
    root.mainloop()