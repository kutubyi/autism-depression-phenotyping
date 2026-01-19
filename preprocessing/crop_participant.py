import os
import subprocess
from pathlib import Path


def crop_participant_videos(input_dir, output_dir, crop_ratio=0.5):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Get all video files
    video_files = sorted(input_path.glob("*.mp4"))

    if not video_files:
        print(f"No video files found in {input_dir}")
        return

    # Check which videos need processing
    to_process = [v for v in video_files if not (output_path / v.name).exists()]

    print(f"Found {len(video_files)} videos, {len(to_process)} need cropping")

    for video_file in to_process:
        output_file = output_path / video_file.name

        print(f"Processing {video_file.name}...")

        # crop=out_w:out_h:x:y
        # For right half: crop=iw*0.5:ih:iw*0.5:0
        crop_filter = f"crop=iw*{crop_ratio}:ih:iw*{1-crop_ratio}:0"

        cmd = [
            "ffmpeg",
            "-i", str(video_file),
            "-vf", crop_filter,
            "-c:a", "copy",  # Copy audio without re-encoding
            "-y",  # Overwrite output file if it exists
            str(output_file)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Saved to {output_file.name}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing {video_file.name}: {e}")
            print(e.stderr.decode())


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    raw_data_dir = script_dir / "../data/raw"
    processed_data_dir = script_dir / "../data/cropped"

    # Crop the right half (participant side)
    crop_participant_videos(raw_data_dir, processed_data_dir, crop_ratio=0.5)

    print("\nProcessing complete!")
