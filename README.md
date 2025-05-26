# Kaleidoscope Generator

This repository contains a deterministic and unique kaleidoscope generator that creates intricate visual patterns based on any input string of characters, making each pattern truly one-of-a-kind. It outputs both an image and a GIF.

<div style="text-align: center;">
  ![Brutalist: Optimal](Examples/brutalist_Optimal.gif)
</div>


## How It Works

- The generator hashes the input string to produce a unique value.
- This hash is converted into numerical data.
- The numbers are processed through a series of nonlinear mathematical functions to generate complex patterns.
- These patterns are then mirrored in multiple sections to produce a kaleidoscope effect.
- Perlin noise is incorporated to add organic variations and enhance visual complexity.

## Usage

1. Clone the repository:

```bash
git clone https://github.com/gabotuzl/kaleidoscope_generator
```

2. Navigate into the project directory:

```bash
cd kaleidoscope_generator
```

3. Run the GUI script:

```bash
python kaleidoscope_gui.py
```

4. In the GUI:
   - Select your preferred kaleidoscope style.
   - Choose whether or not to generate a video (GIF) (Generating a video will take more time).
   - Enter any sequence of characters in the text box.
   
5. Click the button to generate your kaleidoscope pattern. Wait a moment (a couple of minutes or less), and then enjoy your unique creation!

## Dependencies

Make sure to install the following Python packages before running the program:

- PIL (Pillow)
- moviepy
- opencv-python (cv2)
- numpy
- noise

You can install them using pip:

```bash
pip install pillow moviepy opencv-python numpy noise
```

## Notes

- Feel free to customize parameters within `kaleidoscope_gui.py` to explore different visual styles.
- The generator's deterministic nature ensures that the same input string will always produce the same pattern.
- The output GIFs will be more visually pleasing if they are slowed down. The output as GIF is to preserve the color vibrance as this is lost in MP4 compression.

Enjoy creating mesmerizing kaleidoscopic art with your own personalized inputs!
