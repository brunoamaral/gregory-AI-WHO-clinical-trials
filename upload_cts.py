#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys

def upload_file(file_path, source_id):
    """
    Copies a file to a remote server and executes a command on the server.

    Args:
        file_path (str): Path to the file to be copied.
        source_id (str): Source ID for the remote command.

    Raises:
        FileNotFoundError: If the file does not exist.
        EnvironmentError: If required environment variables are not set.
        RuntimeError: If copying the file or executing the remote command fails.
    """
    # Validate parameters
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    # Extract the filename
    filename = os.path.basename(file_path)

    # Remote server details
    from dotenv import load_dotenv

    load_dotenv()

    remote_user = os.getenv('REMOTE_USER')
    remote_host = os.getenv('REMOTE_HOST')
    remote_directory = os.getenv('REMOTE_DIRECTORY')

    if not all([remote_user, remote_host, remote_directory]):
        raise EnvironmentError("Please set REMOTE_USER, REMOTE_HOST, and REMOTE_DIRECTORY in the .env file.")

    # Copy the file to the remote server
    scp_command = [
        'scp',
        file_path,
        f"{remote_user}@{remote_host}:{remote_directory}"
    ]

    print(f"Copying file to remote server: {' '.join(scp_command)}")
    result = subprocess.run(scp_command)

    if result.returncode != 0:
        raise RuntimeError("Failed to copy the file to the remote server.")

    # Execute the command on the remote server
    ssh_command = [
        'ssh',
        f"{remote_user}@{remote_host}",
        f"cd {remote_directory} && "
        f"docker exec gregory python manage.py importWHOXML --file '{filename}' --source-id {source_id}"
    ]

    print(f"Executing command on remote server: {' '.join(ssh_command)}")
    result = subprocess.run(ssh_command)

    if result.returncode != 0:
        raise RuntimeError("Remote command execution failed.")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Copy a file to a remote server and execute a command.')
    parser.add_argument('--file', required=True, help='Path to the file to be copied')
    parser.add_argument('--source-id', required=True, help='Source ID for the remote command')

    args = parser.parse_args()

    file_path = args.file
    source_id = args.source_id

    try:
        upload_file(file_path, source_id)
        print("Upload completed successfully.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()