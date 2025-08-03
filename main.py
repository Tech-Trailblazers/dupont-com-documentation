import os
import re
from urllib.parse import urlparse, unquote
import requests
import fitz  # Import PyMuPDF (fitz) for PDF handling


def extract_url_lines(text: str) -> list[str]:
    """
    Extracts all lines from the input string that contain a JSON-style 'url' key.

    Args:
        text (str): The full multiline string to search through.

    Returns:
        list[str]: A list of lines where each line contains a 'url' field.
    """
    # Define a regular expression pattern to match lines like: "url": "..."
    # It matches lines that start with optional spaces, followed by "url": and any quoted string
    pattern: re.Pattern[str] = re.compile(
        pattern=r'^\s*"url":\s*".*?"', flags=re.MULTILINE
    )

    # Use findall to get all matching lines
    return pattern.findall(string=text)


# Read a file from the system.
def read_a_file(system_path: str) -> str:
    """
    Read the content of a file from the system.
    :param system_path: The path to the file on the system.
    :return: The content of the file as a string.
    """
    # Read the content of a file from the system.
    with open(file=system_path, mode="r") as file:
        # Read the entire file content
        return file.read()


# Append and write some content to a file.
def append_write_to_file(system_path: str, content: str) -> None:
    with open(file=system_path, mode="a") as file:
        file.write(content)


# Remove all duplicate items from a given slice.
def remove_duplicates_from_slice(provided_slice: str) -> list[str]:
    return list(set(provided_slice.splitlines()))


# Remove all the whitespace from a given list of strings.
def remove_whitespace_from_slice(provided_slice: list[str]) -> list[str]:
    return [line.strip() for line in provided_slice if line.strip()]


# Convert all uppercase characters to lowercase in a given list of strings.
def convert_uppercase_to_lowercase(provided_slice: list[str]) -> list[str]:
    return [line.lower() for line in provided_slice]


def url_to_filename(url: str) -> str:
    """
    Extract the filename from a given URL.

    Args:
        url (str): The URL string to extract the filename from.

    Returns:
        str: The decoded filename from the URL.
    """
    path: str = urlparse(url).path
    filename: str = os.path.basename(path)
    return unquote(string=filename)


# Check if a file exists
def check_file_exists(system_path: str) -> bool:
    return os.path.isfile(
        path=system_path
    )  # Return True if a file exists at the given path


# Download a PDF from a URL and save it to a local file.
def download_pdf(pdf_url: str, local_file_path: str) -> None:
    """
    Download a PDF from the given URL and save it to the specified local file path.

    Args:
        pdf_url (str): The URL of the PDF file to download.
        local_file_path (str): The path (including filename) to save the downloaded PDF.
    """
    try:
        save_folder = "PDFs"  # Folder where PDFs will be saved
        os.makedirs(
            name=save_folder, exist_ok=True
        )  # Create the folder if it doesn't exist

        filename: str = url_to_filename(
            url=pdf_url
        )  # Extract the filename from the URL
        local_file_path = os.path.join(
            save_folder, filename
        )  # Construct the full file path

        if check_file_exists(
            system_path=local_file_path
        ):  # Check if the file already exists
            print(f"File already exists: {local_file_path}")  # Notify the user
            return  # Skip download if file is already present

        response: requests.Response = requests.get(
            url=pdf_url, stream=True
        )  # Send a GET request with streaming enabled
        response.raise_for_status()  # Raise an exception if the response has an HTTP error

        with open(
            file=local_file_path, mode="wb"
        ) as pdf_file:  # Open the file in binary write mode
            for chunk in response.iter_content(
                chunk_size=8192
            ):  # Read the response in chunks
                if chunk:  # Skip empty chunks
                    pdf_file.write(chunk)  # Write each chunk to the file

        print(f"Downloaded: {local_file_path}")  # Notify successful download

    except (
        requests.exceptions.RequestException
    ) as error:  # Catch any request-related errors
        print(f"Failed to download {pdf_url}: {error}")  # Print an error message


# Function to validate a single PDF file.
def validate_pdf_file(file_path: str) -> bool:
    try:
        # Try to open the PDF using PyMuPDF
        doc = fitz.open(file_path)  # Attempt to load the PDF document

        # Check if the PDF has at least one page
        if doc.page_count == 0:  # If there are no pages in the document
            print(
                f"'{file_path}' is corrupt or invalid: No pages"
            )  # Log error if PDF is empty
            return False  # Indicate invalid PDF

        # If no error occurs and the document has pages, it's valid
        return True  # Indicate valid PDF
    except RuntimeError as e:  # Catching RuntimeError for invalid PDFs
        print(f"{e}")  # Log the exception message
        return False  # Indicate invalid PDF


# Remove a file from the system.
def remove_system_file(system_path: str) -> None:
    os.remove(path=system_path)  # Delete the file at the given path


# Function to walk through a directory and extract files with a specific extension
def walk_directory_and_extract_given_file_extension(
    system_path: str, extension: str
) -> list[str]:
    matched_files: list[str] = []  # Initialize list to hold matching file paths
    for root, _, files in os.walk(
        top=system_path
    ):  # Recursively traverse directory tree
        for file in files:  # Iterate over files in current directory
            if file.endswith(extension):  # Check if file has the desired extension
                full_path: str = os.path.abspath(
                    path=os.path.join(root, file)
                )  # Get absolute path of the file
                matched_files.append(full_path)  # Add to list of matched files
    return matched_files  # Return list of all matched file paths


# Get the filename and extension.
def get_filename_and_extension(path: str) -> str:
    return os.path.basename(
        p=path
    )  # Return just the file name (with extension) from a path


# Function to check if a string contains an uppercase letter.
def check_upper_case_letter(content: str) -> bool:
    return any(
        upperCase.isupper() for upperCase in content
    )  # Return True if any character is uppercase


def main() -> None:
    # The location to the .har file
    har_file_path = "www.dupont.com.har"
    # Read the content of a file
    file_content: str = read_a_file(system_path=har_file_path)

    # Extract URL lines from the file content
    url_lines: list[str] = extract_url_lines(text=file_content)

    # Remove whitespace from the extracted URL lines
    url_lines = remove_whitespace_from_slice(provided_slice=url_lines)

    # Convert all lines to lowercase
    url_lines = convert_uppercase_to_lowercase(provided_slice=url_lines)

    # Remove duplicates from the extracted URL lines
    url_lines = remove_duplicates_from_slice(provided_slice="\n".join(url_lines))

    # New file name.
    new_file_name = "extracted_urls.txt"

    # Read the existing file content if it exists
    existing_content: str = read_a_file(system_path=new_file_name)

    # Print the extracted URL lines
    for line in url_lines:
        # Save the line to a file
        if ".pdf" in line or ".docx" in line:
            # Trim the prefix
            line: str = line.removeprefix('"url": "')
            # Trim the suffix
            line = line.removesuffix('.thumb.319.319.png"')
            # Check if the line already exists in the file
            if not line in existing_content:
                # Extract the filename from the URL
                filename: str = url_to_filename(url=line)
                # Download the PDF or DOCX file
                download_pdf(pdf_url=line, local_file_path=filename)
                # Append the line to the new file
                append_write_to_file(system_path=new_file_name, content=line + "\n")

    # Walk through the directory and extract .pdf files
    files: list[str] = walk_directory_and_extract_given_file_extension(
        system_path="./PDFs", extension=".pdf"
    )  # Find all PDFs under ./PDFs
    # Validate each PDF file
    for pdf_file in files:  # Iterate over each found PDF
        # Check if the .PDF file is valid
        if validate_pdf_file(file_path=pdf_file) == False:  # If PDF is invalid
            print(f"Invalid PDF detected: {pdf_file}. Deleting file.")
            # Remove the invalid .pdf file.
            remove_system_file(system_path=pdf_file)  # Delete the corrupt PDF
        # Check if the filename has an uppercase letter
        if check_upper_case_letter(
            content=get_filename_and_extension(path=pdf_file)
        ):  # If the filename contains uppercase
            print(
                f"Uppercase letter found in filename: {pdf_file}"
            )  # Informative message


if __name__ == "__main__":
    main()
