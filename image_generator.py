import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import requests
import io
import base64
import threading

API_KEY = ""
API_URL = ""

QUALITY_PRESETS = {
    "Standard": {"steps": 20, "cfg_scale": 7},
    "HD": {"steps": 30, "cfg_scale": 9},
    "Ultra": {"steps": 40, "cfg_scale": 10},
}

STYLE_PRESETS = {
    "Realistic": ", ultra realistic, cinematic lighting, hyper-detailed, photorealistic textures",
    "3D": ", 3d render, unreal engine 5 style, octane render, cinematic lighting, hyper-detailed",
    "Cartoon": ", cartoon style, pixar animation, colorful, 2d illustration, smooth lines, cute design",
}

def generate_image():
    threading.Thread(target=_generate_image).start()

def _generate_image():
    prompt = entry.get().strip()
    if not prompt:
        messagebox.showwarning("Warning", "Please enter a prompt!")
        return

    progress_label.config(text="⏳ Generating image, please wait...")
    progress_bar.start(10)

    style_mode = style_var.get()
    style_suffix = STYLE_PRESETS[style_mode]
    enhanced_prompt = prompt + style_suffix

    quality_mode = quality_var.get()
    settings = QUALITY_PRESETS[quality_mode]

    payload = {
        "steps": settings["steps"],
        "width": 1024,
        "height": 1024,
        "cfg_scale": settings["cfg_scale"],
        "samples": 1,
        "text_prompts": [{"text": enhanced_prompt, "weight": 1}]
    }

    try:
        response = requests.post(
            API_URL,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            json=payload,
            timeout=90
        )

        progress_bar.stop()
        progress_label.config(text="")

        if response.status_code != 200:
            messagebox.showerror("Error", f"API Error {response.status_code}: {response.text}")
            return

        data = response.json()
        img_b64 = data["artifacts"][0]["base64"]
        img_data = base64.b64decode(img_b64)

        img = Image.open(io.BytesIO(img_data)).resize((400, 400))
        photo = ImageTk.PhotoImage(img)
        label.config(image=photo)
        label.image = photo
        label.image_data = img_data

    except Exception as e:
        progress_bar.stop()
        progress_label.config(text="")
        messagebox.showerror("Error", str(e))

def save_image():
    if hasattr(label, "image_data"):
        with open("generated_image.png", "wb") as f:
            f.write(label.image_data)
        messagebox.showinfo("Saved", "Image saved as generated_image.png")
    else:
        messagebox.showwarning("Warning", "No image to save!")

root = tk.Tk()
root.title("AI Image Generator (Stability AI)")
root.geometry("520x720")

tk.Label(root, text="Enter prompt:", font=("Arial", 12)).pack(pady=10)
entry = tk.Entry(root, width=55, font=("Arial", 12))
entry.pack(pady=5)


tk.Label(root, text="Select Quality:", font=("Arial", 12)).pack(pady=5)
quality_var = tk.StringVar(value="Standard")
quality_menu = tk.OptionMenu(root, quality_var, "Standard", "HD", "Ultra")
quality_menu.pack(pady=5)

tk.Label(root, text="Select Style:", font=("Arial", 12)).pack(pady=5)
style_var = tk.StringVar(value="Realistic")
style_menu = tk.OptionMenu(root, style_var, "Realistic", "3D", "Cartoon")
style_menu.pack(pady=5)

tk.Button(root, text="Generate Image", command=generate_image, bg="blue", fg="white").pack(pady=15)
tk.Button(root, text="Save Image", command=save_image, bg="green", fg="white").pack(pady=5)

progress_label = tk.Label(root, text="", font=("Arial", 11), fg="red")
progress_label.pack(pady=5)
progress_bar = ttk.Progressbar(root, mode="indeterminate", length=250)
progress_bar.pack(pady=5)

label = tk.Label(root)
label.pack(pady=20)

root.mainloop()
