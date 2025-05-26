import hashlib
import numpy as np
import cv2
from PIL import Image
import noise  # For Perlin noise

from moviepy import ImageSequenceClip

def mystical_kaleidoscope_generator(input_string, generate_video):

    def create_art(input_string, generate_video):
        if generate_video is False:
            return generate_kaleidoscope_image(input_string, 0, generate_video)
        else:
            frames=[]

            for i in range(60): #60 frames
                img = generate_kaleidoscope_image(input_string, i, generate_video)

                frames.append(np.array(img))
            
            clip = ImageSequenceClip(frames, fps=10)
            clip.write_gif(f'GIFS/mystical_{input_string}.gif', fps=60)
            clip.write_videofile(f'MP4/mystical_{input_string}.mp4', codec="libx264", fps=60)
            clip.close()
            return clip


    def hash_to_params(hash_str):
        # Extracts numerical values from the hash to control the pattern
        params = [int(hash_str[i:i+2], 16) / 255.0 for i in range(0, len(hash_str) - 1, 2)]
        return params

    def generate_perlin_texture(size, hash_str):
        # Generates a Perlin noise texture influenced by the hash
        scale = int(hash_str[:2], 16) / 5 + 5  # Control scale based on hash
        octaves = int(hash_str[2:4], 16) % 5 + 1
        persistence = (int(hash_str[4:6], 16) % 40 + 60) / 100
        lacunarity = (int(hash_str[6:8], 16) % 30 + 70) / 100

        texture = np.zeros((size, size))
        for x in range(size):
            for y in range(size):
                value = noise.pnoise2(x / scale, y / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity)
                texture[x, y] = (value + 1) / 2  # Normalize to [0, 1]
        
        return texture

    def generate_intricate_texture_with_perlin(size, hash_str, i):
        # Combines Perlin noise with wave interference for a complex texture
        params = hash_to_params(hash_str)
        
        # Creates wave interference pattern
        animator =(params[8]+params[19])* np.sin((i) * np.pi/30)
        animator2 = (params[13]+params[2]) * np.cos((i) * np.pi/30)

        x = np.linspace(-2, 2, size)
        y = np.linspace(-2, 2, size)
        X, Y = np.meshgrid(x, y)

        wave1 = ((X + animator))**2 + (Y)**2  - animator2 - (params[0]+params[16]+3 * params[10])
        wave2 = ((X))**2 + (Y - params[10]*animator2)**2 

        combined_wave = np.sin(wave1 + wave2) * params[1] * params[3] * params[24] * np.cos(wave2) 

        # Combines the waves 
        texture = np.multiply(combined_wave, 1)

        # Converts to grayscale intensity
        img = np.uint8(255 * (texture - texture.min()) / (texture.max() - texture.min()))

        # Creates intricate color variations
        r = ((img * (params[10]+params[26]) + animator2**3 * 1.5 + 50) % 255 ).clip(200, 255)
        g = ((img * (params[11]+params[30]) + animator + 3*animator**2 * 0.5 + 50) % 255).clip(200, 255)
        b = ((img * (params[12]+params[31]) + animator2 + animator * 0.9 + 50) % 255).clip(200, 255)
        color_img = np.stack([r, g, b], axis=-1).astype(np.uint8)

        return color_img

    def apply_kaleidoscope_effect(image, hash_str):
        # Creates kaleidoscope effect
        size = image.shape[0]
        center = size // 2
        kaleidoscope = np.zeros_like(image)

        params = hash_to_params(hash_str)
        mirrors = int(params[7]*10+2) if (params[7]*10 > 1) else int(params[7]*10+3)

        # Applies reflections
        for i in range(mirrors):
            angle = i * (360/mirrors)
            M = cv2.getRotationMatrix2D((center, center), angle, 1)
            rotated = cv2.warpAffine(image, M, (size, size))
            kaleidoscope = np.maximum(kaleidoscope, rotated)

        return kaleidoscope


    def apply_sharpening(image):
        """Apply a sharpening filter to make the lines sharper."""
        kernel_sharpen = np.array([[-1, -1, -1], [-1, 9,-1], [-1, -1, -1]])  # Simple sharpening kernel
        sharpened = cv2.filter2D(image, -1, kernel_sharpen)
        kernel_edges = np.array([[ 0,  1,  0], [ 1, -4,  1], [ 0,  1,  0]])
        final_image = cv2.filter2D(sharpened, -1, kernel_edges)
        return final_image

    def apply_saturation_boost(image, factor=1.5):
        """Increase the saturation to make colors more vibrant."""
        # Convert the image to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Scale the saturation channel
        hsv[..., 1] = hsv[..., 1] * factor
        
        # Clip to ensure saturation doesn't go over 255
        hsv[..., 1] = np.clip(hsv[..., 1], 0, 255)
        
        # Convert back to BGR color space
        vibrant_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        return vibrant_image

    def apply_circular_mask(image):
        # Applies a circular mask to keep only the center of the image
        height, width = image.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)

        # Creates a white filled circle in the center
        center = (width // 2, height // 2)
        radius = min(width, height) // 2  # Use half of the smallest dimension
        cv2.circle(mask, center, radius, 255, -1)  # -1 fills the circle

        # Applies the mask: keep only the circle
        masked_image = cv2.bitwise_and(image, image, mask=mask)

        return masked_image

    def generate_kaleidoscope_image(text, i, generate_video, size=720):
        # Generates the final kaleidoscope image based on text input
        hash_str = hashlib.sha256(text.encode()).hexdigest()
        base_pattern = generate_intricate_texture_with_perlin(size, hash_str, i)
        kaleidoscope_image = apply_kaleidoscope_effect(base_pattern, hash_str)

        # Sharpens the image and boost color saturation
        sharpened_image = apply_sharpening(kaleidoscope_image)
        vibrant_image = apply_saturation_boost(sharpened_image)

        # Circular cutout
        final_image = apply_circular_mask(vibrant_image)

        # Converts to PIL Image and Save
        img = Image.fromarray(final_image)
        if generate_video is False:
            img.save(f'PNG/mystical_{text}.png')

        return img


    return create_art(input_string, generate_video)
