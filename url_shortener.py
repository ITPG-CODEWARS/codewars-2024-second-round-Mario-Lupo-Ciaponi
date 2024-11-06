import hashlib
import tkinter as tk
from tkinter import messagebox
import mysql.connector
from flask import Flask, redirect
import threading

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


def hash_url(original_url):
    # Use hashlib to create a short URL
    short_url = hashlib.md5(original_url.encode()).hexdigest()[:6]  # Get first 6 characters
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
            messagebox.showinfo("Success", f"Short URL: {short_url}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save URL: {str(e)}")
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
        messagebox.showerror("Error", f"Could not save URL: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def shorten_url(original_url):
    short_code = hash_url(original_url)  # Simple numeric code
    save_url(original_url, short_code)
    return f'http://127.0.0.1:7001/{short_code}'


@app.route('/<short_code>')
def redirect_to_url(short_code):
    if not short_code:
        return "Short code not provided!", 400

    original_url = get_long_url(short_code)

    if original_url:
        return redirect(original_url)  # Redirect to original URL
    return 'Shortened URL not found!', 404


def run_flask():
    app.run(debug=False, use_reloader=False, port=7001)

# Tkinter GUI

def create_gui():
    # Create the main window
    window = tk.Tk()
    window.title("URL Shortener")

    # Label for instructions
    tk.Label(window, text="Enter a URL to shorten:").pack(pady=10)

    # Entry widget to input URL
    url_entry = tk.Entry(window, width=50)
    url_entry.pack(pady=10)

    # Function to handle URL shortening
    def on_shorten_button_click():
        original_url = url_entry.get()
        if original_url:
            # Generate short URL
            short_url = shorten_url(original_url)
            messagebox.showinfo("Shortened URL", f"Your shortened URL is: {short_url}")
        else:
            messagebox.showwarning("Input Error", "Please enter a valid URL.")

    # Button to shorten URL
    shorten_button = tk.Button(window, text="Shorten URL", command=on_shorten_button_click)
    shorten_button.pack(pady=10)

    # Run the GUI application
    window.mainloop()


# Run the Flask app in a separate thread
thread = threading.Thread(target=run_flask)
thread.start()

# Start the Tkinter GUI
create_gui()
