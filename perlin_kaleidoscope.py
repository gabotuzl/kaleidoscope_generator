import hashlib
import numpy as np
import cv2
from PIL import Image
import noise

from moviepy import ImageSequenceClip

def perlin_kaleidoscope_generator(input_string, generate_video):

    def create_art(input_string, generate_video):
        if generate_video is False:
            return generate_kaleidoscope_image(input_string, 0, generate_video)
        else:
            frames=[]

            for i in range(60): #60 frames
                img = generate_kaleidoscope_image(input_string, i, generate_video)

                frames.append(np.array(img))
            
            clip = ImageSequenceClip(frames, fps=10)
            clip.write_gif(f'GIFS/perlin_{input_string}.gif', fps=60)
            clip.write_videofile(f'MP4/perlin_{input_string}.mp4', codec="libx264", fps=60)
            clip.close()
            return clip

    def hash_to_colors(hash_str, j):
        # Converts SHA-256 hash to RGB color tuples
        colors = []
        for i in range(0, len(hash_str) - 5, 6):  # Ensures full 6-char slices
            r = min(255, max(0, int(hash_str[i:i+2], 16) + 10 * j))
            g = min(255, max(0, int(hash_str[i+2:i+4], 16) + 10 * j))
            b = min(255, max(0, int(hash_str[i+4:i+6], 16) + 10 * j))
            colors.append((r, g, b))
        return colors

    def hash_to_params(hash_str):
        # Extracts numerical values from the hash to control the pattern 
        params = [int(hash_str[i:i+2], 16) / 255.0 for i in range(0, len(hash_str) - 1, 2)]
        return params

    def generate_perlin_texture(size, hash_str, i):
        # Creates a Perlin noise texture influenced by the hash and animated over time 
        z_offset = np.sin(np.pi * i / 30)
        
        scale = int(hash_str[:2], 16) / 5 + 5  # Scale of noise
        octaves = int(hash_str[2:4], 16) % 5 + 1
        persistence = (int(hash_str[4:6], 16) % 40 + 60) / 100
        lacunarity = (int(hash_str[6:8], 16) % 30 + 70) / 100

        texture = np.zeros((size, size, 3), dtype=np.uint8)
        colors = hash_to_colors(hash_str, i)

        for x in range(size):
            for y in range(size):
                value = noise.pnoise3(x / scale, y / scale, z_offset,  # Adding z_offset for animation
                                    octaves=octaves, persistence=persistence, lacunarity=lacunarity)
                color_idx = int((value + 1) / 2 * (len(colors) - 1))  # Map noise to color index
                texture[x, y] = colors[color_idx]

        return texture

    def apply_kaleidoscope_effect(image, hash_str):
        # Creates kaleidoscope effect 
        size = image.shape[0]
        center = size // 2
        kaleidoscope = np.zeros_like(image)

        params = hash_to_params(hash_str)
        mirrors = int(params[7]*10+1)

        # Applies reflections  
        for i in range(mirrors):
            angle = i * (360/mirrors)
            M = cv2.getRotationMatrix2D((center, center), angle, 1)
            rotated = cv2.warpAffine(image, M, (size, size))
            kaleidoscope = np.maximum(kaleidoscope, rotated)

        return kaleidoscope

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

    def apply_sharpening(image):
        # Applies a sharpening filter to make the lines sharper 
        kernel_sharpen = np.array([[-1, -1, -1], [-1, 9,-1], [-1, -1, -1]])  # Simple sharpening kernel
        sharpened = cv2.filter2D(image, -1, kernel_sharpen)
        kernel_edges = np.array([[ 0,  1,  0], [ 1, -4,  1], [ 0,  1,  0]])
        final_image = cv2.filter2D(sharpened, -1, kernel_edges)
        return final_image

    def generate_kaleidoscope_image(text, i, generate_video, size=720):
        # Generate the final kaleidoscope image based on text input
        hash_str = hashlib.sha256(text.encode()).hexdigest()
        base_pattern = generate_perlin_texture(size, hash_str, i)
        kaleidoscope_image = apply_kaleidoscope_effect(base_pattern, hash_str)

        # Convert to PIL Image and Save
        sharpened_image = apply_sharpening(kaleidoscope_image)
        final_image = apply_circular_mask(sharpened_image)
        img = Image.fromarray(final_image)

        if generate_video is False:
            img.save(f'PNG/perlin_{text}.png')
            

        # img.show()
        return img

    
    return create_art(input_string, generate_video)
