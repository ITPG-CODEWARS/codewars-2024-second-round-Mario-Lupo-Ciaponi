[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/fULRwKMW)

# URL shortener:

## Description:

In this app the user can type a URL and he/she will get a shortened URL which will redirect to the original one that he/she typed.
The user also has other options to customize, set a number of times that he/she can use the shortened URL.
There is also a preview button that opens a window with all the information about the created URLs and a user panel that
has the options to delete a URL, change the short code or preview the URLs created.

## Main page:
In the main page the user can add a URL, and it will return the shortened URL.

### Inputs:
- URL to Shorten: Enter the URL to be shortened;
- Custom Short Code (optional): Customize the short code, e.g., "fb" for Facebook.;
- Max Uses (optional): Set a limit for how many times the shortened URL can be used.;
- Due Date (optional): Set an expiration date (format: YYYY-MM-DD). After this date, the shortened URL will be unavailable;
- Password (optional): Require a password to access the shortened URL.

### Slider
Short Code Length: Set the length (5–10 characters) of the generated short code if not using a custom code.

### Buttons:
- Shorten URL: Generates a shortened URL with the specified settings;
- Copy URL: Opens a new window showing information about all created URLs (will not display if there are no URLs).
- Preview: opens a new window and inside of it will be contained all the information about the URLs. If there are no URLs then iw won't print anything;
- User panel: Opens a user panel window with options to delete URLs, edit short codes, or view existing URLs.

## Preview page:
The preview page shows all the information about the URLs including: 
- Original URL;
- Shortened URL;
- Date of creation;
- Due date;
- Number of uses;
- Max number of uses;
- Password;

## User panel:

### Inputs:
- First entry lets the user type THE ORIGINAL URL that he/she wants to delete or edit;
- Second entry lets the user type the short code that he/she wants to edit.

### Buttons:
- Delete: deletes the URL from the database;
- EDIT short code: edits the short code of the URL given in the first entry.

## How to start:
The app need to be started from the one and only python file in it 'url_shortener'.

## Dependencies:

### Built-in Python Libraries:
- hashlib: For hashing URLs, used in the hash_url function;
- datetime: To manage dates, like setting expiry dates;
- math.floor: For rounding down values, used with the slider;
- threading: To run the Flask app concurrently with the Tkinter GUI;
- re: For regular expressions, used to validate URL formats.

### Third-party Libraries:
- ttkbootstrap: A package for creating themed Tkinter GUIs;
- mysql.connector: For MySQL database connectivity, required to interact with a MySQL database;
- Flask: A web framework used to handle URL redirects;
- pyperclip: For copying text to the clipboard;
- pyqrcode: To generate QR codes for URLs;
- PIL (Pillow): To handle images in Tkinter, specifically for displaying QR codes.

### Additional Services:
MySQL Database: A MySQL server is required, with a url_shortener database configured. 
The database must have an urls table with fields matching those used in the code (such as long_url, short_url, date_of_creation, 
number_of_uses, max_uses, due_date, password).

#### MySQL Database Schema
Below is the recommended schema for the `urls` table:

| Field              | Data Type                        | Description                                                 |
|--------------------|----------------------------------|-------------------------------------------------------------|
| `id`               | INT, Primary Key, AUTO_INCREMENT | Unique identifier for each shortened URL.                   |
| `long_url`         | VARCHAR(2048)                    | The original URL that will be shortened.                    |
| `short_url`        | VARCHAR(255)                     | The shortened version of the URL or custom short code.      |
| `date_of_creation` | NOW()                            | Timestamp when the shortened URL was created.               |
| `number_of_uses`   | INT                              | Tracks the number of times the shortened URL has been used. |
| `max_uses`         | INT                              | Maximum allowed uses before expiration.                     |
| `due_date`         | DATE                             | Expiration date for the shortened URL.                      |
| `password`         | VARCHAR(255)                     | (Optional) Password required for accessing the URL.         |


### Environment Setup:
Flask App Configuration: The Flask app runs on http://127.0.0.1:9000. Make sure no other services are using this port when running the code.

## Troubleshooting

- **MySQL Database Connection Error**: Ensure that MySQL is running and that the database `url_shortener` is correctly set up with the required table.
- **Port 9000 Already in Use**: Change the Flask app's port in `url_shortener.py` or close any other applications using port 9000.
- **Library Not Found**: Verify all dependencies are installed by running `pip list`. Reinstall any missing libraries.
