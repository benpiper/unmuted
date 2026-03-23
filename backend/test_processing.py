import os
from scanner import scan_directory_for_videos
from extractor import extract_keyframes

def main():
    test_dir = "/home/user/unmuted"
    print(f"Scanning directory: {test_dir}")
    videos = scan_directory_for_videos(test_dir)
    print(f"Found {len(videos)} videos:")
    for v in videos:
        print(f" - {v}")
        
    if not videos:
        print("No videos found. Expected at least one test video.")
        return
        
    target_video = videos[0]
    output_frames_dir = os.path.join(test_dir, ".unmuted", "frames")
    print(f"Extracting frames for {target_video} to {output_frames_dir} at 1 fps...")
    frames = extract_keyframes(target_video, output_frames_dir, fps=1.0)
    print(f"Extracted {len(frames)} frames. First 5 frames:")
    for f in frames[:5]:
        print(f" - {f}")

if __name__ == "__main__":
    main()
