import cv2
import numpy as np
import requests
from ultralytics import YOLO

class BushXIVision:
    def __init__(self, model_name="yolov8n.pt"):
        # 1. Khởi tạo bộ não thị giác YOLOv8
        self.model = YOLO(model_name)
        self.clean_targets = ["bottle", "cup", "chair", "couch", "dining table"]
        
        # 2. Cấu hình danh sách nhạc thư giãn (Relax Melodies) cho chủ nhà
        # Trong thực tế, bạn có thể lưu các file .mp3 này vào thư mục assets/audio/
        self.relax_playlist = {
            "lofi": "assets/audio/lofi_chill.mp3",
            "classic": "assets/audio/piano_relax.mp3",
            "nature": "assets/audio/rain_forest.mp3"
        }

    def process_frame_with_depth(self, rgb_frame, depth_map):
        """
        HÀM CHUYÊN SÂU: Quét ảnh màu (RGB) kết hợp Bản đồ chiều sâu (Depth Map) 
        để tính toán chính xác tọa độ 3D (X, Y, Z) của rác/đồ đạc cần dọn.
        """
        results = self.model(rgb_frame, stream=True)
        detected_targets = []

        for result in results:
            annotated_frame = result.plot()
            for box in result.boxes:
                label = self.model.names[int(box.cls)]
                
                # Nếu phát hiện ra vật thể cần dọn dẹp
                if label in self.clean_targets:
                    # Lấy tọa độ hộp 2D (Tâm X, Tâm Y, Rộng W, Cao H) trên ảnh
                    x_center, y_center, w, h = box.xywh.tolist()
                    x_idx, y_idx = int(x_center), int(y_center)

                    # TỐI ƯU HÓA ĐO CHIỀU SÂU: Lấy khoảng cách thực tế (mét) từ camera đến vật thể
                    # Sử dụng vùng trung tâm 5x5 pixel để tránh sai số (noise) tại 1 điểm đơn lẻ
                    depth_roi = depth_map[y_idx-2:y_idx+3, x_idx-2:x_idx+3]
                    distance_z = np.median(depth_roi) if depth_roi.size > 0 else depth_map[y_idx, x_idx]

                    # Giả lập ma trận nội thông số Camera (Intrinsic Matrix) để đổi sang tọa độ 3D thực tế (X, Y, Z)
                    focal_length = 500.0  # Tiêu cự giả lập của camera trong Isaac Sim
                    cx, cy = 320.0, 240.0 # Tâm của ảnh độ phân giải 640x480
                    
                    real_x = (x_center - cx) * distance_z / focal_length
                    real_y = (y_center - cy) * distance_z / focal_length
                    real_z = distance_z # Khoảng cách thẳng từ mắt robot đến vật thể

                    detected_targets.append({
                        "object": label,
                        "distance_meters": real_z,
                        "3d_coordinate": (real_x, real_y, real_z)
                    })
                    
                    # Vẽ thêm thông số khoảng cách thực tế lên màn hình giám sát của robot
                    cv2.putText(annotated_frame, f"Z: {real_z:.2f}m", (int(box.xyxy[0][0]), int(box.xyxy[0][1]) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
        return annotated_frame, detected_targets

    def play_relax_music(self, genre="lofi"):
        """
        TÍNH NĂNG CHĂM SÓC: Robot tự phát nhạc giải tỏa căng thẳng cho gia chủ
        """
        if genre in self.relax_playlist:
            print(f"\n[BUSHXI MUSIC] 🎵 Đang phát bản nhạc thư giãn [{genre.upper()}] cho chủ nhà...")
            print(f"[ACTION] Gọi trình hệ thống mở file: {self.relax_playlist[genre]}")
            # Trong phần cứng thật (Jetson), ta sẽ dùng thư viện pygame:
            # import pygame; pygame.mixer.init(); pygame.mixer.music.load(file); pygame.mixer.music.play()
        else:
            print("[BUSHXI MUSIC] Không tìm thấy thể loại nhạc yêu cầu.")

    def get_weather_care_advice(self, city="Hanoi"):
        """
        TÍNH NĂNG QUẢN GIA/MẸ HIỀN: Tự động check thời tiết qua API thực tế 
        và đưa ra lời dặn dò ấm áp về cách ăn mặc cho chủ nhà yên tâm.
        """
        print(f"\n[BUSHXI WEATHER] Đang kiểm tra thời tiết thực tế tại {city}...")
        
        # Gọi API thời tiết miễn phí (Sử dụng Open-Meteo API không cần đăng ký key phức tạp)
        url = f"https://open-meteo.com"
        
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            temp = data['current']['temperature_2m']
            rain = data['current']['rain']
            
            # Tầng tư duy "Mẹ hiền/Quản gia": Dịch thông số số liệu khô khan thành lời dặn ấm áp
            advice = f"Thưa chủ nhà, hiện tại trời {temp}°C. "
            
            if temp < 18:
                advice += "Trời hôm nay khá lạnh đấy, bạn nhớ mặc thêm áo khoác dày và giữ ấm cổ trước khi ra ngoài nhé. 🧥🧣"
            elif temp > 32:
                advice += "Trời ngoài trời rất nắng nóng, bạn hãy mặc đồ thoáng mát, mang theo áo chống nắng và nhớ uống thật nhiều nước nha. ☀️🥛"
            else:
                advice += "Thời tiết mát mẻ dễ chịu, bạn có thể thoải mái diện những bộ đồ yêu thích. 👕"
                
            if rain > 0:
                advice += " À, bên ngoài đang có mưa rơi, đừng quên mang theo ô (dù) hoặc áo mưa bên mình nhé! 🌧️☔"
                
            print(f"[BUSHXI TÂM SỰ]: \"{advice}\"")
            return advice
            
        except Exception as e:
            # Lời thoại dự phòng nếu mất mạng internet
            backup_advice = "Thưa chủ nhà, tôi chưa kết nối được với trạm khí tượng, nhưng dù thời tiết thế nào, hãy luôn giữ sức khỏe thật tốt nhé!"
            print(f"[BUSHXI TÂM SỰ]: \"{backup_advice}\"")
            return backup_advice

# Kịch bản kiểm thử độc lập module Vision nâng cấp
if __name__ == "__main__":
    vision_system = BushXIVision()
    
    # 1. Thử nghiệm tính năng phát nhạc thư giãn
    vision_system.play_relax_music("lofi")
    
    # 2. Thử nghiệm tính năng quan tâm thời tiết ấm áp
    vision_system.get_weather_care_advice(city="Hanoi")
