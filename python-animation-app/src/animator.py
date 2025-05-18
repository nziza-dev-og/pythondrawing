class Animator:
    def __init__(self):
        self.animations = []

    def create_animation(self, images, effects, durations, delays):
        for i in range(len(images)):
            animation_step = {
                'image': images[i],
                'effect': effects[i] if i < len(effects) else None,
                'duration': durations[i] if i < len(durations) else None,
                'delay': delays[i] if i < len(delays) else None
            }
            self.animations.append(animation_step)

    def apply_effects(self):
        for step in self.animations:
            if step['effect']:
                # Apply the effect to the image (pseudo-code)
                step['image'] = step['effect'].apply(step['image'])

    def render_animation(self):
        # Render the animation (pseudo-code)
        for step in self.animations:
            # Display or save the image with the applied effect
            self.display_image(step['image'], step['duration'], step['delay'])

    def display_image(self, image, duration, delay):
        # Logic to display the image for a certain duration with a delay
        pass