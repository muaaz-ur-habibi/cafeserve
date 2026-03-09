from psutil import virtual_memory, net_io_counters, sensors_battery
import os
from requests import get
from requests.exceptions import ConnectionError
import cv2

camera = cv2.VideoCapture(0)

def get_size(start_path:str):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def bytes_to_iec(num_bytes):
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} {units[-1]}"

def test_connection():
    try:
        get("https://google.com")
        return True
    except ConnectionError:
        return False

def get_server_stats(database_location:str):
    memory = virtual_memory()
    memory_info = f"{round(memory.used / (1024 ** 3), 2)} / {round(memory.total / (1024 ** 3))}"

    network = net_io_counters()
    network_info = f"In: {bytes_to_iec(network.bytes_recv)} Out: {bytes_to_iec(network.bytes_sent)}"
    
    battery = sensors_battery()
    if battery == None:
        battery_info = "No battery"
    else:
        battery_info = f"{round(battery.percent, 2)}%"

    database_size = f"Database size: {bytes_to_iec(get_size(database_location))}"

    return {
        "connected": test_connection(),
        "memory_info": memory_info,
        "network_info": network_info,
        "battery_info": battery_info,
        "database_size": database_size
    }

def get_camera_feed():
    if camera.isOpened():
        ret, frame = camera.read()
        _, image_data = cv2.imencode('.JPG', frame)
        #image_data = b64encode(image_data.tobytes()).decode()
        image_data = image_data.tobytes()

        '''
        return {
            'stream': image_data
        }
        '''
        return image_data
    
    else:
        return {
            'success': False
        }