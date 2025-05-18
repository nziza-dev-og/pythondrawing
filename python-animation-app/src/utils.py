def load_image(image_path):
    from PIL import Image
    try:
        image = Image.open(image_path)
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def save_animation(animation, output_path):
    try:
        animation.save(output_path, save_all=True, append_images=animation[1:], loop=0)
        print(f"Animation saved to {output_path}")
    except Exception as e:
        print(f"Error saving animation: {e}")

def get_file_extension(file_path):
    import os
    return os.path.splitext(file_path)[1]

def validate_image_file(file_path):
    valid_extensions = ['.png', '.jpg', '.jpeg', '.gif']
    return get_file_extension(file_path) in valid_extensions

def ensure_directory_exists(directory):
    import os
    if not os.path.exists(directory):
        os.makedirs(directory)