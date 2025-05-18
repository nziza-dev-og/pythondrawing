import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageTk, ImageOps, ImageFilter
import numpy as np
import time
import random
import threading
import cv2
import os


class AutoDrawingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatic Image Drawing System")
        
        # Set up the canvas dimensions
        self.canvas_width = 800
        self.canvas_height = 600
        self.bg_color = "white"
        
        # Create main frames
        self.left_frame = tk.Frame(root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        # Create canvases for original and drawing
        self.canvas_frame = tk.Frame(self.left_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Original image canvas (top)
        self.orig_canvas_label = tk.Label(self.canvas_frame, text="Original Image")
        self.orig_canvas_label.pack(pady=(0, 5))
        
        self.orig_canvas = tk.Canvas(self.canvas_frame, 
                                     width=self.canvas_width, 
                                     height=self.canvas_height // 2,
                                     bg=self.bg_color,
                                     bd=2,
                                     relief=tk.SUNKEN)
        self.orig_canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Drawing canvas (bottom)
        self.drawing_canvas_label = tk.Label(self.canvas_frame, text="Drawing Canvas")
        self.drawing_canvas_label.pack(pady=(0, 5))
        
        self.drawing_canvas = tk.Canvas(self.canvas_frame, 
                                       width=self.canvas_width, 
                                       height=self.canvas_height // 2,
                                       bg=self.bg_color,
                                       bd=2,
                                       relief=tk.SUNKEN)
        self.drawing_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initialize images
        self.original_image = None
        self.drawing_image = Image.new("RGB", (self.canvas_width, self.canvas_height // 2), self.bg_color)
        self.draw = ImageDraw.Draw(self.drawing_image)
        
        # Initialize PhotoImages
        self.original_tk_image = None
        self.drawing_tk_image = ImageTk.PhotoImage(self.drawing_image)
        self.drawing_image_id = self.drawing_canvas.create_image(0, 0, anchor=tk.NW, image=self.drawing_tk_image)
        
        # Drawing parameters
        self.drawing_style = tk.StringVar(value="realistic")
        self.drawing_speed = tk.DoubleVar(value=50.0)
        self.detail_level = tk.IntVar(value=50)
        self.is_drawing = False
        self.drawing_thread = None
        
        # Create controls in right frame
        self.create_controls()
    
    def create_controls(self):
        # File controls
        file_frame = tk.LabelFrame(self.right_frame, text="Image")
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(file_frame, text="Load Image", command=self.load_image).pack(fill=tk.X, padx=5, pady=5)
        
        # Drawing style
        style_frame = tk.LabelFrame(self.right_frame, text="Drawing Style")
        style_frame.pack(fill=tk.X, padx=5, pady=5)
        
        styles = [
            ("Realistic", "realistic"),
            ("Sketch", "sketch"),
            ("Contour", "contour"),
            ("Pointillist", "pointillist"),
            ("Cubist", "cubist"),
            ("Abstract", "abstract")
        ]
        
        for text, value in styles:
            tk.Radiobutton(style_frame, text=text, variable=self.drawing_style, 
                          value=value).pack(anchor=tk.W, padx=5, pady=2)
        
        # Speed control
        speed_frame = tk.LabelFrame(self.right_frame, text="Drawing Speed")
        speed_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Scale(speed_frame, from_=1, to=100, orient=tk.HORIZONTAL, 
                variable=self.drawing_speed).pack(fill=tk.X, padx=5, pady=5)
        
        # Detail level control
        detail_frame = tk.LabelFrame(self.right_frame, text="Detail Level")
        detail_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Scale(detail_frame, from_=10, to=100, orient=tk.HORIZONTAL, 
                variable=self.detail_level).pack(fill=tk.X, padx=5, pady=5)
        
        # Action buttons
        action_frame = tk.Frame(self.right_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.start_button = tk.Button(action_frame, text="Start Drawing", command=self.start_drawing)
        self.start_button.pack(fill=tk.X, pady=2)
        
        self.stop_button = tk.Button(action_frame, text="Stop Drawing", command=self.stop_drawing, state=tk.DISABLED)
        self.stop_button.pack(fill=tk.X, pady=2)
        
        self.clear_button = tk.Button(action_frame, text="Clear Canvas", command=self.clear_canvas)
        self.clear_button.pack(fill=tk.X, pady=2)
        
        self.save_button = tk.Button(action_frame, text="Save Drawing", command=self.save_drawing)
        self.save_button.pack(fill=tk.X, pady=2)
        
        # Progress bar
        progress_frame = tk.LabelFrame(self.right_frame, text="Drawing Progress")
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(self.right_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=5)
    
    def load_image(self):
        """Load an image from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Load and resize the image to fit the canvas
            img = Image.open(file_path)
            self.original_image = self.resize_image(img, self.canvas_width, self.canvas_height // 2)
            
            # Convert to PhotoImage and display
            self.original_tk_image = ImageTk.PhotoImage(self.original_image)
            
            # Clear previous image and display new one
            self.orig_canvas.delete("all")
            self.orig_canvas.create_image(
                self.canvas_width // 2,
                self.canvas_height // 4,
                image=self.original_tk_image
            )
            
            # Clear drawing canvas for new drawing
            self.clear_canvas()
            
            self.status_var.set(f"Loaded image: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image:\n{str(e)}")
    
    def resize_image(self, img, width, height):
        """Resize image to fit within dimensions while preserving aspect ratio"""
        img_width, img_height = img.size
        ratio = min(width/img_width, height/img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        return img.resize(new_size, Image.LANCZOS)
    
    def start_drawing(self):
        """Start the automatic drawing process"""
        if self.original_image is None:
            messagebox.showinfo("Info", "Please load an image first.")
            return
        
        if self.is_drawing:
            return
        
        # Update UI
        self.is_drawing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Drawing in progress...")
        
        # Clear canvas for new drawing
        self.clear_canvas()
        
        # Start drawing in a separate thread
        self.drawing_thread = threading.Thread(target=self.drawing_process)
        self.drawing_thread.daemon = True
        self.drawing_thread.start()
    
    def stop_drawing(self):
        """Stop the current drawing process"""
        if not self.is_drawing:
            return
        
        self.is_drawing = False
        self.status_var.set("Drawing stopped.")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def clear_canvas(self):
        """Clear the drawing canvas"""
        self.drawing_image = Image.new("RGB", (self.canvas_width, self.canvas_height // 2), self.bg_color)
        self.draw = ImageDraw.Draw(self.drawing_image)
        self.update_drawing_canvas()
        self.progress['value'] = 0
        self.status_var.set("Canvas cleared.")
    
    def save_drawing(self):
        """Save the current drawing to a file"""
        if self.drawing_image is None:
            messagebox.showinfo("Info", "No drawing to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.drawing_image.save(file_path)
                self.status_var.set(f"Drawing saved to: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save drawing:\n{str(e)}")
    
    def update_drawing_canvas(self):
        """Update the drawing canvas with the current drawing"""
        self.drawing_tk_image = ImageTk.PhotoImage(self.drawing_image)
        self.drawing_canvas.delete("all")
        self.drawing_canvas.create_image(
            self.canvas_width // 2,
            self.canvas_height // 4,
            image=self.drawing_tk_image
        )
        self.root.update_idletasks()
    
    def drawing_process(self):
        """The main drawing process - runs in a separate thread"""
        # Convert PIL Image to numpy array for processing
        img_array = np.array(self.original_image)
        
        # Convert to grayscale for edge detection
        if len(img_array.shape) == 3:  # Color image
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:  # Already grayscale
            gray = img_array
        
        # Get dimensions
        height, width = gray.shape
        
        # Calculate parameters based on settings
        detail = self.detail_level.get() / 100.0
        speed = 101 - self.drawing_speed.get()  # Invert so higher value = faster
        style = self.drawing_style.get()
        
        total_steps = 0
        current_step = 0
        
        # Different drawing techniques based on selected style
        if style == "realistic":
            total_steps = self.draw_realistic(gray, detail, speed)
        elif style == "sketch":
            total_steps = self.draw_sketch(gray, detail, speed)
        elif style == "contour":
            total_steps = self.draw_contour(gray, detail, speed)
        elif style == "pointillist":
            total_steps = self.draw_pointillist(img_array, detail, speed)
        elif style == "cubist":
            total_steps = self.draw_cubist(img_array, detail, speed)
        elif style == "abstract":
            total_steps = self.draw_abstract(img_array, detail, speed)
        
        # Drawing completed
        if self.is_drawing:  # Only update if not manually stopped
            self.progress['value'] = 100
            self.is_drawing = False
            self.status_var.set("Drawing completed.")
            
            # Update UI from main thread
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
    
    def draw_realistic(self, gray_img, detail, speed):
        """Draw in a realistic style using edge-based approaches"""
        # Apply some blurring to reduce noise
        blurred = cv2.GaussianBlur(gray_img, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 30, 100)
        
        # Find contours in the edge image
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours by length (to draw more significant features first)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        # Limit number of contours based on detail level
        max_contours = max(10, int(len(contours) * detail))
        contours = contours[:max_contours]
        
        # Draw tone first (base layer)
        height, width = gray_img.shape
        tone_step = max(1, int((101 - detail * 100) / 10))
        
        # Update progress counter
        total_steps = len(contours) + (height // tone_step) * (width // tone_step)
        current_step = 0
        
        # Draw shading with lines
        for y in range(0, height, tone_step):
            if not self.is_drawing:
                break
                
            for x in range(0, width, tone_step):
                if not self.is_drawing:
                    break
                    
                value = gray_img[y, x]
                if value < 200:  # Only shade darker areas
                    darkness = 255 - value
                    # Make line length proportional to darkness
                    line_length = int(darkness / 255 * 5) + 1
                    
                    # Draw short lines of varying darkness for shading
                    shade_color = tuple([int(value)] * 3)
                    angle = random.uniform(0, 3.14)
                    x1 = x + line_length * np.cos(angle)
                    y1 = y + line_length * np.sin(angle)
                    self.draw.line([(x, y), (int(x1), int(y1))], fill=shade_color, width=1)
                
                current_step += 1
                if current_step % 50 == 0:
                    self.progress['value'] = (current_step / total_steps) * 100
                    self.update_drawing_canvas()
                    time.sleep(0.01 / (speed / 10))
        
        # Draw contours for edges
        for contour in contours:
            if not self.is_drawing:
                break
                
            points = []
            for point in contour:
                x, y = point[0]
                points.append((x, y))
            
            # Only draw if we have enough points
            if len(points) > 1:
                # Draw with varying pressure
                for i in range(len(points) - 1):
                    x1, y1 = points[i]
                    x2, y2 = points[i + 1]
                    
                    # Vary line width slightly for natural look
                    width = random.uniform(0.8, 1.2)
                    self.draw.line([(x1, y1), (x2, y2)], fill="black", width=int(width))
            
            current_step += 1
            if current_step % 5 == 0:
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_drawing_canvas()
                time.sleep(0.05 / (speed / 10))
        
        return total_steps
    
    def draw_sketch(self, gray_img, detail, speed):
        """Draw in a sketchy style with rough lines"""
        # Edge detection with different thresholds for sketch effect
        edges = cv2.Canny(gray_img, 20, 80)
        
        # Find contours in the edge image
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # Limit contours based on detail level
        max_contours = max(10, int(len(contours) * detail))
        selected_contours = random.sample(contours, min(max_contours, len(contours)))
        
        total_steps = len(selected_contours)
        current_step = 0
        
        # Draw contours with sketchy effect
        for contour in selected_contours:
            if not self.is_drawing:
                break
                
            points = []
            for point in contour:
                x, y = point[0]
                points.append((x, y))
            
            # Only draw if we have enough points
            if len(points) > 1:
                # Draw with sketchy effect (multiple overlapping lines)
                for _ in range(random.randint(1, 3)):
                    # Add some random jitter to points for sketchy look
                    jittered_points = []
                    for x, y in points:
                        jx = x + random.randint(-2, 2)
                        jy = y + random.randint(-2, 2)
                        jittered_points.append((jx, jy))
                    
                    # Draw the sketch lines
                    for i in range(len(jittered_points) - 1):
                        x1, y1 = jittered_points[i]
                        x2, y2 = jittered_points[i + 1]
                        
                        # Vary line width for sketchy effect
                        width = random.uniform(0.5, 1.5)
                        self.draw.line([(x1, y1), (x2, y2)], fill="black", width=int(width))
            
            current_step += 1
            self.progress['value'] = (current_step / total_steps) * 100
            
            if current_step % 3 == 0:
                self.update_drawing_canvas()
                time.sleep(0.03 / (speed / 10))
        
        return total_steps
    
    def draw_contour(self, gray_img, detail, speed):
        """Draw only the main contours/outlines of the image"""
        # Apply bilateral filter to reduce noise while keeping edges sharp
        blurred = cv2.bilateralFilter(gray_img, 9, 75, 75)
        
        # Edge detection with higher threshold for cleaner lines
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours by length (to draw more significant features first)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        # Limit number of contours based on detail level
        max_contours = max(5, int(len(contours) * detail))
        contours = contours[:max_contours]
        
        total_steps = len(contours)
        current_step = 0
        
        # Draw clean contours
        for contour in contours:
            if not self.is_drawing:
                break
                
            # Simplify contour based on detail level
            epsilon = (1.1 - detail) * 0.01 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            points = []
            for point in approx:
                x, y = point[0]
                points.append((x, y))
            
            # Close the contour if we have enough points
            if len(points) > 2:
                points.append(points[0])  # Close the shape
                
                # Draw the contour with solid lines
                for i in range(len(points) - 1):
                    x1, y1 = points[i]
                    x2, y2 = points[i + 1]
                    self.draw.line([(x1, y1), (x2, y2)], fill="black", width=2)
            
            current_step += 1
            self.progress['value'] = (current_step / total_steps) * 100
            
            if current_step % 2 == 0:
                self.update_drawing_canvas()
                time.sleep(0.02 / (speed / 10))
        
        return total_steps
    
    def draw_pointillist(self, img_array, detail, speed):
        """Draw using dots/points like pointillism"""
        height, width = img_array.shape[:2]
        
        # Calculate point density based on detail level
        # Higher detail = more points
        point_step = max(1, int((101 - detail * 100) / 5))
        
        total_steps = (height // point_step) * (width // point_step)
        current_step = 0
        
        # Create points
        for y in range(0, height, point_step):
            if not self.is_drawing:
                break
                
            for x in range(0, width, point_step):
                if not self.is_drawing:
                    break
                    
                # Get color at this pixel
                if len(img_array.shape) == 3:  # Color image
                    b, g, r = img_array[y, x]
                    color = (r, g, b)
                else:  # Grayscale
                    v = img_array[y, x]
                    color = (v, v, v)
                
                # Vary point size based on brightness (darker = larger points)
                brightness = sum(color) / len(color)
                max_radius = 3
                radius = max(1, int(max_radius * (1 - brightness / 255)))
                
                # Add some randomness to point placement
                point_x = x + random.randint(-2, 2)
                point_y = y + random.randint(-2, 2)
                
                # Draw the point
                self.draw.ellipse(
                    [(point_x - radius, point_y - radius), 
                     (point_x + radius, point_y + radius)], 
                    fill=color
                )
                
                current_step += 1
                if current_step % 100 == 0:
                    self.progress['value'] = (current_step / total_steps) * 100
                    self.update_drawing_canvas()
                    time.sleep(0.01 / (speed / 10))
        
        return total_steps
    
    def draw_cubist(self, img_array, detail, speed):
        """Draw in a cubist style with geometric shapes"""
        height, width = img_array.shape[:2]
        
        # Number of polygons based on detail level
        num_polygons = int(50 + 450 * detail)
        
        total_steps = num_polygons
        current_step = 0
        
        # Create geometric shapes
        for _ in range(num_polygons):
            if not self.is_drawing:
                break
            
            # Random polygon size based on detail
            size = random.randint(10, max(11, int(30 * detail)))
            
            # Random position
            x = random.randint(0, width - size)
            y = random.randint(0, height - size)
            
            # Get average color in this region
            region = img_array[y:min(y+size, height), x:min(x+size, width)]
            if len(region) == 0:
                continue
                
            if len(img_array.shape) == 3:  # Color image
                avg_color = region.mean(axis=(0, 1))
                color = (int(avg_color[2]), int(avg_color[1]), int(avg_color[0]))
            else:  # Grayscale
                avg_color = region.mean()
                color = (int(avg_color), int(avg_color), int(avg_color))
            
            # Create polygon with 3-5 points
            num_points = random.randint(3, 5)
            points = []
            
            for _ in range(num_points):
                px = x + random.randint(0, size)
                py = y + random.randint(0, size)
                points.append((px, py))
            
            # Fill polygon with color
            self.draw.polygon(points, fill=color, outline=None)
            
            current_step += 1
            if current_step % 10 == 0:
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_drawing_canvas()
                time.sleep(0.01 / (speed / 10))
        
        return total_steps
    
    def draw_abstract(self, img_array, detail, speed):
        """Draw in an abstract style with flowing lines and shapes"""
        height, width = img_array.shape[:2]
        
        # Generate random curves and shapes based on image colors
        num_elements = int(20 + 180 * detail)
        
        total_steps = num_elements
        current_step = 0
        
        # Draw flowing lines that follow color changes
        for _ in range(num_elements):
            if not self.is_drawing:
                break
            
            # Random starting point
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            
            # Get color at this point
            if len(img_array.shape) == 3:  # Color image
                b, g, r = img_array[y, x]
                color = (r, g, b)
                
                # Modify color for artistic effect
                hue_shift = random.randint(-20, 20)
                r = max(0, min(255, r + hue_shift))
                g = max(0, min(255, g + hue_shift))
                b = max(0, min(255, b + hue_shift))
                color = (r, g, b)
            else:  # Grayscale
                v = img_array[y, x]
                color = (v, v, v)
            
            # Decide what type of element to draw
            element_type = random.choice(['curve', 'circle', 'line'])
            
            if element_type == 'curve':
                # Create a flowing curve
                points = [(x, y)]
                
                # Generate a path that follows similar colors
                num_segments = random.randint(5, 15)
                for _ in range(num_segments):
                    # Move in a somewhat random direction
                    angle = random.uniform(0, 2 * 3.14159)
                    distance = random.randint(5, 20)
                    new_x = int(x + distance * np.cos(angle))
                    new_y = int(y + distance * np.sin(angle))
                    
                    # Keep within bounds
                    new_x = max(0, min(width - 1, new_x))
                    new_y = max(0, min(height - 1, new_y))
                    
                    points.append((new_x, new_y))
                    x, y = new_x, new_y
                
                # Draw a smooth curve through the points
                if len(points) > 1:
                    self.draw.line(points, fill=color, width=random.randint(1, 3))
            
            elif element_type == 'circle':
                # Draw a circle or ellipse
                radius = random.randint(5, 25)
                self.draw.ellipse(
                    [(x - radius, y - radius), (x + radius, y + radius)],
                    outline=color,
                    width=random.randint(1, 3)
                )
            
            else:  # line
                # Draw a straight line in a random direction
                angle = random.uniform(0, 2 * 3.14159)
                length = random.randint(20, 80)
                end_x = int(x + length * np.cos(angle))
                end_y = int(y + length * np.sin(angle))
                
                # Keep within bounds
                end_x = max(0, min(width - 1, end_x))
                end_y = max(0, min(height - 1, end_y))
                
                self.draw.line([(x, y), (end_x, end_y)], fill=color, width=random.randint(1, 3))
            
            current_step += 1
            if current_step % 5 == 0:
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_drawing_canvas()
                time.sleep(0.02 / (speed / 10))
        
        return total_steps


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoDrawingSystem(root)
    root.geometry("1200x700")
    root.mainloop()