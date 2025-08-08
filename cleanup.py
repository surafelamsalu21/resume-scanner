#!/usr/bin/env python3
import os
import shutil
import sys
from datetime import datetime

# Get confirmation from user


def confirm(message):
    response = input(f"{message} (y/n): ").lower().strip()
    return response == 'y' or response == 'yes'

# Log the deletion process


def log_deletion(item_path):
    print(f"Deleted: {item_path}")


# Files to delete
files_to_delete = [
    # Debug and test files
    "debug_cv_processing.py",
    "debug_login.py",
    "test_login.py",
    "test_app.py",
    "test_admin_routes.py",
    "test_openai.py",

    # Temporary or generated files
    "job_match_response.txt",
    "openai_response.txt"
]

# Directories to delete
dirs_to_delete = [
    "__pycache__",
    "logs"
]

# Optional: Clean up old uploads (keeping only the most recent ones)


def cleanup_uploads(uploads_dir, keep_latest=3):
    if not os.path.exists(uploads_dir):
        print(f"Uploads directory not found: {uploads_dir}")
        return

    # Group files by base name (without timestamp)
    file_groups = {}
    for filename in os.listdir(uploads_dir):
        # Skip directories
        if os.path.isdir(os.path.join(uploads_dir, filename)):
            continue

        # Parse timestamp and base name
        parts = filename.split('_', 1)
        if len(parts) > 1:
            timestamp = parts[0]
            base_name = parts[1]

            if base_name not in file_groups:
                file_groups[base_name] = []

            file_groups[base_name].append({
                'filename': filename,
                'timestamp': timestamp,
                'path': os.path.join(uploads_dir, filename)
            })

    # For each group, keep only the latest files
    deleted_count = 0
    for base_name, files in file_groups.items():
        # Sort by timestamp (newest first)
        sorted_files = sorted(
            files, key=lambda x: x['timestamp'], reverse=True)

        # Delete older files, keeping the latest 'keep_latest'
        if len(sorted_files) > keep_latest:
            for file_info in sorted_files[keep_latest:]:
                if os.path.exists(file_info['path']):
                    os.remove(file_info['path'])
                    log_deletion(file_info['path'])
                    deleted_count += 1

    print(f"Cleaned up {deleted_count} old upload files")


def main():
    print("Resume AI Backend Cleanup Script")
    print("================================")
    print("This script will delete unnecessary files and directories.")
    print("Files to be deleted:")
    for file in files_to_delete:
        print(f" - {file}")
    print("\nDirectories to be deleted:")
    for directory in dirs_to_delete:
        print(f" - {directory}")

    print("\nOptional: Clean up old uploads (keeping only the most recent versions)")

    if not confirm("\nDo you want to proceed with deletion?"):
        print("Operation cancelled.")
        return

    # Create a backup directory
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Created backup directory: {backup_dir}")

    # Delete files
    for file in files_to_delete:
        if os.path.exists(file):
            # Backup the file
            try:
                shutil.copy2(file, os.path.join(backup_dir, file))
                print(f"Backed up: {file}")

                # Delete the file
                os.remove(file)
                log_deletion(file)
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")
        else:
            print(f"File not found: {file}")

    # Delete directories
    for directory in dirs_to_delete:
        if os.path.exists(directory):
            try:
                # Backup the directory
                # Only backup non-empty directories
                if os.path.isdir(directory) and os.listdir(directory):
                    shutil.copytree(directory, os.path.join(
                        backup_dir, directory))
                    print(f"Backed up: {directory}")

                # Delete the directory
                shutil.rmtree(directory)
                log_deletion(directory)
            except Exception as e:
                print(f"Error processing {directory}: {str(e)}")
        else:
            print(f"Directory not found: {directory}")

    # Optional: Clean up uploads
    if confirm("Do you want to clean up old uploads (keeping only the 3 most recent versions)?"):
        cleanup_uploads("uploads", keep_latest=3)

    print("\nCleanup completed successfully!")
    print(f"A backup of all deleted files was created in: {backup_dir}")
    print("If you need to restore any files, you can find them in the backup directory.")


if __name__ == "__main__":
    main()
