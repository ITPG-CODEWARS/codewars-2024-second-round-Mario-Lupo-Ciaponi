import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import pyshorteners


class UrlShortener:
    URL = 'http://tinyurl.com/api-create.php?url='

    def __init__(self, master):
        self.master = master
        self.master.title("URL Shortener")
        self.master.geometry("400x210")

        self.url_label = ttk.Label(text="URL:", font=("Helvetica", 25), bootstyle=INFO)
        self.url_label.pack(pady="10")

        self.url_entry = ttk.Entry(master, width=30)
        self.url_entry.pack()

        self.get_short_url_button = ttk.Button(text="Get shorter ULR", command=self.get_shortener_ulr)
        self.get_short_url_button.pack(pady="30")

        self.result_entry = ttk.Entry()
        self.result_entry.pack()

    def get_shortener_ulr(self):
        long_url = self.url_entry.get()

        try:
            type_tiny = pyshorteners.Shortener()
            short_url = type_tiny.tinyurl.short(long_url)
        except pyshorteners.exceptions.BadURLException:
            invalid_url_message_box = Messagebox.okcancel("The URL provided is invalid!", "Invalid URL!")
        else:
            self.result_entry.delete(0, END)
            self.result_entry.insert(0, f"{short_url}")


if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    url_shortener = UrlShortener(root)
    root.mainloop()
