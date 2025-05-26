import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
from brutalist_kaleidoscope import brutalist_kaleidoscope_generator
from perlin_kaleidoscope import perlin_kaleidoscope_generator
from mystical_kaleidoscope import mystical_kaleidoscope_generator
import time 
import threading
from moviepy import VideoFileClip
from moviepy.video.fx import MultiplySpeed
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


def generate_image():
    global image_generator, generate_video
    user_input = text_box.get()

    if generate_video is False:
        img = image_generator(user_input, generate_video)
        img_tk = ImageTk.PhotoImage(img)
        image_label.configure(image=img_tk, text='')
        image_label.image = img_tk  # Ensure the reference is maintained
    elif generate_video is True:
        # Sets preview of kaleidoscope (first frame). For aesthetic and cache-cleaning purposes
        stop_gif()
        img = image_generator(user_input, False)
        img_tk = ImageTk.PhotoImage(img)
        image_label.configure(image=img_tk, text='')
        image_label.image = img_tk  # Ensure the reference is maintained

        # Creates and displays gif on gui
        img = image_generator(user_input, generate_video)
        update_status('Video generated!', 'green')
        start_gif(f'GIFS/{style_chosen}_{text_box.get()}.gif')

    

def set_style(style):
    global image_generator, style_chosen

    perlin_var.set(0)
    brutalist_var.set(0)
    mystical_var.set(0)
    style.set(1)

    if style == perlin_var:
        image_generator = perlin_kaleidoscope_generator
        style_chosen = 'perlin'        
    elif style == brutalist_var:
        image_generator = brutalist_kaleidoscope_generator
        style_chosen = 'brutalist'
    elif style == mystical_var:
        image_generator = mystical_kaleidoscope_generator
        style_chosen = 'mystical'

def on_generate():
    global generate_video

    if video_var.get():
        update_status('Generating video... \nthis can take a while', 'red') 
        generate_video = True

        # Run the long-running task in a separate thread to avoid blocking the main thread
        threading.Thread(target=generate_image, daemon=True).start()
        
        
    else:
        stop_gif()
        generate_video = False
        generate_image()
        update_status('Image generated!', 'green')

def cargarGIF(filename):
    global frames, frame_count
    gif = Image.open(filename)
    #Extraer los frames en una lista
    frames = []
    try:
        while True:
            frames.append(ImageTk.PhotoImage(gif.copy()))
            gif.seek(len(frames))
    except EOFError:
        pass
    frame_count = len(frames)

def start_gif(filename):
    global running

    image_label.image = None
    image_label.configure(image=None, text='')

    cargarGIF(filename)
    running = True
    update_gif()

def stop_gif():
    global running 
    running = False

def update_gif(ind=0):
    global frame, frame_count
    if running:  # Check if animation should continue
        frame = frames[ind % frame_count]
        image_label.configure(image=frame)    
        #100 es el delay entre frames    
        app.after(75, update_gif, ind + 1)


def create_and_send_mail():

    global style_chosen
    user_input = text_box.get()
    sender_email = 'intrigavisual@gmail.com'
    sender_password = 'npfoosbyrzxdhzow'
    
    
    subject = 'ArtJam Kaleidoscope !'
    receiver_email = email_box.get()
    body = 'You have sent yourself a Kaleidoscope after interacting with the Kaleidoscope Generator at ArtJam in MACROFEST 2025!\n\n Te has enviado un Caleidoscopio despues de interactuar con el Generador de Caleidoscopio en el ArtJam en MACROFEST 2025'
    try:
        # Set up the server
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail SMTP server
        server.starttls()  # Secure connection

        # Log in to the email account
        server.login(sender_email, sender_password)

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Attach the email body
        msg.attach(MIMEText(body, 'plain'))

        attachment_paths = [f'MP4/{style_chosen}_{user_input}.mp4', 
                            f'PNG/{style_chosen}_{user_input}.png']

        # Loop through the attachment paths and attach them if they exist
        for attachment_path in attachment_paths:
            if os.path.exists(attachment_path):  # Check if the file exists
                # Open the file in binary mode
                with open(attachment_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)

                    # Add the header for the attachment
                    part.add_header('Content-Disposition', f'attachment; filename={attachment_path.split("/")[-1]}')

                    # Attach the file to the email
                    msg.attach(part)
            else:
                pass


        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())

        # Close the connection
        server.quit()

        message = "Email sent \nsuccessfully!"
        color = 'green'
        update_status(message, color)

        print("Email sent successfully!")

    except Exception as e:
        print(f"Error: {e}")

def on_send():
    # Run the long-running task in a separate thread to avoid blocking the main thread
    threading.Thread(target=create_and_send_mail, daemon=True).start()
    

# Function to update status message
def update_status(message, color):
    status_label.configure(text=message, text_color=color)

# Initialize the main window
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("Kaleidoscope Generator")
app.geometry("1200x900")

# Main frame (using grid)
frame = ctk.CTkFrame(app)
frame.grid(row=0, column=0, pady=20, padx=20, sticky="nsew")

# Configure grid layout
frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1, uniform="equal")
frame.grid_columnconfigure(1, weight=3, uniform="equal")

# Title label
title_label = ctk.CTkLabel(frame, text="! GENERA TU CALEIDOSCOPIO !\n@intrigavisual", font=("Arial", 32))
title_label.grid(row=0, column=0, columnspan=2, pady=10)

# Image placeholder (placed in the right column, bigger image size)
image_label = ctk.CTkLabel(frame, text="", width=800, height=600, fg_color="black")
image_label.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

# Frame for controls (checkboxes, text box, and buttons)
controls_frame = ctk.CTkFrame(frame, fg_color="#354a42")  # Custom background color for control section
controls_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nswe")

# Configure controls frame to take up more space
controls_frame.grid_rowconfigure(0, weight=0)
controls_frame.grid_rowconfigure(1, weight=0)
controls_frame.grid_rowconfigure(2, weight=0)
controls_frame.grid_rowconfigure(3, weight=0)
controls_frame.grid_rowconfigure(4, weight=0)  # Text box, video box, and generate button have more room
controls_frame.grid_rowconfigure(5, weight=1)  # Email box
controls_frame.grid_rowconfigure(6, weight=0)  # SEND button
controls_frame.grid_rowconfigure(7, weight=0)  # SEND button

# Checkboxes for image generation styles
perlin_var = ctk.IntVar()
brutalist_var = ctk.IntVar()
mystical_var = ctk.IntVar()

perlin_checkbox = ctk.CTkCheckBox(controls_frame, text="Perlin Style", variable=perlin_var, command=lambda: set_style(perlin_var))
brutalist_checkbox = ctk.CTkCheckBox(controls_frame, text="Brutalist Style", variable=brutalist_var, command=lambda: set_style(brutalist_var))
mystical_checkbox = ctk.CTkCheckBox(controls_frame, text="Mystical Style", variable=mystical_var, command=lambda: set_style(mystical_var))

perlin_checkbox.grid(row=0, column=0, pady=10, padx=10, sticky="w")
brutalist_checkbox.grid(row=1, column=0, pady=10, padx=10, sticky="w")
mystical_checkbox.grid(row=2, column=0, pady=10, padx=10, sticky="w")

# Status message box placed in second column, spanning the first three rows
status_label = ctk.CTkLabel(controls_frame, text="Choose your \nkaleidoscope!", width=100, height=100, fg_color="black")
status_label.grid(row=0, column=1, rowspan=3, padx=20, pady=20, sticky="nsew")

# Checkbox for video generation
video_var = ctk.IntVar()
video_checkbox = ctk.CTkCheckBox(controls_frame, text="Generate Video", variable=video_var)
video_checkbox.grid(row=3, column=0, pady=10, padx=10, sticky="w")

# Generate button (above email box)
generate_button = ctk.CTkButton(controls_frame, text="Generate!", command=on_generate)
generate_button.grid(row=5, column=0, columnspan=2, pady=10, padx=20, sticky="new")

# Text box for input (centered in the grid)
text_box = ctk.CTkEntry(controls_frame, placeholder_text="Enter text here")
text_box.grid(row=4, column=0, pady=10, columnspan=2, padx=20, sticky="new")

# Text box for email input (at the bottom)
email_box = ctk.CTkEntry(controls_frame, placeholder_text="Enter email address")
email_box.grid(row=6, column=0, pady=10, padx=20, sticky="new")

# SEND button next to the email box
send_button = ctk.CTkButton(controls_frame, text="SEND", command=on_send)
send_button.grid(row=6, column=1, padx=10, pady=10, sticky="new")

# Add a logo at the bottom left, more flattering alignment
image = Image.open("artjam_logo.PNG")  # Replace with your image path
image = image.resize((300, 300))  # Resize the image to a more flattering size
logo = ImageTk.PhotoImage(image)

logo_label = ctk.CTkLabel(controls_frame, image=logo, text='', height=300, width=300)
logo_label.grid(row=7, column=0, columnspan=2, padx=20, pady=20, sticky="sew")

# Run the application
app.mainloop()
