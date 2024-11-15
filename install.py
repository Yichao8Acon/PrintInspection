import subprocess
import sys


def install_requirements(requirements_file="requirements.txt", silent=False):
    """
    Check and install missing dependencies from requirements.txt.

    Parameters:
    - requirements_file: Path to the requirements.txt file.
    - silent: If True, suppresses the output of pip install.
    """
    try:
        with open(requirements_file, "r") as file:
            required_packages = file.read().splitlines()

        for package in required_packages:
            package_name = package.split('==')[0]  # Extract package name (ignoring version)

            try:
                __import__(package_name)  # Try importing the package
                print(f"{package_name} is already installed.")
            except ImportError:
                print(f"{package_name} not found. Installing...")
                install_command = [sys.executable, "-m", "pip", "install"]
                if silent:
                    install_command.append("--quiet")  # Add quiet flag if silent mode is enabled
                install_command.append(package)  # Add the package to the install command

                try:
                    subprocess.check_call(install_command)
                except subprocess.CalledProcessError as e:
                    print(f"Error installing {package_name}: {e}")

    except FileNotFoundError:
        print(f"{requirements_file} not found. Skipping dependency check.")

if __name__ == "__main__":
    install_requirements()