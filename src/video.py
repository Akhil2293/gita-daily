import os, subprocess
from common import *
DUR = [float(x) for x in os.environ.get("SLIDE_SECONDS", "4,5,6,6,4").split(",")]
def make():
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for i, d in enumerate(DUR, 1): cmd += ["-loop", "1", "-t", str(d), "-i", str(OUT / f"slide{i}.jpg")]
    music = ROOT / "template" / "assets" / "music.mp3"            # optional: drop a royalty-free track here
    if music.exists(): cmd += ["-i", str(music)]
    n = len(DUR)
    cmd += ["-filter_complex", "".join(f"[{i}:v]scale=1080:1920,setsar=1,fps=30[v{i}];" for i in range(n)) + "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]",
            "-map", "[v]"]
    if music.exists(): cmd += ["-map", f"{n}:a", "-shortest", "-c:a", "aac", "-b:a", "128k"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", str(OUT / "reel.mp4")]
    subprocess.run(cmd, check=True)
if __name__ == "__main__": make()
