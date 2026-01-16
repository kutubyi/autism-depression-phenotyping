import csv
from datetime import datetime

def parse_timestamp(timestamp_str):
    """Parse timestamp string to datetime object."""
    return datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S')

def main():
    input_file = 'responses.csv'
    output_file = 'responses_deduplicated.csv'

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    # Keep the latest entry for each participant
    participant_data = {}

    for row in rows:
        participant_id = row[1]
        timestamp = parse_timestamp(row[0])

        if participant_id not in participant_data:
            participant_data[participant_id] = (timestamp, row)
        else:
            existing_timestamp, _ = participant_data[participant_id]
            if timestamp > existing_timestamp:
                participant_data[participant_id] = (timestamp, row)

    # Extract deduplicated rows, sorted by participant ID
    deduplicated_rows = [row for _, row in participant_data.values()]
    deduplicated_rows.sort(key=lambda x: int(x[1]))

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(deduplicated_rows)

if __name__ == '__main__':
    main()
