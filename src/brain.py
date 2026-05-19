import json
import requests
import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel

class BushXIBrain:
    def __init__(self, config_path="config/robot_config.yaml"):
        # Giả lập đọc cấu hình đơn giản
        self.llava_url = "http://localhost:11434/api/generate"
        self.whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        self.sample_rate = 16000

    def record_voice(self, duration=5, filename="temp_command.wav"):
        """Thu âm từ microphone phần cứng"""
        print(f"\n[BUSHXI MIC] Đang lắng nghe trong {duration} giây...")
        recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='int16')
        sd.wait()
        wav.write(filename, self.sample_rate, recording)
        return filename

    def audio_to_text(self, audio_path):
        """Dịch sóng âm thanh tiếng Việt thành chữ"""
        segments, _ = self.whisper_model.transcribe(audio_path, beam_size=5, language="vi")
        text = "".join([seg.text for seg in segments]).strip()
        print(f"[BUSHXI WHISPER] Nhận diện: '{text}'")
        return text

    def think(self, image_path, voice_command):
        """Gửi ảnh và câu lệnh tới LLaVA để phân tích hành động"""
        system_prompt = f"""
        Bạn là hệ điều hành AI cấp cao của robot humanoid BushXI. Người dùng ra lệnh: "{voice_command}".
        Phân tích ảnh camera, chọn vật thể phù hợp và TRẢ VỀ CHÍNH XÁC chuỗi JSON sau, không viết gì thêm:
        {{
            "target_found": true,
            "object_name": "tên vật thể bằng tiếng Anh",
            "action": "PICK_UP" hoặc "WIPE",
            "hand": "right_hand" hoặc "left_hand"
        }}
        """
        try:
            response = requests.post(self.llava_url, json={
                "model": "llava", "prompt": system_prompt, "images": [image_path], "stream": False
            })
            return json.loads(response.text)['response'].strip()
        except Exception as e:
            return f"{{\"target_found\": false, \"error\": \"{str(e)}\"}}"

if __name__ == "__main__":
    brain = BushXIBrain()
    # Script chạy thử nghiệm độc lập module Brain
    audio_file = brain.record_voice()
    command = brain.audio_to_text(audio_file)
