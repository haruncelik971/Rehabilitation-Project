import socket
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# --- AĞ AYARLARI ---
UDP_IP = "0.0.0.0"
UDP_PORT = 5005

class RehabDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("RehabHub - El Rehabilitasyon Ana Kontrol Paneli")
        self.root.geometry("600x520")
        self.root.configure(bg="#1e272e")

        self.max_pitch = 0.0
        self.max_roll = 0.0
        self.max_force = 0
        self.running = True

        self.setup_ui()
        
        self.listen_thread = threading.Thread(target=self.udp_listener, daemon=True)
        self.listen_thread.start()

    def setup_ui(self):
        tk.Label(self.root, text="EL REHABİLİTASYON SİSTEMİ", font=("Arial", 16, "bold"), fg="#00d2d3", bg="#1e272e").pack(pady=(15, 5))
        self.status_lbl = tk.Label(self.root, text="Durum: Sensör Verisi Bekleniyor (Port 5005)...", font=("Arial", 10), fg="#ff9f43", bg="#1e272e")
        self.status_lbl.pack(pady=(0, 15))

        # --- CANLI SENSÖR GÖSTERGELERİ ---
        sensor_frame = tk.LabelFrame(self.root, text=" Canlı Sensör Verileri ", font=("Arial", 11, "bold"), fg="white", bg="#2f3640", padx=15, pady=10)
        sensor_frame.pack(fill="x", padx=20, pady=5)

        self.pitch_lbl = tk.Label(sensor_frame, text="Bilek Öne/Arkaya (Pitch): 0.0°", font=("Consolas", 11), fg="white", bg="#2f3640")
        self.pitch_lbl.pack(anchor="w")
        self.pitch_bar = ttk.Progressbar(sensor_frame, length=500, mode="determinate", maximum=180)
        self.pitch_bar.pack(pady=(2, 10))
        self.pitch_bar["value"] = 90

        self.roll_lbl = tk.Label(sensor_frame, text="Bilek Sağa/Sola (Roll): 0.0°", font=("Consolas", 11), fg="white", bg="#2f3640")
        self.roll_lbl.pack(anchor="w")
        self.roll_bar = ttk.Progressbar(sensor_frame, length=500, mode="determinate", maximum=180)
        self.roll_bar.pack(pady=(2, 10))
        self.roll_bar["value"] = 90

        self.force_lbl = tk.Label(sensor_frame, text="Kavrama Gücü (FSR): 0 / 1023", font=("Consolas", 11), fg="white", bg="#2f3640")
        self.force_lbl.pack(anchor="w")
        self.force_bar = ttk.Progressbar(sensor_frame, length=500, mode="determinate", maximum=1023)
        self.force_bar.pack(pady=(2, 5))

        # --- TIBBİ ÖZET (ROM) PANELİ ---
        stats_frame = tk.LabelFrame(self.root, text=" Seans Rekorları (ROM & Güç) ", font=("Arial", 11, "bold"), fg="white", bg="#2f3640", padx=15, pady=10)
        stats_frame.pack(fill="x", padx=20, pady=10)

        self.stats_lbl = tk.Label(stats_frame, text="Maks. Pitch: 0.0°  |  Maks. Roll: 0.0°  |  Maks. Güç: 0", font=("Consolas", 10, "bold"), fg="#1dd1a1", bg="#2f3640")
        self.stats_lbl.pack(side="left")

        tk.Button(stats_frame, text="Sıfırla", command=self.reset_stats, bg="#ee5253", fg="white", font=("Arial", 9, "bold")).pack(side="right")

        # --- OYUN MODÜLLERİ ALANI ---
        game_frame = tk.LabelFrame(self.root, text=" Egzersiz Oyunları ", font=("Arial", 11, "bold"), fg="white", bg="#2f3640", padx=15, pady=10)
        game_frame.pack(fill="x", padx=20, pady=5)

        tk.Button(game_frame, text="Oyun 1 (Yakında)", command=lambda: self.launch_game("Oyun 1"), bg="#54a0ff", fg="white", width=18, height=2).pack(side="left", padx=10)
        tk.Button(game_frame, text="Oyun 2 (Yakında)", command=lambda: self.launch_game("Oyun 2"), bg="#5f27cd", fg="white", width=18, height=2).pack(side="left", padx=10)
        tk.Button(game_frame, text="Doktor Raporu", command=lambda: self.launch_game("Rapor"), bg="#10ac84", fg="white", width=18, height=2).pack(side="right", padx=10)

    def udp_listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((UDP_IP, UDP_PORT))
        sock.settimeout(1.0)

        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                sensor_data = json.loads(data.decode("utf-8"))
                self.root.after(0, self.update_ui, sensor_data, addr[0])
            except socket.timeout:
                continue
            except Exception as e:
                print("Veri okuma hatası:", e)
        
        sock.close()

    def update_ui(self, data, sender_ip):
        pitch = float(data.get("pitch", 0.0))
        roll = float(data.get("roll", 0.0))
        force = int(data.get("force", 0))

        self.status_lbl.config(text=f"Bağlandı! Veri Kaynağı: {sender_ip}", fg="#1dd1a1")

        self.pitch_lbl.config(text=f"Bilek Öne/Arkaya (Pitch): {pitch:.1f}°")
        self.pitch_bar["value"] = max(0, min(180, pitch + 90))

        self.roll_lbl.config(text=f"Bilek Sağa/Sola (Roll): {roll:.1f}°")
        self.roll_bar["value"] = max(0, min(180, roll + 90))

        self.force_lbl.config(text=f"Kavrama Gücü (FSR): {force} / 1023")
        self.force_bar["value"] = max(0, min(1023, force))

        if abs(pitch) > self.max_pitch:
            self.max_pitch = abs(pitch)
        if abs(roll) > self.max_roll:
            self.max_roll = abs(roll)
        if force > self.max_force:
            self.max_force = force

        self.stats_lbl.config(text=f"Maks. Pitch: {self.max_pitch:.1f}°  |  Maks. Roll: {self.max_roll:.1f}°  |  Maks. Güç: {self.max_force}")

    def reset_stats(self):
        self.max_pitch = 0.0
        self.max_roll = 0.0
        self.max_force = 0
        self.stats_lbl.config(text="Maks. Pitch: 0.0°  |  Maks. Roll: 0.0°  |  Maks. Güç: 0")

    def launch_game(self, name):
        messagebox.showinfo("Modül Hazır", f"{name} modülü buraya entegre edilecek!")

    def on_close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RehabDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()