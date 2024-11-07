import hashlib
from math import floor
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import mysql.connector
from flask import Flask, redirect
import threading
import pyperclip
import pyqrcode
import png

# Flask app for URL redirection
app = Flask(__name__)

def connect_db():
    conn = mysql.connector.connect(
        database="url_shortener",
        user="root",
        password="mS1029384756,.F!",
        host="localhost",
        port="3306"
    )
    return conn

def hash_url(original_url, length_of_url):
    # Use hashlib to create a short URL
    short_url = hashlib.md5(original_url.encode()).hexdigest()[:length_of_url]
    return short_url

def save_url(original_url, short_url):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM urls WHERE short_url = %s", (short_url,))
        result = cursor.fetchone()
        if result:
            return result[1]
        else:
            cursor.execute("INSERT INTO urls (long_url, short_url) VALUES (%s, %s)", (original_url, short_url))
            conn.commit()
    except Exception as e:
        Messagebox.ok("Error", f"Could not save URL: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_long_url(short_url):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM urls WHERE short_url = %s", (short_url,))
        result = cursor.fetchone()
        return result[1]
    except Exception as e:
        Messagebox.ok("Error", f"Could not fetch URL: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def shorten_url(original_url, length_of_url):
    short_code = hash_url(original_url, length_of_url)
    save_url(original_url, short_code)
    return f'http://127.0.0.1:9000/{short_code}'

@app.route('/<short_code>')
def redirect_to_url(short_code):
    if not short_code:
        return "Short code not provided!", 400
    original_url = get_long_url(short_code)
    if original_url:
        return redirect(original_url)
    return 'Shortened URL not found!', 404

def run_flask():
    app.run(debug=False, use_reloader=False, port=9000)

# Tkinter GUI
def create_gui():
    window = ttk.Window(themename="superhero")
    window.title("URL Shortener")
    window.geometry("500x350")

    ttk.Label(window, text="Enter a URL to shorten:", font=("Helvetica", 22), bootstyle=DANGER).pack(pady=10)
    url_entry = ttk.Entry(window, width=50)
    url_entry.pack(pady=10)

    def slider(e):
        length_label.config(text=f"{floor(length_scale.get())}")


    def copy_to_clipboard():
        if generated_short_url:
            pyperclip.copy(generated_short_url)
            Messagebox.ok("Copied", "Short URL copied to clipboard!")
        else:
            Messagebox.ok("Copy Error", "No URL to copy. Please shorten a URL first.")

    def create_qr_code(original_url):
        input_path = filedialog.asksaveasfilename(title="Sve Image",
                                                  filetypes=(("PNG File", ".png"), ("All Files", "*.*")))

        if input_path:
            if input_path.endswith(".png"):
                get_code = pyqrcode.create(original_url)
                get_code.png(input_path, scale=5)
            else:
                input_path = f"{input_path}.png"
                get_code = pyqrcode.create(original_url)
                get_code.png(input_path, scale=5)

            global get_image
            get_image = ImageTk.PhotoImage(Image.open(input_path))

            qr_code_label.config(image=get_image)
            window.geometry("500x600")

    def on_shorten_button_click():
        original_url = url_entry.get()
        length_of_url = floor(length_scale.get())
        if original_url:
            global generated_short_url
            generated_short_url = shorten_url(original_url, length_of_url)
            short_url_label.config(text=f"Short URL: {generated_short_url}")

            answer_to_request = (Messagebox.yesno
                                 ("Would you like to generate a QR code of the URL?", "QR code request"))

            if answer_to_request == "Yes":
                create_qr_code(original_url)
            else:
                window.geometry("500x350")
        else:
            Messagebox.ok("Input Error", "Please enter a valid URL.")

    ttk.Label(text="Length of URL address:", bootstyle=INFO).pack(pady=5)
    length_scale = ttk.Scale(window, length=5, from_=5, to=10, value=5, bootstyle=INFO, command=slider)
    length_scale.pack()
    length_label = ttk.Label(window, text=f"{length_scale.get()}")
    length_label.pack()

    shorten_button = ttk.Button(window, text="Shorten URL", command=on_shorten_button_click)
    shorten_button.pack(pady=20)

    global short_url_label, generated_short_url

    generated_short_url = ""
    short_url_label = ttk.Label(window, text="Short URL: 'no URL generated'")
    short_url_label.pack(pady=10)

    copy_url_button = ttk.Button(window, text="Copy URL", bootstyle=INFO, command=copy_to_clipboard)
    copy_url_button.pack()

    qr_code_label = ttk.Label(window, text="")
    qr_code_label.pack(pady=20)

    window.mainloop()


if __name__ == "__main__":
    thread = threading.Thread(target=run_flask)
    thread.start()
    create_gui()
