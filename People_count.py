import cv2
import time
from ultralytics import YOLO
from deep_sort import DeepSort    # deepsort pytorch repo
import torch

model = YOLO('yolov8n.pt')

deepsort = DeepSort(
    model_path="deep_sort/deep/checkpoint/ckpt.t7",
    max_dist=0.2,        # max_cosine_distance
    min_confidence=0.3,  # detection confidence
    nms_max_overlap=1.0,
    max_iou_distance=0.7,
    max_age=30,
    n_init=3,
    nn_budget=100,
    use_cuda=False
)

video_path = "people.mp4"
out_video_path = "people_counter_output.mp4"
cap = cv2.VideoCapture(video_path)

PEOPLE_CLASS_ID = 0 

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
fps = int(cap.get(cv2.CAP_PROP_FPS))


fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(out_video_path, fourcc, fps, (frame_width, frame_height))

frame_count = 0
start = time.time()


# Lists to store unique People IDs for counting
people_counter_id = []



while cap.isOpened():
    start_time = time.time()
    
    ret, frame = cap.read()

    
    if not ret:
        break
    # -----------------------------------YOLOv8 Detection--------------------------
    results = model.predict(source=frame, conf=0.4, classes=[PEOPLE_CLASS_ID], save=False, verbose=False, imgsz=640)
    if results[0].boxes is None:
        continue
    
    xywhs = results[0].boxes.xywh.cpu().numpy()  # Get bounding box coordinates
    class_ids = results[0].boxes.cls.cpu().numpy()  # Get class IDs
    scores = results[0].boxes.conf.cpu().numpy()  # Get confidence scores

    if len(xywhs) == 0:
        continue
    # -----------------------------------DeepSORT Tracking-------------------------
    tracks = deepsort.update(torch.Tensor(xywhs), scores, class_ids, frame)
    if tracks is None or len(tracks) == 0:
        continue
    bboxes = tracks[:, :4]
    identities = tracks[:, -2]
    for i, box in enumerate(bboxes):
        x1, y1, x2, y2 = [int(coord) for coord in box]
        track_id = int(identities[i]) if identities is not None else 0
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
        # -------------------People Counting Logic---------------------
        if track_id not in people_counter_id:
            people_counter_id.append(track_id)
        
    # Count the total People detected in variable people_counter
    current_frame_total_people_track_Id = len(people_counter_id)

    end_time = time.time()
    fps = 1 / (end_time - start_time)
    frame_count += 1
    print(f'trame_count: {frame_count} FPS: {fps:.2f}')
    cv2.putText(frame, f'People count: {current_frame_total_people_track_Id}', (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 4)

    #cv2.imshow('people Tracking', frame)
    out.write(frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break


cap.release()
out.release()
cv2.destroyAllWindows()

total_time = time.time() - start
average_fps = frame_count / total_time if total_time > 0 else 0
print(f'Average FPS: {average_fps:.2f}')
print(f'Total peoples in Video : {current_frame_total_people_track_Id}')