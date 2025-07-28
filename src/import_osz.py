import os
import zipfile
import tempfile
import shutil
import time
import psutil
import random
import argparse
import sys

# Couleurs inspirées osu! (roses / violets / cyan)
class Colors:
    HEADER = '\033[95m'     # violet clair
    PINK = '\033[95m'       # même que HEADER pour rose/violet
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

OSU_PROCESS_NAME = "osu!.exe"
IMPORTER_MEMORY_MAX = 80 * 1024 * 1024  # 80 Mo

def count_import_processes():
    count = 0
    for proc in psutil.process_iter(['name', 'memory_info']):
        if proc.info['name'] == OSU_PROCESS_NAME:
            try:
                if proc.memory_info().rss < IMPORTER_MEMORY_MAX:
                    count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    return count

def wait_for_imports(expected_count):
    print(f"{Colors.CYAN}Waiting for {expected_count} import(s) to finish...{Colors.RESET}")
    while True:
        current = count_import_processes()
        done = expected_count - current
        print(f"{Colors.PINK}Imported: {done}/{expected_count}{Colors.RESET}", end="\r", flush=True)
        if current == 0:
            break
        time.sleep(0.2)
    print()

def import_osz(path: str, batch_size=5):
    temp_dir = None
    try:
        if path.endswith('.zip'):
            temp_dir = tempfile.mkdtemp()
            print(f"{Colors.BLUE}Extracting '{path}' to '{temp_dir}'...{Colors.RESET}")
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            search_path = temp_dir
        else:
            search_path = path

        if not os.path.isdir(search_path):
            print(f"{Colors.RED}Error: Directory not found at '{search_path}'{Colors.RESET}")
            return 1

        osz_files = [f for f in os.listdir(search_path) if f.endswith('.osz')]
        total = len(osz_files)
        if total == 0:
            print(f"{Colors.YELLOW}No .osz files found in '{search_path}'.{Colors.RESET}")
            return 1

        success_count = 0
        print(f"{Colors.HEADER}Found {total} .osz file(s) in '{search_path}'.{Colors.RESET}")

        for i in range(0, total, batch_size):
            batch = osz_files[i:i+batch_size]
            print(f"\n{Colors.BOLD}[{success_count+1}/{total}]{Colors.RESET} Launching batch {i//batch_size + 1} with {len(batch)} file(s)...")

            for osz_file in batch:
                full_path = os.path.join(search_path, osz_file)
                try:
                    os.startfile(full_path)
                    print(f"{Colors.GREEN}Launched: '{osz_file}'{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.RED}Failed to launch '{osz_file}': {e}{Colors.RESET}")

            wait_for_imports(len(batch))
            success_count += len(batch)

            imported_file = random.choice(batch)
            print(f"{Colors.CYAN}imported : '{imported_file}'{Colors.RESET}")
            print(f"{Colors.PINK}Progress: {success_count}/{total} beatmaps imported.{Colors.RESET}")

        print(f"\n{Colors.GREEN}✅ Finished: {success_count}/{total} beatmaps successfully imported.{Colors.RESET}")
        return 0

    except Exception as e:
        print(f"{Colors.RED}An error occurred: {e}{Colors.RESET}")
        return 1

    finally:
        if temp_dir and os.path.exists(temp_dir):
            print(f"{Colors.BLUE}Cleaning up temporary directory: {temp_dir}{Colors.RESET}")
            shutil.rmtree(temp_dir)

def main():
    parser = argparse.ArgumentParser(description=f"{Colors.PINK}Batch import osu! beatmaps from .osz files or zip archive.{Colors.RESET}")
    parser.add_argument('path', help="Path to a directory with .osz files or a .zip archive containing them")
    parser.add_argument('--batch-size', type=int, default=5, help="Number of files to import concurrently (default: 5)")

    args = parser.parse_args()

    exit_code = import_osz(args.path, args.batch_size)
    print(f"{Colors.BOLD}Importer script finished.{Colors.RESET}")
    print(f"{Colors.HEADER}This CLI Tool was created by iSweat, you can find me on GitHub at https://github.com/iSweat and you can also find me on Discord at isweatmc, if you have any questions or suggestions feel free to contact me, if you want support the project you can star the repository on GitHub, it would be greatly appreciated.{Colors.RESET}")
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
