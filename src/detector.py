import cv2, os, time, yaml
from ultralytics import YOLO
import mediapipe as mp

CONFIG_PATH = "config/dev.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

os.makedirs(CFG["paths"]["alerts_dir"], exist_ok=True)
os.makedirs(CFG["paths"]["logs_dir"], exist_ok=True)

# تحميل نموذج YOLO
model = YOLO(CFG["detector"]["model_path"])

# كاشف الوجوه للتمويه
mp_face = mp.solutions.face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

def blur_faces_inplace(bgr):
    h, w = bgr.shape[:2]
    res = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    detections = mp_face.process(res).detections
    if detections:
        for det in detections:
            box = det.location_data.relative_bounding_box
            x1 = max(0, int(box.xmin * w)); y1 = max(0, int(box.ymin * h))
            x2 = min(w, x1 + int(box.width  * w)); y2 = min(h, y1 + int(box.height * h))
            roi = bgr[y1:y2, x1:x2]
            if roi.size:
                small = cv2.resize(roi, (16,16), interpolation=cv2.INTER_LINEAR)
                pix = cv2.resize(small, (x2-x1, y2-y1), interpolation=cv2.INTER_NEAREST)
                bgr[y1:y2, x1:x2] = pix
    return bgr

def main():
    src = CFG["camera"]["source"]
    cap = cv2.VideoCapture(src)
    if CFG["camera"].get("width"):  cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CFG["camera"]["width"])
    if CFG["camera"].get("height"): cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CFG["camera"]["height"])

    conf_th = CFG["detector"]["conf"]
    imgsz   = CFG["detector"]["imgsz"]

    # نافذة زمنية بسيطة لتأكيد الاكتشاف
    window, need = CFG["temporal"]["window"], CFG["temporal"]["confirm_frames"]
    history_hits = 0
    frame_buf = []

    while True:
        ok, frame = cap.read()
        if not ok: break

        # كشف
        res = model(frame, imgsz=imgsz, verbose=False)[0]
        hit = False
        for b in res.boxes:
            cls = int(b.cls[0].item())
            conf = float(b.conf[0].item())
            x1,y1,x2,y2 = map(int, b.xyxy[0].tolist())

            # مبدئياً، اعرض كل شيء (شخص/حقائب...) — لاحقاً نقيّد بفئاتنا
            color = (0,255,0)
            cv2.rectangle(frame, (x1,y1), (x2,y2), color, 2)
            cv2.putText(frame, f"{cls}:{conf:.2f}", (x1, y1-6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # إذا أردت اختبار قاعدة بسيطة: اعتبر أي كشف بثقة عالية "حدث"
            if conf >= conf_th:
                hit = True

        # التنعيم الزمني
        frame_buf.append(hit)
        if len(frame_buf) > window:
            frame_buf.pop(0)
        history_hits = sum(frame_buf)

        # عند التأكيد: احفظ لقطة مشوشة وجوه
        if history_hits >= need:
            ts = int(time.time())
            shot = frame.copy()
            if CFG["evidence"]["enable_face_blur"]:
                shot = blur_faces_inplace(shot)
            out_path = os.path.join(CFG["paths"]["alerts_dir"], f"alert_{ts}.jpg")
            cv2.imwrite(out_path, shot)
            # امسح النافذة حتى لا يحفظ كل فريم
            frame_buf = []

        cv2.imshow("VisionGuard - Preview", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
