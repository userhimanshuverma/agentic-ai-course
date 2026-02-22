import os
import shutil
import json
from pathlib import Path


# -----------------------------
# 📁 TOOL: File Organizer
# -----------------------------
def file_organizer_tool(folder_path: str):
    """
    Organizes files in a folder by their type.
    Creates subfolders and moves files into appropriate categories.
    """
    # Define file categories and their extensions
    file_categories = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".tex"],
        "Data": [".csv", ".xls", ".xlsx", ".json", ".xml", ".yaml", ".yml", ".db", ".sql"],
        "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
        "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".php", ".rb", ".go", ".rs", ".swift"],
        "Executables": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"]
    }

    # Convert to Path object
    target_folder = Path(folder_path).expanduser().resolve()

    # Check if folder exists
    if not target_folder.exists():
        return {
            "status": "error",
            "message": f"Folder not found: {folder_path}"
        }

    if not target_folder.is_dir():
        return {
            "status": "error",
            "message": f"Path is not a directory: {folder_path}"
        }

    # Track organized files
    organized = {category: [] for category in file_categories.keys()}
    organized["Others"] = []

    # Get all files (not directories)
    files = [f for f in target_folder.iterdir() if f.is_file()]

    if not files:
        return {
            "status": "success",
            "message": "No files to organize",
            "folder": str(target_folder),
            "organized": {}
        }

    # Process each file
    for file_path in files:
        file_ext = file_path.suffix.lower()
        file_name = file_path.name

        # Find the category for this file
        category_found = False
        for category, extensions in file_categories.items():
            if file_ext in extensions:
                # Create category folder if it doesn't exist
                category_folder = target_folder / category
                category_folder.mkdir(exist_ok=True)

                # Move file to category folder
                destination = category_folder / file_name

                # Handle duplicate filenames
                counter = 1
                while destination.exists():
                    stem = file_path.stem
                    destination = category_folder / f"{stem}_{counter}{file_ext}"
                    counter += 1

                shutil.move(str(file_path), str(destination))
                organized[category].append(file_name)
                category_found = True
                break

        # If no category matched, put in Others
        if not category_found:
            others_folder = target_folder / "Others"
            others_folder.mkdir(exist_ok=True)
            destination = others_folder / file_name

            # Handle duplicate filenames
            counter = 1
            while destination.exists():
                stem = file_path.stem
                destination = others_folder / f"{stem}_{counter}{file_ext}"
                counter += 1

            shutil.move(str(file_path), str(destination))
            organized["Others"].append(file_name)

    # Remove summary (only include categories that have files)
    organized = {k: v for k, v in organized.items() if v}

    return {
        "status": "success",
        "message": f"Organized {len(files)} files",
        "folder": str(target_folder),
        "organized": organized
    }


# -----------------------------
# 📊 TOOL: Preview Files (Dry Run)
# -----------------------------
def preview_files_tool(folder_path: str):
    """
    Shows what would happen without actually moving files.
    """
    file_categories = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".tex"],
        "Data": [".csv", ".xls", ".xlsx", ".json", ".xml", ".yaml", ".yml", ".db", ".sql"],
        "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
        "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".php", ".rb", ".go", ".rs", ".swift"],
        "Executables": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"]
    }

    target_folder = Path(folder_path).expanduser().resolve()

    if not target_folder.exists():
        return {"status": "error", "message": f"Folder not found: {folder_path}"}

    files = [f for f in target_folder.iterdir() if f.is_file()]

    if not files:
        return {"status": "success", "message": "No files to organize", "preview": {}}

    preview = {category: [] for category in file_categories.keys()}
    preview["Others"] = []

    for file_path in files:
        file_ext = file_path.suffix.lower()
        file_name = file_path.name

        categorized = False
        for category, extensions in file_categories.items():
            if file_ext in extensions:
                preview[category].append(file_name)
                categorized = True
                break

        if not categorized:
            preview["Others"].append(file_name)

    # Remove empty categories
    preview = {k: v for k, v in preview.items() if v}

    return {
        "status": "success",
        "message": f"Preview: {len(files)} files would be organized",
        "folder": str(target_folder),
        "preview": preview
    }


# -----------------------------
# 🤖 AGENT: File Organizer Agent
# -----------------------------
def file_organizer_agent(folder_path: str, dry_run: bool = False):
    """
    Main agent function that organizes files.

    Args:
        folder_path: Path to the folder to organize
        dry_run: If True, only preview without moving files
    """
    print(f"\n📁 Target Folder: {folder_path}")

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be moved\n")
        return preview_files_tool(folder_path)
    else:
        print("🚀 Organizing files...\n")
        return file_organizer_tool(folder_path)


# -----------------------------
# 🚀 MAIN
# -----------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("📂 File Organizer Agent")
    print("=" * 50)
    print("\nI will organize files in a folder by their type.")
    print("Supported categories: Images, Documents, Data, Videos,")
    print("                     Audio, Archives, Code, Executables, Others")
    print()

    # Get folder path from user
    folder_path = input("Enter folder path to organize (or 'test' for demo): ").strip()

    if folder_path.lower() in ['exit', 'quit', 'bye']:
        print("\n👋 Goodbye!")
        exit()

    # Create test folder if user types 'test'
    if folder_path.lower() == 'test':
        test_folder = Path.home() / "Downloads" / "test_organize"
        test_folder.mkdir(parents=True, exist_ok=True)

        # Create sample files
        sample_files = [
            "report.pdf", "photo.jpg", "data.csv", "notes.txt",
            "script.py", "archive.zip", "song.mp3", "video.mp4"
        ]

        for filename in sample_files:
            (test_folder / filename).touch()

        print(f"\n✅ Created test folder: {test_folder}")
        print("   Sample files created:", ", ".join(sample_files))
        folder_path = str(test_folder)

    # Ask for dry run
    dry_run_input = input("\nPreview first? (y/n): ").strip().lower()
    dry_run = dry_run_input in ['y', 'yes']

    if dry_run:
        result = file_organizer_agent(folder_path, dry_run=True)
        print("\n=== PREVIEW ===\n")
        print(json.dumps(result, indent=2))

        confirm = input("\nProceed with organization? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            result = file_organizer_agent(folder_path, dry_run=False)
            print("\n=== RESULT ===\n")
            print(json.dumps(result, indent=2))
        else:
            print("\n❌ Cancelled. No files were moved.")
    else:
        result = file_organizer_agent(folder_path, dry_run=False)
        print("\n=== RESULT ===\n")
        print(json.dumps(result, indent=2))

    print("\n✅ Done!")
