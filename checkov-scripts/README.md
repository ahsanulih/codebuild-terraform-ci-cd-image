# Checkov check summarizer script

Checkov check summary sorted from the biggest count

## Usage
1. Install the dependencies
    ```
    pip install -r requirements.txt
    ```
2. Run the script
    ```
    python summarizer.py -d .
    ```

## Options
See `python summarizer --help`
| Name            | Description                                         | Note                                                       |
| --------------- | --------------------------------------------------- | ---------------------------------------------------------- |
| --directory, -d | Target directory to check, can use multiple options | e.g. `.. -d <dir1> -d <dir2> ..`                           |
| --base-dir      | Base directory                                      |                                                            |
| --format        | Output format                                       | Current supported format: `text`, `json`                   |

## Next Development
- [ ] Print with tiered directory
- [ ] Custom output target
- [x] Integration with github action
