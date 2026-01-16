import csv

regular_mapping = {
    '1': 0,  # あてはまらない
    '2': 1,  # ときどきあてはまる
    '3': 2,  # たいていあてはまる
    '4': 3   # ほとんどいつもあてはまる
}

reverse_mapping = {
    '1': 3,  # あてはまらない
    '2': 2,  # ときどきあてはまる
    '3': 1,  # たいていあてはまる
    '4': 0   # ほとんどいつもあてはまる
}

reverse_items = {3, 7, 11, 12, 15, 17, 21, 22, 26, 32, 38, 40, 43, 45, 48}

regular_items = {1, 2, 4, 5, 6, 8, 9, 10, 13, 14, 16, 18, 19, 20, 23, 24, 25, 27, 28, 29,
                 30, 31, 33, 34, 35, 36, 37, 39, 41, 42, 44, 46, 47, 49, 50, 51, 52, 53,
                 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65}

def calculate_srs2_score(srs2_responses):
    total = 0

    for i, response in enumerate(srs2_responses):
        item_number = i + 1  # Items are numbered 1-65
        response = response.strip()

        if item_number in reverse_items:
            total += reverse_mapping[response]
        elif item_number in regular_items:
            total += regular_mapping[response]
    return total

def main():
    responses_file = 'responses_deduplicated.csv'
    scores_file = 'scores.csv'

    # Read responses CSV
    with open(responses_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        response_rows = list(reader)

    # Read scores CSV
    with open(scores_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        score_rows = list(reader)

    # Update header
    score_rows[0].append('srs2_score')

    # Process each participant
    for i in range(1, len(response_rows)):
        response_row = response_rows[i]
        participant_id = response_row[1]

        # Columns 11-75
        srs2_responses = response_row[11:76]
        srs2_score = calculate_srs2_score(srs2_responses)

        # Add SRS-2 score to scores
        if i < len(score_rows):
            score_rows[i].append(srs2_score)

    # Write updated scores CSV
    with open(scores_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(score_rows)

if __name__ == '__main__':
    main()
