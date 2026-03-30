import cv2
import os

video_path = 'public/earth-zoom.mp4'
output_dir = 'public/frames'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Open the video file
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error opening video stream or file {video_path}")
    exit(1)

frame_count = 0

print(f"Extracting frames from {video_path} into {output_dir}...")
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        frame_count += 1
        # Save frame as WebP with 80% quality
        output_path = os.path.join(output_dir, f'frame_{frame_count:04d}.webp')
        cv2.imwrite(output_path, frame, [cv2.IMWRITE_WEBP_QUALITY, 80])
        
        if frame_count % 100 == 0:
            print(f"Extracted {frame_count} frames...")
    else:
        break

cap.release()
print(f"Extraction complete! Total frames: {frame_count}")
