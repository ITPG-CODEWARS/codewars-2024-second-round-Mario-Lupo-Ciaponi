import hashlib
from math import floor
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.window import Toplevel
from tkinter import filedialog
from PIL import Image, ImageTk
import mysql.connector
from flask import Flask, redirect
import threading
import pyperclip
import pyqrcode
import png
import re


# Flask app for URL redirection
app = Flask(__name__)

REGEX_FOR_VALIDATING_URL = (r"(https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z]{2,}(\.[a-zA-Z]{2,})"
                            r"(\.[a-zA-Z]{2,})?\/[a-zA-Z0-9]{2,}|((https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)"
                            r"?[a-zA-Z]{2,}(\.[a-zA-Z]{2,})(\.[a-zA-Z]{2,})?)|(https:\/\/www\.|http:\/\/www\.|https:\/\
                            /|http:\/\/)?[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}(\.[a-zA-Z0-9]{2,})?")


def connect_db():
    """
    Connects to the database.
    """
    conn = mysql.connector.connect(
        database="url_shortener",
        user="root",
        password="mS1029384756,.F!",
        host="localhost",
        port="3306"
    )
    return conn


def hash_url(original_url, length_of_url):
    """
    Generate a hash-based short URL if no custom code is provided.
    """
    return hashlib.md5(original_url.encode()).hexdigest()[:length_of_url]  # The value of the slider (length_of_url)


def save_url(original_url, short_url):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Check if the short URL already exists
        cursor.execute("SELECT * FROM urls WHERE short_url = %s", (short_url,))
        result = cursor.fetchone()
        if result:
            return result[1]
        else:
            cursor.execute("INSERT INTO urls (long_url, short_url, date_of_creation) VALUES (%s, %s, NOW())",
                           (original_url, short_url))
            conn.commit()
            return short_url
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
    except TypeError:
        pass
    except Exception as e:
        Messagebox.ok("Error", f"Could not fetch URL: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def shorten_url(original_url, length_of_url, custom_code=None):
    # Use the custom code if provided; otherwise, generate a hashed short URL
    short_code = custom_code if custom_code else hash_url(original_url, length_of_url)
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


# Ttkbootstrap GUI
def create_gui():
    """
    Creates a GUI for the app and inside of it, there a some nested important functions.
    """
    window = ttk.Window(themename="superhero")
    window.title("URL Shortener")
    window.geometry("500x383")

    ttk.Label(window, text="Enter a URL to shorten:", font=("Helvetica", 22), bootstyle=DANGER).pack(pady=10)
    url_entry = ttk.Entry(window, width=50)
    url_entry.pack(pady=10)

    ttk.Label(window, text="Custom Short Code (Optional):", bootstyle=INFO).pack(pady=5)
    custom_code_entry = ttk.Entry(window, width=50)
    custom_code_entry.pack(pady=5)

    def slider(e):
        """
        Changes the value of length_label
        """
        length_label.config(text=f"{floor(length_scale.get())}")

    def copy_to_clipboard():
        """
        It copies the shortened URL to the clipboard.
        """
        if generated_short_url:
            pyperclip.copy(generated_short_url)
            Messagebox.ok("Copied", "Short URL copied to clipboard!")
        else:
            Messagebox.ok("Copy Error", "No URL to copy. Please shorten a URL first.")

    def show_urls():
        """
        It shows all the URLS in the database.
        """
        second_window = Toplevel()
        second_window.title("Preview of URLS")

        connection = connect_db()

        sql_select_query = "SELECT * FROM urls"
        cursor = connection.cursor()
        cursor.execute(sql_select_query)

        records = cursor.fetchall()

        ttk.Label(second_window, text="URLS:", font=("Helvetica", 20, "bold"), bootstyle=DANGER).pack(pady=17)

        for row in records:
            ttk.Label(second_window, text=f"Original URl: {row[1]} | "
                                          f"Shortened URL: http://127.0.0.1:9000/{row[2]} | "
                                          f"Date of creation: {row[3]}",
                      font=("Helvetica", 13), bootstyle=PRIMARY).pack(pady=10, padx=25)

    def create_qr_code(short_url):
        """
        Firstly, it asks where do you want to save it(save as),
        then it generates a qr code at the bottom of the app
        """
        input_path = filedialog.asksaveasfilename(title="Save Image",
                                                  filetypes=(("PNG File", ".png"), ("All Files", "*.*")))
        if input_path:
            if not input_path.endswith(".png"):
                input_path += ".png"

            get_code = pyqrcode.create(short_url)
            get_code.png(input_path, scale=5)

            global get_image
            get_image = ImageTk.PhotoImage(Image.open(input_path))
            qr_code_label.config(image=get_image)
            window.geometry("500x750")

    def on_shorten_button_click():
        """
        Generates a short URL after checking if the URL is valid.
        """
        original_url = url_entry.get()

        if re.search(REGEX_FOR_VALIDATING_URL, original_url):  # Check if the URL given is valid
            custom_code = custom_code_entry.get().strip()
            length_of_url = floor(length_scale.get())

            global generated_short_url

            # Check if the custom code is already in use
            if custom_code and get_long_url(custom_code):
                Messagebox.ok("Custom Code Error", "This custom code is already in use. Please choose another.")
                return

            # Generate short URL using custom code if provided, otherwise generate a hashed short URL
            generated_short_url = shorten_url(original_url, length_of_url, custom_code if custom_code else None)
            short_url_label.config(text=f"Short URL: {generated_short_url}")

            # Ask to generate a QR code
            if Messagebox.yesno("QR Code", "Would you like to generate a QR code of the URL?") == "Yes":
                create_qr_code(generated_short_url)
            else:
                window.geometry("500x383")
        else:
            Messagebox.ok("Input Error", "Please enter a valid URL.")

    ttk.Label(window, text="Length of URL address:", bootstyle=INFO).pack(pady=5)

    length_scale = ttk.Scale(window, length=50, from_=5, to=10, value=5, bootstyle=INFO, command=slider)
    length_scale.pack()

    length_label = ttk.Label(window, text=f"{length_scale.get()}")  # To show the value that the slider is currently on.
    length_label.pack()

    shorten_button = ttk.Button(window, text="Shorten URL", command=on_shorten_button_click)
    shorten_button.pack(pady=20)

    global short_url_label, generated_short_url

    generated_short_url = ""
    short_url_label = ttk.Label(window, text="Short URL: 'No URL generated'")
    short_url_label.pack(pady=10)

    copy_url_button = ttk.Button(window, text="Copy URL", bootstyle=INFO, command=copy_to_clipboard)
    copy_url_button.pack()

    preview_button = ttk.Button(window, text="Preview", bootstyle=INFO, command=show_urls)
    preview_button.pack(pady=20)

    qr_code_label = ttk.Label(window, text="")
    qr_code_label.pack(pady=20)

    window.mainloop()


if __name__ == "__main__":
    thread = threading.Thread(target=run_flask)
    thread.start()
    create_gui()
