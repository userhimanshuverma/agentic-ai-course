# Part 5 — File Organizer Agent

This agent performs **real automation**.

It organizes files in a folder by their type.

---

## What This Agent Does

1. Takes a folder path from the user
2. Scans all files in that folder
3. Detects file types by extension
4. Creates category subfolders
5. Moves files into proper folders

**Before:**
```
Downloads/
├── report.pdf
├── photo.jpg
├── data.csv
├── notes.txt
├── script.py
└── archive.zip
```

**After:**
```
Downloads/
├── Documents/
│   └── report.pdf
├── Images/
│   └── photo.jpg
├── Data/
│   └── data.csv
├── Text/
│   └── notes.txt
├── Code/
│   └── script.py
└── Archives/
    └── archive.zip
```

---

## File Categories

| Folder | Extensions |
|--------|------------|
| Images | .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .ico |
| Documents | .pdf, .doc, .docx, .txt, .rtf, .odt, .tex |
| Data | .csv, .xls, .xlsx, .json, .xml, .yaml, .yml, .db, .sql |
| Videos | .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm |
| Audio | .mp3, .wav, .flac, .aac, .ogg, .wma, .m4a |
| Archives | .zip, .rar, .7z, .tar, .gz, .bz2 |
| Code | .py, .js, .html, .css, .java, .cpp, .c, .h, .php, .rb, .go, .rs, .swift |
| Executables | .exe, .msi, .dmg, .pkg, .deb, .rpm |
| Others | Everything else |

---

## Requirements

- Python 3.8+
- No external dependencies (uses only standard library)

---

## Setup Instructions

### Step 1 — No Dependencies to Install

This agent uses only Python's built-in libraries:
- `os`
- `shutil`
- `json`
- `pathlib`

---

### Step 2 — Run the Agent

```bash
python agent.py
```

---

## How to Use

### Option 1: Organize a Specific Folder

```
Enter folder path to organize: C:\Users\YourName\Downloads
```

### Option 2: Test with Sample Files

```
Enter folder path to organize: test
```

This creates a test folder with sample files in your Downloads.

### Dry Run Mode

The agent asks if you want to preview first:

```
Preview first? (y/n): y
```

This shows what would happen without moving any files.

---

## Example Session

```
==================================================
📂 File Organizer Agent
==================================================

I will organize files in a folder by their type.

Enter folder path to organize (or 'test' for demo): test

✅ Created test folder: C:\Users\You\Downloads\test_organize
   Sample files created: report.pdf, photo.jpg, data.csv, notes.txt, script.py, archive.zip, song.mp3, video.mp4

Preview first? (y/n): y

📁 Target Folder: C:\Users\You\Downloads\test_organize
🔍 DRY RUN MODE - No files will be moved

=== PREVIEW ===

{
  "status": "success",
  "message": "Preview: 8 files would be organized",
  "folder": "C:\\Users\\You\\Downloads\\test_organize",
  "preview": {
    "Documents": ["report.pdf"],
    "Images": ["photo.jpg"],
    "Data": ["data.csv"],
    "Documents": ["notes.txt"],
    "Code": ["script.py"],
    "Archives": ["archive.zip"],
    "Audio": ["song.mp3"],
    "Videos": ["video.mp4"]
  }
}

Proceed with organization? (y/n): y

=== RESULT ===

{
  "status": "success",
  "message": "Organized 8 files",
  "folder": "C:\\Users\\You\\Downloads\\test_organize",
  "organized": {
    "Documents": ["report.pdf", "notes.txt"],
    "Images": ["photo.jpg"],
    "Data": ["data.csv"],
    "Code": ["script.py"],
    "Archives": ["archive.zip"],
    "Audio": ["song.mp3"],
    "Videos": ["video.mp4"]
  }
}

✅ Done!
```

---

## Architecture (Block Diagram)

```
+-------------+
|   User      |
+-------------+
        |
        v
+------------------+
|   agent.py       |
| (File Organizer  |
|     Agent)       |
+------------------+
        |
        v
+--------------------------+
| 1. Get Folder Path       |
+--------------------------+
        |
        v
+--------------------------+
| 2. Scan Files            |
+--------------------------+
        |
        v
+--------------------------+
| 3. Categorize by Ext     |
+--------------------------+
        |
        v
+--------------------------+
| 4. Create Folders        |
+--------------------------+
        |
        v
+--------------------------+
| 5. Move Files            |
+--------------------------+
        |
        v
+------------------+
| Return JSON      |
| Summary          |
+------------------+
```

---

## How the Code Works

### 1. File Categories Dictionary

```python
file_categories = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ...],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ...],
    ...
}
```

Maps folder names to file extensions.

---

### 2. Scanning Files

```python
files = [f for f in target_folder.iterdir() if f.is_file()]
```

Gets all files (not directories) in the target folder.

---

### 3. Categorizing Files

```python
for category, extensions in file_categories.items():
    if file_ext in extensions:
        # Move to this category
```

Matches file extension to category.

---

### 4. Creating Folders

```python
category_folder = target_folder / category
category_folder.mkdir(exist_ok=True)
```

Creates category folder if it doesn't exist.

---

### 5. Moving Files

```python
shutil.move(str(file_path), str(destination))
```

Moves file to the appropriate folder.

---

### 6. Dry Run Mode

```python
def preview_files_tool(folder_path: str):
    # Shows what would happen
    # Without actually moving files
```

Preview mode for safety.

---

## Safety Features

| Feature | Description |
|---------|-------------|
| Dry Run | Preview before organizing |
| Confirmation | Ask before proceeding |
| Duplicate Handling | Renames duplicates (file_1.txt) |
| Path Validation | Checks if folder exists |
| Only Files | Ignores subdirectories |

---

## What You Just Built

This agent demonstrates:

- **File system operations**
- **Pattern matching** (by extension)
- **Batch processing**
- **Safe automation** (dry run, confirmation)

This is the foundation for:

- File management systems
- Automated organizers
- Data pipeline tools
- Backup systems

---

## No LLM Required!

Unlike previous parts, this agent:
- ✅ Does NOT use Ollama
- ✅ Does NOT need Mistral
- ✅ Works completely offline
- ✅ Uses only Python standard library

This is a **pure automation** agent!
