import hashlib
from datetime import datetime
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
from tkcalendar import Calendar



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


def save_url(original_url, short_url, max_uses=None, due_date=None):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Check if the short URL already exists
        cursor.execute("SELECT * FROM urls WHERE short_url = %s", (short_url,))
        result = cursor.fetchone()
        if result:
            return result[1]
        else:
            # Set max_uses to 0 (unlimited uses) if not provided
            if max_uses is None:
                max_uses = 0  # Unlimited uses by default

            # Insert the URL with the optional due_date
            cursor.execute(
                "INSERT INTO urls (long_url, short_url, date_of_creation, number_of_uses, max_uses, due_date) "
                "VALUES (%s, %s, NOW(), 0, %s, %s)",
                (original_url, short_url, max_uses, due_date)
            )
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


def shorten_url(original_url, length_of_url, custom_code=None, max_uses=None, due_date=None):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Check if the original URL already exists in the database
        cursor.execute("SELECT short_url FROM urls WHERE long_url = %s", (original_url,))
        result = cursor.fetchone()

        # If the URL exists, return the existing short URL
        if result:
            existing_short_url = result[0]
            Messagebox.ok("URL already exists!", f"Short URL: http://127.0.0.1:9000/{existing_short_url}")
            return f'http://127.0.0.1:9000/{existing_short_url}'

        # If the URL does not exist, create a new short URL
        short_code = custom_code if custom_code else hash_url(original_url, length_of_url)

        # Save the new URL and short code to the database with max_uses and due_date
        save_url(original_url, short_code, max_uses, due_date)

        return f'http://127.0.0.1:9000/{short_code}'

    except Exception as e:
        Messagebox.ok("Error", f"Error while shortening URL: {str(e)}")

    finally:
        cursor.close()
        conn.close()



@app.route('/<short_code>')
def redirect_to_url(short_code):
    if not short_code:
        return "Short code not provided!", 400

    original_url = get_long_url(short_code)

    if original_url:
        connection = connect_db()
        cursor = connection.cursor()

        cursor.execute("SELECT number_of_uses, max_uses, due_date FROM urls WHERE short_url = %s", (short_code,))
        result = cursor.fetchone()

        if result:
            number_of_uses, max_uses, due_date = result
            # Check if the URL has expired
            if due_date and datetime.now() > due_date:
                return "This shortened URL has expired.", 403

            if max_uses != 0 and number_of_uses >= max_uses:
                return "This shortened URL has reached its maximum number of uses.", 403

            cursor.execute("UPDATE urls SET number_of_uses = number_of_uses + 1 WHERE short_url = %s", (short_code,))
            connection.commit()

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
    window.geometry("500x650")

    ttk.Label(window, text="Enter a URL to shorten:", font=("Helvetica", 22), bootstyle=DANGER).pack(pady=10)
    url_entry = ttk.Entry(window, width=50)
    url_entry.pack(pady=10)

    ttk.Label(window, text="Custom Short Code (Optional):", bootstyle=INFO).pack(pady=5)
    custom_code_entry = ttk.Entry(window, width=50)
    custom_code_entry.pack(pady=5)

    ttk.Label(window, text="Due Date (Optional):", bootstyle=ttk.INFO).pack(pady=5)
    due_date_entry = ttk.Entry(window, width=50)
    due_date_entry.pack(pady=10)

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
            get_code.png(input_path, scale=4)

            global get_image
            get_image = ImageTk.PhotoImage(Image.open(input_path))
            qr_code_label.config(image=get_image)
            window.geometry("500x750")

    def delete_url(url):
        if url and re.search(REGEX_FOR_VALIDATING_URL, url):
            connection = connect_db()
            cursor = connection.cursor()

            try:
                # Check if the URL exists in the database
                cursor.execute("SELECT * FROM urls WHERE long_url = %s", (url,))
                record = cursor.fetchone()

                if record:
                    # URL found, proceed with deletion
                    cursor.execute("DELETE FROM urls WHERE long_url = %s", (url,))
                    connection.commit()  # Commit the deletion
                    Messagebox.ok("URL deleted successfully!", "Success")
                else:
                    # URL not found in the records
                    Messagebox.ok("No URL found in the records!", "Error")

            except Exception as e:
                Messagebox.ok(f"Error while deleting URL: {str(e)}", "Error")

            finally:
                # Ensure both cursor and connection are closed
                cursor.close()
                connection.close()
        else:
            Messagebox.ok("Invalid URL format. Please enter a valid URL.", "Error")

    def show_urls():
        """
        It shows all the URLS in the database.
        """
        second_window = Toplevel()
        second_window.title("Preview of URLS")

        connection = connect_db()

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM urls")

        records = cursor.fetchall()

        ttk.Label(second_window, text="URLS:", font=("Helvetica", 20, "bold"), bootstyle=DANGER).pack(pady=17)

        for row in records:
            original_url, short_code, date_of_creation, number_of_uses, max_uses, date_of_experiment = row[1:]

            ttk.Label(second_window, text=f"Original URl: {original_url} | "
                                          f"Shortened URL: http://127.0.0.1:9000/{short_code} | "
                                          f"Date of creation: {date_of_creation} | "
                                          f"Due date: {date_of_experiment}"
                                          f"Number of uses: {number_of_uses} | "
                                          f"Max nuber of uses: {max_uses if max_uses else 'Unlimited'}",
                      font=("Helvetica", 13), bootstyle=PRIMARY).pack(pady=10, padx=25)

    def edit_short_code(original_url, new_short_code):
        """
        Updates the short code for a given URL.
        """
        if not original_url or not re.search(REGEX_FOR_VALIDATING_URL, original_url):
            Messagebox.ok("Invalid URL format. Please enter a valid URL.", "Error")
            return

        if not new_short_code:
            Messagebox.ok("Please enter a new short code.", "Error")
            return

        connection = connect_db()
        cursor = connection.cursor()

        try:
            # Check if the original URL exists
            cursor.execute("SELECT * FROM urls WHERE long_url = %s", (original_url,))
            record = cursor.fetchone()

            if not record:
                Messagebox.ok("Original URL not found in records!", "Error")
                return

            # Check if the new short code is already in use
            cursor.execute("SELECT * FROM urls WHERE short_url = %s", (new_short_code,))
            if cursor.fetchone():
                Messagebox.ok("This short code is already in use. Choose another.", "Error")
                return

            # Update the short code
            cursor.execute("UPDATE urls SET short_url = %s WHERE long_url = %s", (new_short_code, original_url))
            connection.commit()
            Messagebox.ok("Short code updated successfully!", "Success")

        except Exception as e:
            Messagebox.ok(f"Error while updating short code: {str(e)}", "Error")

        finally:
            cursor.close()
            connection.close()

    def show_user_panel():
        panel_window = Toplevel()
        panel_window.title("User Panel")
        panel_window.geometry("500x300")

        ttk.Label(panel_window, text="User Panel", font=("Helvetica", 20, "bold"), bootstyle=DANGER).pack(pady=20)

        # Entry for URL to delete/edit
        url_entry = ttk.Entry(panel_window, bootstyle=INFO, width=30)
        url_entry.pack(pady=5)
        url_entry.insert(0, "Enter Original URL to Delete/Edit")

        # Entry for new short code (for editing)
        new_code_entry = ttk.Entry(panel_window, bootstyle=INFO, width=30)
        new_code_entry.pack(pady=5)
        new_code_entry.insert(0, "Enter New Short Code (Optional)")

        # Delete button
        delete_url_button = ttk.Button(panel_window, text="DELETE", bootstyle=DANGER,
                                       command=lambda: delete_url(url_entry.get()))
        delete_url_button.pack(pady=10)

        # Edit button
        edit_url_button = ttk.Button(panel_window, text="EDIT Short Code", bootstyle=INFO,
                                     command=lambda: edit_short_code(url_entry.get(), new_code_entry.get()))
        edit_url_button.pack(pady=10)

        # Preview button
        panel_preview_button = ttk.Button(panel_window, text="Preview URLs", bootstyle=INFO, command=show_urls)
        panel_preview_button.pack(pady=10)

    def on_shorten_button_click():
        """
        Generates a short URL after checking if the URL is valid and includes a due date if provided.
        """
        original_url = url_entry.get()

        # Check if the entered URL is valid
        if not original_url:
            Messagebox.show_error("Input Error", "Please enter a valid URL.")
            return

        # Get the due date from the Entry widget (validate the date format)
        due_date_str = due_date_entry.get()  # Get input as a string
        due_date = None

        # Validate if the date is entered in the correct format (YYYY-MM-DD)
        try:
            if due_date_str:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            else:
                due_date = None
        except ValueError:
            Messagebox.show_error("Date Format Error", "Please enter a valid date (YYYY-MM-DD).")
            return

        # Now handle max uses (if applicable)
        max_uses_input = max_uses_entry.get().strip()
        if max_uses_input and not max_uses_input.isdigit():
            Messagebox.show_error("Input Error", "Please enter a valid number for max uses.")
            return

        max_uses = int(max_uses_input) if max_uses_input else None

        # Generate short URL using custom code if provided, otherwise generate a hashed short URL
        custom_code = custom_code_entry.get().strip()
        length_of_url = floor(length_scale.get())

        # Generate the shortened URL using the shorten_url function
        global generated_short_url
        generated_short_url = shorten_url(original_url, length_of_url, custom_code if custom_code else None,
                                          max_uses, due_date)

        short_url_label.config(text=f"Short URL: {generated_short_url}")

        # Ask to generate a QR code
        if Messagebox.yesno("QR Code", "Would you like to generate a QR code of the URL?") == "Yes":
            create_qr_code(generated_short_url)
        else:
            window.geometry("500x650")

    ttk.Label(window, text="Length of URL address:", bootstyle=INFO).pack(pady=5)

    length_scale = ttk.Scale(window, length=50, from_=5, to=10, value=5, bootstyle=INFO, command=slider)
    length_scale.pack()

    length_label = ttk.Label(window, text=f"{length_scale.get()}")  # To show the value that the slider is currently on.
    length_label.pack()

    ttk.Label(window, text="Max Number of Uses (Optional):", bootstyle=INFO).pack(pady=5)
    max_uses_entry = ttk.Entry(window, width=50)
    max_uses_entry.pack(pady=5)

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

    user_panel_button = ttk.Button(window, text="User panel", bootstyle=INFO, command=show_user_panel)
    user_panel_button.pack()

    qr_code_label = ttk.Label(window, text="")
    qr_code_label.pack(pady=20)

    window.mainloop()


if __name__ == "__main__":
    thread = threading.Thread(target=run_flask)
    thread.start()
    create_gui()
