# Daily Symptom Journal
> Logging and reporting symptoms

# Purpose
In dealing with chronic illness, it's incredibly helpful to have a clinical understanding of how your most prominent symptoms shift over time. This tool helps to track those symptoms and their severity, and provides the ability to export your data.

*Note: The implementation is slightly opinionated for my use case.*

## Set up
The only external requirement is `matplotlib`. This is only imported and utilized when using the plotting feature of `report.py`.

# Usage
## Logging
**Use this daily to log your symptoms (and daily notes).** Updates your JSON journal and archives it to store a backup. Previously logged symptoms will show up as options when logging, otherwise new ones can be added.

### Running
`$ python log.py`

### Options
- `-j`, `--journal`: Path to journal JSON file. Defaults to `journal.json`
- `-a`, `--archive`: Path to archive directory. Defaults to `journal_archive`
- `-n`, `--num-daily-symptoms`: Number of daily symptoms to log. Defaults to 5.

## Reporting
**Use this to generate reports from your journal.** Exports your journal data to a text file, and (optionally) stores a png graph with your symptom changes over time.

### Running
`$ python report.py`

### Options
- `-j`, `--journal`: Path to journal JSON file. Defaults to `journal.json`
- `-s`, `--start-date`: Start date for the report. Follows the format `mm-dd-yyyy`. Defaults to today.
- `-e`, `--end-date`: End date for the report. Follows the format `mm-dd-yyyy`. Defaults to a month ago.
- `-r`, `--reports`: Path to journal reports directory. Defaults to `reports`
- `-p`, `--plot`: Flag to enable the storing of a png plot of symptoms over time. Requires `matplotlib`.

# Journal Format
Currently the journal is stored as a JSON file. While this is not ideal, it will work for now (it's readable and portable). Eventually the size will become an issue, in which case an alternative data store will make more sense.

The journal is backed up every time you save a new entry.

Journal, archive, and reports are all gitignored - data is never sync'ed.

## Structure
```json

{
    "patient": "Patient name",
    "journal": [
        {
            date": "mm-dd-yyyy",
            "symptoms": [{
                "name": "Symptom name",
                "value": 5
            }],
            "note": "notable items from the day"
        }
    ]
}
```

