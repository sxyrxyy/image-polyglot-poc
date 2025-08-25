import os
import sys
import glob

MARKER = b"\n__lolz__\n"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8"

def is_png(head: bytes) -> bool:  return head.startswith(PNG_MAGIC)
def is_jpeg(head: bytes) -> bool: return head.startswith(JPEG_MAGIC)

def bold(s: str) -> str:
    return f"\033[1m{s}\033[0m" if sys.stdout.isatty() else s

def green(s: str) -> str:
    return f"\033[92m{s}\033[0m" if sys.stdout.isatty() else s

def choose_image() -> str:
    # Find image files in current directory
    files = sorted(glob.glob("*.png") + glob.glob("*.jpg") + glob.glob("*.jpeg"))
    if files:
        print(bold("Found images in current folder:"))
        for idx, f in enumerate(files, 1):
            print(f"  [{idx}] {f}")
        print("  [0] Enter another path manually")
        try:
            choice = int(input("Select image number: ").strip())
        except Exception:
            choice = -1
        if 1 <= choice <= len(files):
            return files[choice-1]
    # fallback: manual path
    while True:
        p = input("Path to PNG/JPG: ").strip().strip('"').strip("'")
        if not p:
            continue
        if not os.path.isfile(p):
            print("File not found. Try again.")
            continue
        with open(p, "rb") as f:
            head = f.read(12)
        if not (is_png(head) or is_jpeg(head)):
            print("Not recognized as PNG/JPEG by magic bytes. Try another file.")
            continue
        return p

def prompt_payload_type() -> str:
    while True:
        t = input("Payload type [bash|ps|cmd]: ").strip().lower()
        if t in ("bash", "ps", "cmd"):
            return t
        print("Please enter one of: bash, powershell, cmd")

def prompt_script() -> str:
    print("\nPaste your script. End with Ctrl+D (Linux/macOS) or Ctrl+Z then Enter (Windows).")
    print("-" * 60)
    try:
        content = sys.stdin.read()
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
    script = content.strip("\n")
    if not script.strip():
        script = 'echo "Hello World"'
    return script + "\n"

def out_path_for(img_path: str) -> str:
    root, ext = os.path.splitext(img_path)
    ext = ext or ".png"
    return f"{root}_polyglot{ext}"

def main():
    img_path = choose_image()
    payload = prompt_payload_type()
    script = prompt_script()

    with open(img_path, "rb") as f:
        img = f.read()

    out_path = out_path_for(img_path)
    with open(out_path, "wb") as f:
        f.write(img + MARKER + script.encode("utf-8"))

    print("\n" + green(f"✅ Created {out_path}"))
    print()

    print(bold("Run the embedded script (copy one line):"))
    if payload == "bash":
        cmd = f"awk 'f{{print}} /^__lolz__$/ {{f=1; next}}' \"{out_path}\" | bash"
    elif payload == "ps":
        # Fixed version: extract bytes after marker, convert to Base64, run with -EncodedCommand
        cmd = (
            f"$f=\"{out_path}\";"
            f"$b=[IO.File]::ReadAllBytes($f);"
            f"$m=[Text.Encoding]::ASCII.GetBytes(\"`n__lolz__`n\");"
            f"$i=-1;for($p=0;$p -le $b.Length-$m.Length;$p++){{"
            f"$ok=$true;for($k=0;$k -lt $m.Length;$k++){{ if($b[$p+$k] -ne $m[$k]){{$ok=$false;break}} }} "
            f"if($ok){{$i=$p;break}} }};"
            f"if($i -lt 0){{throw \"Marker not found\"}};"
            f"$tail=[Text.Encoding]::UTF8.GetString($b,$i+$m.Length,$b.Length-$i-$m.Length);"
            f"$enc=[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($tail));"
            f"powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand $enc"
        )
    else:  # cmd
        cmd = (
            f"$s=(Get-Content -Raw \"{out_path}\") -split \"`r?`n\"; "
            f"$i=[Array]::IndexOf($s,\"__lolz__\"); "
            f"($s[($i+1)..($s.Length-1)] -join \"`r`n\") | cmd.exe /Q"
        )
    print(cmd)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user.")
