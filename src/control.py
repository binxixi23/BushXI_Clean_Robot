import numpy as np

class BushXIController:
    def __init__(self):
        print("[BUSHXI CONTROL] Đang khởi tạo bộ giải thuật động học ngược IK & RMPflow...")
        self.current_joints = np.zeros(19) # Giả lập 19 khớp của robot hình người

    def compute_safe_path(self, current_hand_pos, target_3d_pos, dynamic_obstacles):
        """
        Giả lập thuật toán RMPflow: Tính toán lực hút tới mục tiêu 
        và lực đẩy từ các chướng ngại vật động.
        """
        # Lực hút hướng tới rác
        attraction_vector = target_3d_pos - current_hand_pos
        
        # Lực đẩy từ vật cản động xung quanh (ví dụ: chân người đi qua)
        repulsion_vector = np.zeros(3)
        for obs in dynamic_obstacles:
            dist = np.linalg.norm(current_hand_pos - obs['pos'])
            if dist < obs['safe_radius']:
                # Tạo lực đẩy ngược lại hướng vật cản
                repulsion_vector += (current_hand_pos - obs['pos']) / (dist + 1e-5)

        # Quỹ đạo an toàn cuối cùng là sự hợp nhất của các lực trường vật lý ảo
        safe_direction = attraction_vector + repulsion_vector * 2.0
        return safe_direction

    def send_torque_to_hardware(self, joint_angles):
        """Đóng gói dữ liệu nhị phân gửi xuống vi điều khiển MCU qua CAN-Bus"""
        # Module này sẽ kết nối trực tiếp với kịch bản cổng Serial đã làm ở các bước trước
        pass
