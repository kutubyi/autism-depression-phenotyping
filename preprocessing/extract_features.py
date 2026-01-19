import os
import subprocess
from pathlib import Path
import pandas as pd
import numpy as np


def extract_features_single_video(video_path, output_dir, openface_path=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Skip if already processed
    output_csv = output_dir / f"{video_path.stem}.csv"
    if output_csv.exists():
        print(f"Skipping {video_path.name} (already processed)")
        return True

    # Determine OpenFace command
    if openface_path:
        cmd = [openface_path]
    else:
        cmd = ["FeatureExtraction"]

    # Add arguments
    cmd.extend([
        "-f", str(video_path),
        "-out_dir", str(output_dir),
        "-aus",  # Extract action units
        "-pose",  # Extract head pose
        "-gaze"  # Extract gaze
    ])

    print(f"Processing: {video_path.name}")

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error processing {video_path.name}: {e}")
        return False


def aggregate_video_features(csv_path, participant_id):
    df = pd.read_csv(csv_path)

    # Define feature columns
    head_rotation = ['pose_Rx', 'pose_Ry', 'pose_Rz']  # 3 features
    action_units = ['AU01_r', 'AU02_r', 'AU04_r', 'AU05_r', 'AU06_r', 'AU07_r', 'AU12_r']  # 7 features

    # Filter successful frames (confidence > 0.5)
    if 'confidence' in df.columns:
        df = df[df['confidence'] > 0.5]

    if len(df) == 0:
        print(f"No valid frames for participant {participant_id}")
        return None

    # Aggregate statistics: mean for each feature
    aggregated = {'participant_id': participant_id}

    # Head rotation (3 features)
    for feature in head_rotation:
        if feature in df.columns:
            aggregated[feature] = df[feature].mean()
        else:
            print(f"Feature {feature} not found in {csv_path}")
            aggregated[feature] = np.nan

    # Action units (7 features)
    for feature in action_units:
        if feature in df.columns:
            aggregated[feature] = df[feature].mean()
        else:
            print(f"Feature {feature} not found in {csv_path}")
            aggregated[feature] = np.nan

    # Gaze (2 features - average both eyes)
    gaze_x_cols = ['gaze_0_x', 'gaze_1_x']
    gaze_y_cols = ['gaze_0_y', 'gaze_1_y']

    if all(col in df.columns for col in gaze_x_cols):
        aggregated['gaze_x'] = df[gaze_x_cols].mean(axis=1).mean()
    else:
        aggregated['gaze_x'] = np.nan

    if all(col in df.columns for col in gaze_y_cols):
        aggregated['gaze_y'] = df[gaze_y_cols].mean(axis=1).mean()
    else:
        aggregated['gaze_y'] = np.nan

    return aggregated


def process_all_videos(input_dir, openface_output_dir, final_output_csv, openface_path=None):
    input_path = Path(input_dir)
    video_files = sorted(input_path.glob("*.mp4"))

    if not video_files:
        print(f"No video files found in {input_dir}")
        return

    # Check which videos need processing
    openface_output_path = Path(openface_output_dir)
    to_process = [v for v in video_files if not (openface_output_path / f"{v.stem}.csv").exists()]

    print(f"Found {len(video_files)} videos, {len(to_process)} to process")

    # Extract features for each video
    for video_file in to_process:
        success = extract_features_single_video(
            video_file,
            openface_output_dir,
            openface_path
        )
        if not success:
            print(f"Failed to process {video_file.name}")

    # Move log files to separate directory
    openface_output_path = Path(openface_output_dir)
    log_dir = openface_output_path / "log"
    log_dir.mkdir(exist_ok=True)

    for log_file in openface_output_path.glob("*_of_details.txt"):
        log_file.rename(log_dir / log_file.name)

    print(f"Moved log files to {log_dir}")
    print("Aggregating features...")

    # Aggregate results
    all_features = []
    openface_output_path = Path(openface_output_dir)

    for video_file in video_files:
        participant_id = video_file.stem  # Filename without extension
        csv_file = openface_output_path / f"{participant_id}.csv"

        if not csv_file.exists():
            print(f"Warning: CSV not found for {participant_id}")
            continue

        features = aggregate_video_features(csv_file, participant_id)
        if features:
            all_features.append(features)

    # Save to CSV
    if all_features:
        features_df = pd.DataFrame(all_features)

        # Reorder columns: participant_id first, then features in order
        feature_order = ['participant_id',
                        'pose_Rx', 'pose_Ry', 'pose_Rz',  # Head rotation (3)
                        'AU01_r', 'AU02_r', 'AU04_r', 'AU05_r', 'AU06_r', 'AU07_r', 'AU12_r',  # AUs (7)
                        'gaze_x', 'gaze_y']  # Gaze (2)

        features_df = features_df[feature_order]
        features_df.to_csv(final_output_csv, index=False)
    else:
        print("No features extracted!")


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    input_dir = script_dir / "../data/cropped"
    openface_output_dir = script_dir / "../data/processed/openface_raw"
    final_output_csv = script_dir / "../data/processed/visual_features.csv"

    # If OpenFace is not in PATH, specify the full path here:
    openface_path = os.path.expanduser("~/OpenFace/build/bin/FeatureExtraction")

    # Check if the file exists, otherwise set to None to try PATH
    if not os.path.exists(openface_path):
        openface_path = None

    # Process all videos
    process_all_videos(input_dir, openface_output_dir, final_output_csv, openface_path)

    print("\nProcessing complete!")
