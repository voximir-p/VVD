import shutil
import subprocess as sp
import sys
import traceback
from collections.abc import Callable
from msvcrt import getch
from pathlib import Path

import yt_dlp


def catch_exceptions(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (yt_dlp.utils.DownloadError, FileNotFoundError, ValueError):
            print(traceback.format_exc())
            input("Press Enter to exit...")
            sys.exit()

    return wrapper


class Downloader:
    def __init__(self):
        self.video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.output_folder = Path.home() / "Downloads"

    def wait_key(self, prompt: str, key: bytes):
        print(prompt, end="", flush=True)
        while getch() != key:
            pass

    def open_in_explorer(self, path: Path):
        sp.Popen(f'explorer /select,"{path}"')

    def move_and_open(self, file_name: Path) -> None:
        finale_path = (self.output_folder / file_name.name).resolve()
        if finale_path.exists() and input("Do you want to overwrite existing file? [y/N]: ").lower() != "y":
            self.open_in_explorer(file_name)
        else:
            shutil.move(file_name, finale_path)
            self.open_in_explorer(finale_path)

    def download(self, url: str, format_id: str | int) -> Path:
        yt_opts = {
            "format": format_id,
            "quiet": True,
            "external_downloader": "aria2c",
            "external_downloader_args": {
                "aria2c": [
                    "-x", "16",      # connections per server
                    "-s", "16",      # split into 16 pieces
                    "-k", "1M",      # chunk size
                    "--min-split-size", "1M",
                    "--download-result=full"
                ]
            },
            "concurrent_fragment_downloads": 16
        }
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            formatted_name = (
                info["title"]
                .replace("\\", "⧹")
                .replace("/", "⧸")
                .replace(":", "：")
                .replace("*", "＊")
                .replace("?", "？")
                .replace('"', "＂")
                .replace("|", "｜")
            )
        return (Path() / f"{formatted_name} [{info["id"]}].{info["ext"]}").resolve()

    def download_video_with_audio(self, video_format_id: str, audio_format_id: str) -> Path:
        video_path = self.download(self.video_url, video_format_id)
        audio_path = self.download(self.video_url, audio_format_id)
        print(
            f"Video path: {video_path}\n"
            f"Audio path: {audio_path}\n"
            f"Video extension: {video_path.suffix}\n"
            f"Audio extension: {audio_path.suffix}\n"
        )

        temp_folder = Path("temp")
        temp_folder.mkdir(exist_ok=True)
        output_video_path = (temp_folder / video_path.name).resolve()
        command = (
            "ffmpeg",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", "copy",
            str(output_video_path),
        )
        print(f"Running command: {command}\n")
        sp.run(command, check=False)

        video_path.unlink()
        audio_path.unlink()

        return output_video_path

    def download_audio(self) -> None:
        audio_format_id = input("Select the audio format ID: ")
        file_name = self.download(self.video_url, audio_format_id)
        self.move_and_open(file_name)

    def download_video(self) -> None:
        video_format_id = input("Select the video format ID: ")
        file_name = self.download(self.video_url, video_format_id)
        self.move_and_open(file_name)

    def download_both(self) -> None:
        video_format_id = input("Select the video format ID: ")
        audio_format_id = input("Select the audio format ID: ")
        output_vid_path = self.download_video_with_audio(video_format_id, audio_format_id)
        self.move_and_open(output_vid_path)

    @catch_exceptions
    def main(self) -> None:
        self.video_url = input("Enter the video URL: ") or self.video_url
        download_type = (input("Select download type (video/audio/[both]): ") or "b")[0].lower()
        if download_type not in ("a", "v", "b"):
            print("Invalid download type!", end="")
            self.wait_key("Press 'Enter' to exit.", b"\r")
            return

        output_folder = input(f"Enter the output folder (Defaults to {self.output_folder}): ")
        if output_folder:
            self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)

        with yt_dlp.YoutubeDL({"quiet": True}) as info_ydl:
            info = info_ydl.extract_info(self.video_url, download=False)
            info_ydl.list_formats(info)

        if download_type == "a":
            self.download_audio()
        elif download_type == "v":
            self.download_video()
        else:
            self.download_both()

        print("Download completed!")


if __name__ == "__main__":
    downloader = Downloader()
    downloader.main()
