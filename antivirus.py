"""Plugin - Service to check for virus, malware and other threats """


import os
import pyclamd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_clamav():
    cd = pyclamd.ClamdAgnostic()
    if not cd.ping():
        logger.error("Could not connect to the ClamAV server")
        raise ConnectionError("Could not connect to the ClamAV server")
    logger.info("Connected to ClamAV server")
    return cd

def scan_directory(scan_path, clamav_instance):
    suspicious_files = []
    for root, dirs, files in os.walk(scan_path):
        for file in files:
            file_path = os.path.join(root, file)
            if is_suspicious(file_path, clamav_instance):
                logger.warning(f"Suspicious file detected: {file_path}")
                suspicious_files.append(file_path)
    return suspicious_files

def scan_for_viruses():
    cd = initialize_clamav()
    logger.info("Starting virus scan for the entire device...")
    suspicious_files = []

    exclude_dirs = ["/C:Program Files", "/C:Program Files (x86)", "/C:ProgramData", "/C:Windows"]

    for root in Path("/").iterdir():
        if root.is_dir() and str(root) not in exclude_dirs:
            logger.info(f"Scanning directory: {root}")
            suspicious_files.extend(scan_directory(root, cd))
    
    if suspicious_files:
        result_message = f"Suspicious files detected: {', '.join(suspicious_files)}"
        logger.info(result_message)
        return result_message
    else:
        result_message = "No threats detected."
        logger.info(result_message)
        return result_message

def is_suspicious(file_path, clamav_instance):
    try:
        scan_result = clamav_instance.scan_file(file_path)
        if scan_result:
            logger.info(f"File {file_path} is suspicious: {scan_result}")
            return True
    except Exception as e:
        logger.error(f"Error scanning file {file_path}: {e}")
    return False
