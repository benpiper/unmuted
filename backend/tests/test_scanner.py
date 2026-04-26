import pytest
from pathlib import Path
from scanner import scan_directory_for_videos

def test_scan_directory_for_videos_success(tmp_path):
    # Create dummy video files
    video1 = tmp_path / "video1.mp4"
    video2 = tmp_path / "video2.mkv"
    video1.write_text("dummy content")
    video2.write_text("dummy content")

    # Create a non-video file
    readme = tmp_path / "README.txt"
    readme.write_text("not a video")

    videos = scan_directory_for_videos(str(tmp_path))

    assert len(videos) == 2
    assert any(v.endswith("video1.mp4") for v in videos)
    assert any(v.endswith("video2.mkv") for v in videos)
    assert not any(v.endswith("README.txt") for v in videos)

def test_scan_directory_for_videos_empty(tmp_path):
    videos = scan_directory_for_videos(str(tmp_path))
    assert videos == []

def test_scan_directory_for_videos_sorting(tmp_path):
    (tmp_path / "b.mp4").write_text("content")
    (tmp_path / "a.mp4").write_text("content")
    (tmp_path / "c.mp4").write_text("content")

    videos = scan_directory_for_videos(str(tmp_path))

    assert len(videos) == 3
    assert videos[0].endswith("a.mp4")
    assert videos[1].endswith("b.mp4")
    assert videos[2].endswith("c.mp4")

def test_scan_directory_for_videos_case_insensitive(tmp_path):
    (tmp_path / "video.MP4").write_text("content")

    videos = scan_directory_for_videos(str(tmp_path))

    assert len(videos) == 1
    assert videos[0].endswith("video.MP4")

def test_scan_directory_non_existent():
    with pytest.raises(ValueError, match="does not exist"):
        scan_directory_for_videos("/non/existent/path/at/all")

def test_scan_directory_is_file(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("content")

    with pytest.raises(ValueError, match="is not a directory"):
        scan_directory_for_videos(str(file_path))
