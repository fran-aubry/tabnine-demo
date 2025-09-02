
import tkinter as tk
from tkinter import filedialog, Frame, Button, Canvas, Label, Menu, Text, messagebox
from PIL import Image, ImageTk
from image_generator import generate_image
import threading

class ImageSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Selector")
        self.root.geometry("800x600")

        # Store image data (path, PhotoImage, widget)
        self.image_data = {}
        self.images_per_row = 5
        self.thumbnail_size = (120, 120)

        # Frame for the canvas and scrollbar
        canvas_frame = Frame(root)
        canvas_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Canvas for thumbnails
        self.canvas = Canvas(canvas_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Frame inside the canvas to hold the thumbnails
        self.thumbnail_frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.thumbnail_frame, anchor="nw")

        self.thumbnail_frame.bind("<Configure>", self.on_frame_configure)

        # Frame for the prompt
        prompt_frame = Frame(root)
        prompt_frame.pack(pady=(0, 10), padx=10, fill=tk.X)

        prompt_label = Label(prompt_frame, text="Prompt:")
        prompt_label.pack(anchor="w")

        self.prompt_text = Text(prompt_frame, height=4)
        self.prompt_text.pack(fill=tk.X, expand=True)

        # Frame for the button
        button_frame = Frame(root)
        button_frame.pack(pady=10)

        # Button to select images
        select_button = Button(button_frame, text="Select Images", command=self.select_images)
        select_button.pack(side=tk.LEFT, padx=5)

        # Button to generate image
        self.generate_button = Button(button_frame, text="Generate Image", command=self.run_generation)
        self.generate_button.pack(side=tk.LEFT, padx=5)

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def select_images(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=(
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("All files", "*.*")
            )
        )

        if file_paths:
            for file_path in file_paths:
                if file_path not in self.image_data:
                    self.add_thumbnail(file_path)
            self.regrid_thumbnails()

    def add_thumbnail(self, file_path):
        try:
            img = Image.open(file_path)
            img.thumbnail(self.thumbnail_size)
            photo_img = ImageTk.PhotoImage(img)
            
            label = Label(self.thumbnail_frame, image=photo_img, bd=2, relief="raised")
            # Bind for right-click on Windows/Linux
            label.bind("<Button-3>", lambda event, p=file_path: self.show_context_menu(event, p))
            # Bind for right-click on macOS
            label.bind("<Button-2>", lambda event, p=file_path: self.show_context_menu(event, p))
            
            # Store all data associated with the image
            self.image_data[file_path] = {
                "photo_img": photo_img,
                "widget": label
            }
        except Exception as e:
            print(f"Error opening {file_path}: {e}")

    def show_context_menu(self, event, file_path):
        """Displays a context menu on right-click."""
        context_menu = Menu(self.root, tearoff=0)
        context_menu.add_command(label="Delete", command=lambda: self.remove_image(file_path))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def remove_image(self, file_path):
        if file_path in self.image_data:
            self.image_data[file_path]["widget"].destroy()
            del self.image_data[file_path]
            self.regrid_thumbnails()

    def run_generation(self):
        """
        Handles the image generation process in a separate thread to keep the UI responsive.
        """
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt.")
            return

        image_paths = list(self.image_data.keys())
        # if not image_paths:
        #     messagebox.showwarning("Warning", "Please select at least one image.")
        #     return

        # Disable button to prevent multiple clicks
        self.generate_button.config(state=tk.DISABLED, text="Generating...")

        # Run the API call in a separate thread
        thread = threading.Thread(target=self.generate_image_thread, args=(image_paths, prompt))
        thread.start()

    def generate_image_thread(self, image_paths, prompt):
        """
        Calls the Gemini API and handles the result.
        This method is intended to be run in a background thread.
        """
        print("Calling Gemini API...")
        # Use the new generate_image function
        from image_generator import generate_image
        result = generate_image(prompt, image_paths)
        print("\n--- Gemini Response ---")
        print(f"Result: {result}")
        print("-----------------------")

        # Since we are in a background thread, we need to schedule UI updates
        # on the main thread using `after`.
        self.root.after(0, self.on_generation_complete, result)

    def on_generation_complete(self, result):
        """
        Actions to perform on the main thread after generation is complete.
        Displays the generated image in a new window or shows an error if no image was created.
        """
        # Re-enable the button
        self.generate_button.config(state=tk.NORMAL, text="Generate Image")

        if result and result.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                # Create a new top-level window to display the image
                new_window = tk.Toplevel(self.root)
                new_window.title("Generated Image")

                img = Image.open(result)
                photo_img = ImageTk.PhotoImage(img)

                img_label = Label(new_window, image=photo_img)
                # Keep a reference to the image to prevent it from being garbage collected
                img_label.image = photo_img
                img_label.pack(padx=10, pady=10)

            except Exception as e:
                messagebox.showerror("Error", f"Could not display image: {e}")
        else:
            # If no image path was returned, inform the user.
            messagebox.showinfo("Generation Info", "No image was generated. Check the console for text output.")


    def regrid_thumbnails(self):
        row, col = 0, 0
        for file_path in self.image_data:
            widget = self.image_data[file_path]["widget"]
            widget.grid(row=row, column=col, padx=5, pady=5)
            
            col += 1
            if col >= self.images_per_row:
                col = 0
                row += 1


def main():
    root = tk.Tk()
    app = ImageSelectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
