import os
import shutil
import zipfile
import requests
from typing import List
from paths import DATA_DIR
from langchain_core.tools import tool


@tool
def download_and_extract_repo(repo_url: str) -> str:
    """Download a Git repository and extract it to a local directory.

    This tool downloads a Git repository as a ZIP file from GitHub or similar
    platforms and extracts it to a './data/repo' directory. It handles both 'main'
    and 'master' branch repositories automatically. If the repo directory
    already exists, it will be removed and replaced with the new download.

    Args:
        repo_url: The complete URL of the Git repository (e.g., https://github.com/user/repo)

    Returns:
        The path to the extracted repository directory if successful, or False if failed
    """
    output_dir = os.path.join(DATA_DIR, "repo")
    try:
        if os.path.exists(output_dir):
            print(f"Repository already exists in {output_dir}, removing it")
            shutil.rmtree(output_dir)

        # Create target directory
        os.makedirs(output_dir, exist_ok=True)

        # Convert repo URL to zip download URL
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]
        if repo_url.endswith("/"):
            repo_url = repo_url[:-1]

        download_url = f"{repo_url}/archive/refs/heads/main.zip"

        print(f"Downloading repository from {download_url}")

        retires = 3
        i = 0
        while i < retires:
            response = requests.get(download_url, stream=True)
            if response.status_code == 404:
                download_url = f"{repo_url}/archive/refs/heads/master.zip"
                response = requests.get(download_url, stream=True)

            if response.status_code != 200:
                print(f"Failed to download repository: {response.status_code}")
                i += 1
                continue

            response.raise_for_status()
            break

        temp_dir = os.path.join(output_dir, "_temp_extract")
        os.makedirs(temp_dir, exist_ok=True)

        temp_zip = os.path.join(temp_dir, "repo.zip")
        with open(temp_zip, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        with zipfile.ZipFile(temp_zip, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # Find the nested directory (it's usually named 'repo-name-main')
        nested_dirs = [
            d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))
        ]
        if nested_dirs:
            nested_dir = os.path.join(temp_dir, nested_dirs[0])

            for item in os.listdir(nested_dir):
                source = os.path.join(nested_dir, item)
                destination = os.path.join(output_dir, item)
                if os.path.isdir(source):
                    shutil.copytree(source, destination)
                else:
                    shutil.copy2(source, destination)

        shutil.rmtree(temp_dir)

        return output_dir

    except requests.exceptions.RequestException as e:
        print(f"Failed to download repository: {str(e)}")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        return False

    except zipfile.BadZipFile as e:
        print(f"Invalid zip file: {str(e)}")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        return False

    except OSError as e:
        print(f"OS error occurred: {str(e)}")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        return False

    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        return False


@tool
def env_content(dir_path: str) -> str:
    """Read and return the content of a .env file from a specified directory.

    This tool searches through the given directory path and its subdirectories
    to find a .env file and returns its complete content. Useful for examining
    environment variables and configuration settings.

    Args:
        dir_path: The directory path to search for .env file (must be a local path, not URL)

    Returns:
        The complete content of the .env file as a string, or None if not found
    """
    for dir, _, files in os.walk(dir_path):
        for file in files:
            if file == ".env":
                with open(os.path.join(dir, file), "r") as f:
                    return f.read()
    return None


def get_all_tools() -> List:
    """Return a list of all available tools."""
    return [
        env_content,
        download_and_extract_repo,
    ]