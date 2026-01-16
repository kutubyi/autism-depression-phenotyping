import csv

response_mapping = {
    '全くない': 0,
    '少しだけ': 1,
    'ときどき': 2,
    'たいてい': 3,
    'いつも': 4
}

def calculate_k6_score(responses):
    total = 0
    
    for response in responses:
        response = response.strip()
        total += response_mapping[response]
        
    return total

def main():
    input_file = 'responses.csv'
    output_file = 'scores.csv'

    # Read responses CSV
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Skip header row
    header = rows[0]
    data_rows = rows[1:]

    # Prepare output data
    results = []
    results.append(['id', 'k6_score'])  

    # Process each participant
    for row in data_rows:
        participant_id = row[1]

        # Columns 5-10 
        k6_responses = row[5:11]

        # Calculate K6 score
        k6_score = calculate_k6_score(k6_responses)

        results.append([participant_id, k6_score])

    # Write output CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(results)

if __name__ == '__main__':
    main()
