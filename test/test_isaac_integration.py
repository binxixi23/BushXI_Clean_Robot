import cv2
import numpy as np
from src.brain import BushXIBrain
from src.vision import BushXIVision
from src.control import BushXIController

def run_simulation_test():
    """Kịch bản kiểm thử tích hợp toàn hệ thống trong Isaac Sim"""
    print("[TEST] Bắt đầu khởi chạy hệ thống giả lập tích hợp...")
    
    # Khởi tạo 3 module cốt lõi của BushXI
    brain = BushXIBrain()
    vision = BushXIVision()
    controller = BushXIController()

    # Giả lập vòng lặp xử lý của robot (Simulation Tick Loop)
    # Trong thực tế, bạn sẽ lấy ảnh trực tiếp từ `robot_camera.get_current_frame()`
    dummy_camera_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(dummy_camera_frame, "Bottle on table", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # 1. Tầng thị giác quét camera
    annotated_img, objects = vision.process_frame(dummy_camera_frame)
    print(f"[TEST VISION] Đã quét xong. Tìm thấy {len(objects)} vật thể mục tiêu.")

    # 2. Giả lập chướng ngại vật động xuất hiện (Ví dụ: Con người ở tọa độ X=0.6, Y=0.2)
    obstacles = [{'pos': np.array([0.6, 0.2, 0.4]), 'safe_radius': 0.3}]
    
    # 3. Tầng điều khiển tính toán hướng đi an toàn thông qua RMPflow
    hand_pos = np.array([0.1, 0.0, 0.2])
    target_pos = np.array([0.5, 0.0, 0.2]) # Vị trí chai nước
    
    action_vector = controller.compute_safe_path(hand_pos, target_pos, obstacles)
    print(f"[TEST CONTROL] Vectơ di chuyển an toàn được tính bởi RMPflow: {action_vector}")
    print("[TEST] Kiểm thử tích hợp module hoàn thành thành công!")

if __name__ == "__main__":
    run_simulation_test()
