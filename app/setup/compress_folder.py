import os
import zipfile
import tarfile
from app.setup.settings import *  # Make sure settings.py defines OUTPUT_DIR and ROOT_DIR
from app.logs.logger_config import initialize_loggers

# Initialize all loggers
loggers = initialize_loggers()

def compress_folder(folder_path, output_dir, compression_type, case_number=None):
    """
    Compresses a given folder using the specified compression type and saves it in the output directory.

    Args:
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
        loggers["acquisition"].warning(f"Output directory does not exist, creating directory at {output_dir}")
    
    # Determine the output file name based on the case number
    base_name = "case_"+case_number if case_number else "output"

    # Add appropriate extension based on compression type
    if compression_type == "zip":
        output_path = os.path.join(output_dir, f"{base_name}.zip")
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
        loggers["acquisition"].info(f"Folder compressed successfully as ZIP: {output_path}")

    elif compression_type in ["tar", "tar.gz"]:
        extension = "tar.gz" if compression_type == "tar.gz" else "tar"
        output_path = os.path.join(output_dir, f"{base_name}.{extension}")
        mode = "w:gz" if compression_type == "tar.gz" else "w"
        with tarfile.open(output_path, mode) as tar:
            tar.add(folder_path, arcname=os.path.basename(folder_path))
        loggers["acquisition"].info(f"Folder compressed successfully as {compression_type.upper()}: {output_path}")
    
    else:
        raise ValueError("Unsupported compression type. Use 'zip', 'tar', or 'tar.gz'.")
