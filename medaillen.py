import cv2
import numpy as np

def calculate_activity_score(heatmap):
    import cv2
    import numpy as np
    import math

    # Normalisieren
    normalized = cv2.normalize(heatmap, None, 0, 1.0, cv2.NORM_MINMAX)

    # Schwellenwert definieren
    threshold = 0.75
    active_pixels = np.sum(normalized > threshold)

    print(f"📊 Aktive Pixel über Schwellwert: {active_pixels}")

    # Logarithmische Skala: Score verdoppelt sich bei Verzehnfachung
    if active_pixels <= 0:
        return 0

    score = math.log10(active_pixels) * 25  # log10(10000) = 4 → 4 * 25 = 100
    score = int(round(min(score, 100)))     # Maximal 100

    return score

def get_activity_level(score):
    if score < 25:
        return "Bronze 🥉"
    elif score < 50:
        return "Silver 🥈"
    elif score < 75:
        return "Gold 🥇"
    else:
        return "Platin 🏆"
