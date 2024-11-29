import os
import zipfile
import tarfile
from app.setup.settings import *  # Make sure settings.py defines OUTPUT_DIR and ROOT_DIR
from app.logs.logger_config import initialize_loggers

# Initialize all loggers
loggers = initialize_loggers()

def compress_folder(case_name, folder_path, output_dir, compression_type, case_number=None):
    """
    Compresses a given folder using the specified compression type and saves it in the output directory.

    Args:
        case_name (str): Name of the case for naming the compressed file.
        folder_path (str): Path to the folder to be compressed.
        output_dir (str): Path to the directory where the compressed file will be saved.
        compression_type (str): Compression type: "zip", "tar", or "tar.gz".
        case_number (str, optional): Case number to use in the output file name. Defaults to None.

    Raises:
        ValueError: If the specified compression type is not supported.
    """
    if not os.path.isdir(folder_path):
        raise ValueError("The provided folder path does not exist or is not a directory.")

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        loggers["compress"].warning(f"Output directory does not exist, creating directory at {output_dir}")
    
    # Count total files for progress calculation
    total_files = sum(len(files) for _, _, files in os.walk(folder_path))
    if total_files == 0:
        raise ValueError("The folder is empty and cannot be compressed.")

    # Replace spaces in case_name with underscores
    case_name = case_name.replace(" ", "_")
    
    # Determine the output file name based on the case number
    base_name = f"{case_name}_{case_number}" if case_number else "output"
    files_processed = 0  # Initialize counter for processed files

    # Add appropriate extension based on compression type
    if compression_type == "zip":
        output_path = os.path.join(output_dir, f"{base_name}.zip")
        loggers["compress"].info(f"Starting ZIP compression: {output_path}")

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
                    files_processed += 1
                    percentage = (files_processed / total_files) * 100
                    print(f"\rProgress: {percentage:.2f}% ({files_processed}/{total_files})\n", end="")
                    loggers["compress"].info(f"Added file to ZIP: {arcname}")

        loggers["compress"].info(f"Folder compressed successfully as ZIP: {output_path}")

    elif compression_type in ["tar", "tar.gz"]:
        extension = "tar.gz" if compression_type == "tar.gz" else "tar"
        output_path = os.path.join(output_dir, f"{base_name}.{extension}")
        loggers["compress"].info(f"Starting {compression_type.upper()} compression: {output_path}")

        mode = "w:gz" if compression_type == "tar.gz" else "w"
        with tarfile.open(output_path, mode) as tar:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    tar.add(file_path, arcname=os.path.relpath(file_path, folder_path))
                    files_processed += 1
                    percentage = (files_processed / total_files) * 100
                    print(f"\rProgress: {percentage:.2f}% ({files_processed}/{total_files})\n", end="")
                    loggers["compress"].info(f"Added file to {compression_type.upper()}: {file_path}")

        loggers["compress"].info(f"Folder compressed successfully as {compression_type.upper()}: {output_path}")

    else:
        raise ValueError("Unsupported compression type. Use 'zip', 'tar', or 'tar.gz'.")