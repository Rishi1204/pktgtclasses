import csv
import json
from fuzzywuzzy import process

def extract_names_from_csv(file_path):
    names_list = []

    def combine_names(first_name, last_name):
        return f"{first_name} {last_name}"

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                first_name = row['First Name']
                last_name = row['Last Name']
                status = row['Status']

                # Check if status is 'Active', 'AM', or 'Senior Status'
                if status in ['Active', 'AM', 'Senior Status']:
                    full_name = combine_names(first_name, last_name)
                    names_list.append(full_name)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return []

    return names_list

def replace_names_with_fuzzy_matching(name_list, input_file_path, output_file_path):
    try:
        with open(input_file_path, mode='r', encoding='utf-8') as input_file:
            json_data = json.load(input_file)
    except Exception as e:
        print(f"Error reading the input file: {e}")
        return

    name_list_set = set(name_list)

    unknown_names = set()

    def replace_with_fuzzy_match(name, name_list):
        if name not in name_list_set:
            unknown_names.add(name)
        match, score = process.extractOne(name, name_list)
        if score >= 75:
            if score < 80:
                print(f"Replacing '{name}' with '{match}' (Score: {score})")
            return match
        return name
    

    for course in json_data:
        if course.get('Current_Takers'):
            course['Current_Takers'] = [replace_with_fuzzy_match(name, name_list) for name in course['Current_Takers']]

        if course.get('Past_Takers'):
            course['Past_Takers'] = [replace_with_fuzzy_match(name, name_list) for name in course['Past_Takers']]


    print(f"Unknown names: {unknown_names}")
    try:
        with open(output_file_path, mode='w', encoding='utf-8') as output_file:
            json.dump(json_data, output_file, indent=2)
        print(f"Results have been written to {output_file_path}")
    except Exception as e:
        print(f"Error writing the output file: {e}")

# Function to remove specified names from Current_Takers and Past_Takers
def remove_names_from_takers(input_file, names_to_remove, output_file):
    try:
        # Read the input JSON file
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Normalize the names to remove (case-insensitive comparison)
        names_to_remove = set(name.lower() for name in names_to_remove)

        # Process each course in the JSON data
        for course in data:
            # Remove names from Current_Takers
            course['Current_Takers'] = [name for name in course['Current_Takers'] if name.lower() not in names_to_remove]

            # Remove names from Past_Takers
            course['Past_Takers'] = [name for name in course['Past_Takers'] if name.lower() not in names_to_remove]

            if not course['Current_Takers'] and not course['Past_Takers']:
                data.remove(course)

        # Write the updated data to the output JSON file
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, indent=2)

        print(f"Processed data has been saved to {output_file}")

    except Exception as e:
        print(f"Error: {e}")

def move_current_to_past(input_file_path, output_file_path):
    try:
        # Read the input JSON file
        with open(input_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Process each course in the JSON data
        for course in data:
            current_takers = set(course.get('Current_Takers', []))  # Convert to set to avoid duplicates
            past_takers = set(course.get('Past_Takers', []))  # Convert to set to avoid duplicates

            # Add all current takers to past takers and remove duplicates
            course['Past_Takers'] = list(past_takers.union(current_takers))

            # Clear the current takers list
            course['Current_Takers'] = []

        # Write the updated data to the output JSON file
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, indent=2)

        print(f"Processed data has been saved to {output_file_path}")

    except Exception as e:
        print(f"Error: {e}")


def add_class_data_to_json(csv_file_path, json_file_path, output_file_path, name_list):
    try:
        # Read the existing JSON file
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)

        # Create a dictionary to store the names and their classes from the CSV
        person_classes = {}

        def replace_with_fuzzy_match(name, name_list):
            match, score = process.extractOne(name, name_list)
            if score >= 75:
                if score < 80:
                    print(f"Replacing '{name}' with '{match}' (Score: {score})")
                return match
            return name

        # Read the CSV file
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                full_name = row['Full Name']
                full_name = replace_with_fuzzy_match(full_name, name_list)
                class_info = row['Classes'].strip().split("\n")

                if full_name not in person_classes:
                    person_classes[full_name] = []

                person_classes[full_name].extend(class_info)

        # Process each course in the JSON data
        for course in json_data:
            current_takers = course.get('Current_Takers', [])
            past_takers = course.get('Past_Takers', [])

            # Update Current_Takers and Past_Takers based on the class names in the CSV
            for full_name, classes in person_classes.items():
                if any(course_name in classes for course_name in [course['Course_Name']]):
                    if full_name not in current_takers:
                        current_takers.append(full_name)

            course['Current_Takers'] = current_takers
            course['Past_Takers'] = past_takers  # Modify this if you want to update past takers too

        # Write the updated JSON data to the output file
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            json.dump(json_data, output_file, indent=2)

        print(f"Data successfully written to {output_file_path}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    csv_file_path = 'src/data/roster.csv'
    input_json_file_path = 'src/data/Cleaned_Data.json'
    output_json_file_path = 'src/data/real_names.json'
    final_output_json_file_path = 'src/data/final_output.json'
    classes_csv_file_path = 'src/data/responses.csv'
    new_semester_json_file_path = 'src/data/new_semester.json'
    added_classes_file_path = 'src/data/new_classes_added.json'

    full_names = extract_names_from_csv(csv_file_path)

    replace_names_with_fuzzy_matching(full_names, input_json_file_path, output_json_file_path)

    names_to_remove = ['Paul Barsa', 'Andrew Graffeo', 'Derrick Adams', 'Vince', 'Tejas Pradeep', 'Will Bunker', 'Ryan Sheppard', 'Ahmad', 'Jason Meng', 'David Lloyd George', 'Ethan Atkinson', 'Ethan FrAtkinson', 'Paden Davis']

    remove_names_from_takers(output_json_file_path, names_to_remove, final_output_json_file_path)

    move_current_to_past(final_output_json_file_path, new_semester_json_file_path)

    add_class_data_to_json(classes_csv_file_path, new_semester_json_file_path, added_classes_file_path, full_names)