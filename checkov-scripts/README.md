# Checkov failed check summarizer script

Failed check_id sorted from the biggest count

## Usage
1. Install the dependencies
    ```
    pip install -r requirements.txt
    ```
2. Run the script
    - From current directory
        ```
        python failed_summarizer.py -d .
        ```
     - From base repo directory
        ```
        python scripts/security/checkov/failed_summarizer.py -d . --base-dir $PWD
        ```

## Options
See `python failed_summarizer --help`
| Name            | Description                                         | Note                                                       |
| --------------- | --------------------------------------------------- | ---------------------------------------------------------- |
| --directory, -d | Target directory to check, can use multiple options | e.g. `.. -d <dir1> -d <dir2> ..`                           |
| --base-dir      | Base directory                                      |                                                            |
| --format        | Output format                                       | Current supported format: `text`, `json`                   |

## Next Development
- [ ] Print with tiered directory
- [ ] Custom output target
- [x] Integration with github action
