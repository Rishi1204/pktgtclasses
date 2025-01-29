import csv
import json
from fuzzywuzzy import process

def extract_names_from_roster(file):
    """
    Given a CSV with roster data, this extracts all the names for actives, AMs, and senior status members.
    """
    names_list = []

    def combine_names(first_name, last_name):
        return f"{first_name} {last_name}"

    try:
        with open(file, mode='r', encoding='utf-8') as file:
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
        match, score = process.extractOne(name, name_list)
        if score >= 80:
            if score < 100:
                print(f"Replacing '{name}' with '{match}' (Score: {score})")
            return match
        if name not in name_list_set:
            unknown_names.add(name)
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
    
    return list(unknown_names)

def remove_names_from_takers(input_file, names_to_remove, output_file):
    try:
        # Read the input JSON file
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Normalize the names to remove (case-insensitive comparison)
        names_to_remove = set(name.lower() for name in names_to_remove)
        print(f"Names to remove: {names_to_remove}")

        # Process each course and remove names
        updated_data = []
        for course in data:
            # Remove names from Current_Takers and Past_Takers
            course['Current_Takers'] = [name for name in course['Current_Takers'] if name.lower() not in names_to_remove]
            course['Past_Takers'] = [name for name in course['Past_Takers'] if name.lower() not in names_to_remove]

            # Only keep the course if it still has takers
            if course['Current_Takers'] or course['Past_Takers']:
                updated_data.append(course)

        # Write the updated data to the output JSON file
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(updated_data, outfile, indent=2)

        print(f"Processed data has been saved to {output_file}")

    except Exception as e:
        print(f"Error processing the file: {e}")

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
            if score >= 80:
                if score < 85:
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

        # A helper function to check if a course exists and return the course entry, else None
        def find_course_in_json(course_name):
            for course in json_data:
                if course['Course_Name'] == course_name:
                    return course
            return None

        # Process each person's classes and update the JSON data
        for full_name, classes in person_classes.items():
            for class_name in classes:
                course_entry = find_course_in_json(class_name)

                if course_entry:
                    # If the course already exists, add to Current_Takers if the name isn't present
                    current_takers = course_entry.get('Current_Takers', [])
                    if full_name not in current_takers:
                        current_takers.append(full_name)
                    course_entry['Current_Takers'] = current_takers

                else:
                    # If the course does not exist, create a new course entry and add to JSON
                    new_course_entry = {
                        "Course_Name": class_name,
                        "Current_Takers": [full_name],
                        "Past_Takers": []
                    }
                    json_data.append(new_course_entry)

        # Write the updated JSON data to the output file
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            json.dump(json_data, output_file, indent=2)

        print(f"Data successfully written to {output_file_path}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    prev_sem = 'f24'
    curr_sem = 's25'
    roster_file = '../data/roster.csv'
    prev_sem_data = f"../data/class_data_{prev_sem}.json"
    prev_sem_replaced_name_data = '../data/real_names.json'
    final_output_json_file_path = '../data/final_output.json'
    classes_csv_file_path = '../data/responses.csv'
    new_semester_data = '../data/new_semester.json'
    added_classes_file_path = f"../data/class_data_{curr_sem}.json"

    full_names = extract_names_from_roster(roster_file)

    unknown_names = replace_names_with_fuzzy_matching(full_names, prev_sem_data, prev_sem_replaced_name_data)

    names_to_remove = unknown_names

    remove_names_from_takers(prev_sem_replaced_name_data, names_to_remove, final_output_json_file_path)

    move_current_to_past(final_output_json_file_path, new_semester_data)

    add_class_data_to_json(classes_csv_file_path, new_semester_data, added_classes_file_path, full_names)