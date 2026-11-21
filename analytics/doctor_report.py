import csv
import glob
import os
import sys
import matplotlib.pyplot as plt

def find_latest_session():
    """data/ klasöründeki en son kaydedilen seans dosyasını bulur."""
    files = glob.glob(os.path.join("data", "seans_*.csv"))
    if not files:
        return None
    return max(files, key=os.path.getctime)

def generate_report(csv_path=None):
    if not csv_path:
        csv_path = find_latest_session()

    if not csv_path or not os.path.exists(csv_path):
        print("Hata: Gösterilecek seans kaydı bulunamadı. Önce bir seans kaydedin.")
        return

    times, pitches, rolls, forces = [], [], [], []

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        start_time = None
        for row in reader:
            t = float(row["timestamp"])
            if start_time is None:
                start_time = t
            times.append(round(t - start_time, 2))
            pitches.append(float(row["pitch"]))
            rolls.append(float(row["roll"]))
            forces.append(int(row["force"]))

    if len(times) < 2:
        print("Hata: Grafik çizmek için yeterli veri yok (en az 2 saniye kayıt alın).")
        return

    # --- TIBBİ METRİK HESAPLAMALARI ---
    duration = times[-1]
    max_pitch = max(abs(p) for p in pitches)
    max_roll = max(abs(r) for r in rolls)
    max_force = max(forces)
    avg_force = sum(forces) / len(forces)

    # Kas Yorulma İndeksi (İlk yarı vs İkinci yarı ortalama kavrama gücü)
    mid = len(forces) // 2
    first_half_avg = sum(forces[:mid]) / max(1, mid)
    second_half_avg = sum(forces[mid:]) / max(1, len(forces) - mid)

    if first_half_avg > 0:
        fatigue_pct = ((first_half_avg - second_half_avg) / first_half_avg) * 100
    else:
        fatigue_pct = 0.0

    fatigue_text = f"%{fatigue_pct:.1f} Düşüş" if fatigue_pct > 0 else f"%{abs(fatigue_pct):.1f} Artış (Yorulma Yok)"

    # --- GRAFİK ÇİZİMİ ---
    plt.style.use("seaborn-v0_8-darkgrid")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    fig.canvas.manager.set_window_title("RehabHub - Tıbbi Seans Raporu")

    # Üst Başlık ve Özet Bilgi
    summary = (
        f"Seans Süresi: {duration:.1f} sn  |  "
        f"Maks. Pitch (ROM): {max_pitch:.1f}°  |  "
        f"Maks. Roll (ROM): {max_roll:.1f}°\n"
        f"Maks. Kavrama Gücü: {max_force}/1023  |  "
        f"Ortalama Güç: {avg_force:.1f}  |  "
        f"Kas Yorulma Analizi: {fatigue_text}"
    )
    fig.suptitle("EL REHABİLİTASYON SEANS RAPORU", fontsize=14, fontweight="bold", y=0.98)
    fig.text(0.5, 0.90, summary, ha="center", fontsize=10, bbox=dict(facecolor="#dff9fb", edgecolor="#22a6b3", boxstyle="round,pad=0.5"))

    # 1. Grafik: Bilek Açıları (Pitch & Roll)
    ax1.plot(times, pitches, label="Pitch (Öne/Arkaya)", color="#0984e3", linewidth=2)
    ax1.plot(times, rolls, label="Roll (Sağa/Sola)", color="#e17055", linewidth=2)
    ax1.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax1.set_ylabel("Açı (Derece)")
    ax1.set_title("Bilek Hareket Açısı (ROM) Değişimi", fontsize=11, fontweight="bold")
    ax1.legend(loc="upper right")

    # 2. Grafik: Kavrama Gücü (FSR)
    ax2.plot(times, forces, label="Kavrama Gücü (FSR)", color="#00b894", linewidth=2)
    ax2.fill_between(times, forces, color="#00b894", alpha=0.2)
    ax2.axhline(avg_force, color="#d63031", linestyle="--", linewidth=1.5, label=f"Ortalama ({avg_force:.0f})")
    ax2.set_xlabel("Zaman (Saniye)")
    ax2.set_ylabel("Kuvvet (0 - 1023)")
    ax2.set_title("Kavrama Gücü ve Kas Dayanıklılığı", fontsize=11, fontweight="bold")
    ax2.legend(loc="upper right")

    plt.tight_layout(rect=[0, 0, 1, 0.87])
    plt.show()

if __name__ == "__main__":
    target_file = sys.argv[1] if len(sys.argv) > 1 else None
    generate_report(target_file)