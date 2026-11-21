import socket
import json
import time
import tkinter as tk

# --- AĞ AYARLARI ---
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_sensor_data():
    """Sürgülerdeki anlık değerleri okuyup JSON formatında UDP üzerinden yollar."""
    payload = {
        "timestamp": round(time.time(), 3),
        "pitch": round(pitch_slider.get(), 2),
        "roll": round(roll_slider.get(), 2),
        "force": int(force_slider.get())
    }
    
    message = json.dumps(payload).encode("utf-8")
    sock.sendto(message, (UDP_IP, UDP_PORT))
    
    status_label.config(text=f"Yayınlanıyor ({UDP_IP}:{UDP_PORT})\n{payload}")
    root.after(33, send_sensor_data)  # ~30 Hz

def reset_values():
    """Tüm sensör değerlerini nötr (0) konumuna sıfırlar."""
    pitch_slider.set(0)
    roll_slider.set(0)
    force_slider.set(0)

def on_close():
    sock.close()
    root.destroy()

# --- ARAYÜZ TASARIMI ---
root = tk.Tk()
root.title("Sanal ESP32 - Rehabilitasyon Topu Simülatörü")
root.geometry("420x350")
root.protocol("WM_DELETE_WINDOW", on_close)

tk.Label(root, text="Bilek Yukarı/Aşağı (Pitch - Derece)", font=("Arial", 10, "bold")).pack(pady=(10, 0))
pitch_slider = tk.Scale(root, from_=-90, to=90, orient=tk.HORIZONTAL, resolution=0.5, length=350)
pitch_slider.pack()

tk.Label(root, text="Bilek Sağa/Sola (Roll - Derece)", font=("Arial", 10, "bold")).pack(pady=(10, 0))
roll_slider = tk.Scale(root, from_=-90, to=90, orient=tk.HORIZONTAL, resolution=0.5, length=350)
roll_slider.pack()

tk.Label(root, text="Topu Sıkma Kuvveti (FSR - 0..1023)", font=("Arial", 10, "bold")).pack(pady=(10, 0))
force_slider = tk.Scale(root, from_=0, to=1023, orient=tk.HORIZONTAL, resolution=1, length=350)
force_slider.pack()

tk.Button(root, text="Nötr Konuma Sıfırla", command=reset_values, bg="#e74c3c", fg="white").pack(pady=15)

status_label = tk.Label(root, text="Başlatılıyor...", font=("Consolas", 9), fg="#2c3e50")
status_label.pack(pady=5)

send_sensor_data()
root.mainloop()