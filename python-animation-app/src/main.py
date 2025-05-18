from animator import Animator

def main():
    print("Welcome to the Python Animation App!")
    
    # Get user input for images
    image_paths = input("Please enter the paths of the images you want to animate, separated by commas: ").split(',')
    image_paths = [path.strip() for path in image_paths]
    
    # Create an instance of Animator
    animator = Animator()
    
    # Get user-defined effects and durations
    effects = input("Enter the effects you want to apply (fade_in, slide_in, bounce), separated by commas: ").split(',')
    effects = [effect.strip() for effect in effects]
    
    duration = float(input("Enter the duration for the animation (in seconds): "))
    delay = float(input("Enter the delay between animations (in seconds): "))
    
    # Create and render the animation
    animator.create_animation(image_paths, effects, duration, delay)
    animator.render_animation()

if __name__ == "__main__":
    main()