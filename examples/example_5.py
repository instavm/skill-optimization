# File processor with command injection
import os
import subprocess

def process_image(filename, output_format):
    """Convert image to different format."""
    # Command injection vulnerability
    command = f"convert {filename} output.{output_format}"
    os.system(command)
    return f"output.{output_format}"

def backup_files(directory):
    """Backup files from directory."""
    # Path traversal vulnerability
    backup_cmd = f"tar -czf backup.tar.gz {directory}"
    subprocess.call(backup_cmd, shell=True)

def get_file_info(filepath):
    """Get file information."""
    # Arbitrary file read
    with open(filepath) as f:
        content = f.read()
    return content

def delete_temp_files(pattern):
    """Delete temporary files."""
    # Dangerous glob pattern
    os.system(f"rm -rf /tmp/{pattern}")

# Usage
if __name__ == "__main__":
    user_input = input("Enter filename: ")
    process_image(user_input, "png")
