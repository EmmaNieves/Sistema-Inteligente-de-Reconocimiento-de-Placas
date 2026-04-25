import cv2
import easyocr
import time
from ultralytics import YOLO

# Cargar modelos (se descargan la primera vez)
yolo_model = YOLO('yolov8n.pt')
reader = easyocr.Reader(['es'], gpu=False)

WINDOW_NAME = 'Camara en Vivo - Placas'


def _init_window():
    """Crea la ventana OpenCV de forma compatible con Windows."""
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 1280, 720)


def _draw_overlay(frame, detections, fps=None):
    """Dibuja encabezado, FPS y recuadros de deteccion sobre el frame."""
    h, w = frame.shape[:2]

    # Barra superior semitransparente
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 40), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

    cv2.putText(frame, 'Sistema Reconocimiento de Placas',
                (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)

    if fps is not None:
        cv2.putText(frame, f'FPS: {fps:.1f}',
                    (w - 130, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 200), 2)

    cv2.putText(frame, 'Presiona "q" para salir | "c" para capturar',
                (10, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)

    for (x1, y1, x2, y2, label, color) in detections:
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 6, y1), color, -1)
        cv2.putText(frame, label, (x1 + 3, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    return frame


def show_camera_live(camera_index=1):  
    """
    Muestra el feed en vivo continuo con deteccion de placas.
    'q' para salir, 'c' para capturar el frame actual.
    Devuelve lista de (plate_text, frame) capturados.
    """
    cap = cv2.VideoCapture("http://192.168.20.51:4747/video")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print('No se pudo abrir la camara.')
        return []

    _init_window()
    print('Camara en vivo iniciada.')
    print('  "q" para salir  |  "c" para capturar')

    detected_plates = []
    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print('No se pudo leer el frame.')
            break

        curr_time = time.time()
        fps = 1.0 / max(curr_time - prev_time, 1e-6)
        prev_time = curr_time

        # Deteccion YOLO
        results = yolo_model(frame, conf=0.5, verbose=False)
        detections = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                plate_crop = frame[y1:y2, x1:x2]
                if plate_crop.size == 0:
                    continue

                ocr_result = reader.readtext(
                    plate_crop,
                    allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
                )
                for (_, text, prob) in ocr_result:
                    if prob > 0.65 and len(text) >= 5:
                        plate_text = text.upper().replace(' ', '').replace('-', '')
                        detections.append((x1, y1, x2, y2, f'{plate_text} ({conf:.0%})', (0, 255, 0)))
                        print(f'Placa: {plate_text}  YOLO:{conf:.2f}  OCR:{prob:.2f}')
                    else:
                        detections.append((x1, y1, x2, y2, f'? {conf:.0%}', (0, 200, 255)))

        # Mostrar frame — siempre, aunque YOLO haya tardado
        display = _draw_overlay(frame.copy(), detections, fps)
        cv2.imshow(WINDOW_NAME, display)

        # waitKey DEBE llamarse en el mismo hilo que imshow (Windows requiere esto)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print('Cerrando...')
            break
        elif key == ord('c'):
            for (x1, y1, x2, y2, label, color) in detections:
                if color == (0, 255, 0):
                    plate_text = label.split(' ')[0]
                    print(f'Captura: {plate_text}')
                    detected_plates.append((plate_text, frame.copy()))
                    break
            else:
                print('No hay placa confirmada en este frame.')

    cap.release()
    cv2.destroyAllWindows()
    return detected_plates


def detect_plate_from_camera(camera_index=1, timeout_seconds=60):
    """
    Espera hasta detectar UNA placa y retorna (plate_text, frame).
    Muestra feed en vivo mientras espera. 'q' para cancelar.
    """
    cap = cv2.VideoCapture("http://192.168.20.51:4747/video")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print('No se pudo abrir la camara.')
        return None, None

    _init_window()
    print('Camara iniciada. Apunta a una placa... ("q" para cancelar)')
    start_time = time.time()
    prev_time = time.time()
    result_plate = None
    result_frame = None

    while time.time() - start_time < timeout_seconds:
        ret, frame = cap.read()
        if not ret:
            break

        curr_time = time.time()
        fps = 1.0 / max(curr_time - prev_time, 1e-6)
        prev_time = curr_time

        results = yolo_model(frame, conf=0.5, verbose=False)
        detections = []
        found = False

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                plate_crop = frame[y1:y2, x1:x2]
                if plate_crop.size == 0:
                    continue

                ocr_result = reader.readtext(
                    plate_crop,
                    allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
                )
                for (_, text, prob) in ocr_result:
                    if prob > 0.65 and len(text) >= 5:
                        plate_text = text.upper().replace(' ', '').replace('-', '')
                        print(f'Placa detectada: {plate_text} (YOLO:{conf:.2f} OCR:{prob:.2f})')
                        detections.append((x1, y1, x2, y2, f'{plate_text} ({conf:.0%})', (0, 255, 0)))
                        result_plate = plate_text
                        result_frame = frame.copy()
                        found = True
                    else:
                        detections.append((x1, y1, x2, y2, f'? {conf:.0%}', (0, 200, 255)))

        display = _draw_overlay(frame.copy(), detections, fps)
        cv2.imshow(WINDOW_NAME, display)

        # Siempre procesar eventos de ventana
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        if found:
            # Mostrar resultado 1.5s antes de cerrar
            cv2.waitKey(1500)
            break

    cap.release()
    cv2.destroyAllWindows()
    return result_plate, result_frame
