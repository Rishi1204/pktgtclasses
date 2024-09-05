const fs = require('fs');

// Your existing helper function to clean and split names
const splitAndCleanNames = (names) => {
  return names
    .split(',')
    .map(name => name.trim())  // Remove extra spaces
    .filter(name => name !== "");  // Remove empty strings
};

// Your logic to reorganize the data
const reorganizeData = (data) => {
  return data.reduce((acc, curr) => {
    const existingCourse = acc.find(item => item.Course_Name === curr.Course_Name);

    const currentTakersList = splitAndCleanNames(curr.Current_Takers);
    const pastTakersList = splitAndCleanNames(curr.Past_Takers);

    if (existingCourse) {
      // Merge the current and past takers if the course already exists
      existingCourse.Current_Takers = [...new Set([...existingCourse.Current_Takers, ...currentTakersList])];
      existingCourse.Past_Takers = [...new Set([...existingCourse.Past_Takers, ...pastTakersList])];
    } else {
      // Add a new course entry
      acc.push({
        Course_Name: curr.Course_Name,
        Current_Takers: currentTakersList,
        Past_Takers: pastTakersList,
      });
    }

    return acc;
  }, []);
};

// Parent function to read, process, and write the data
const processJsonFile = (inputFilePath, outputFilePath) => {
  try {
    // Read the input JSON file
    const rawData = fs.readFileSync(inputFilePath, 'utf-8');
    const data = JSON.parse(rawData);

    // Process the data
    const processedData = reorganizeData(data);

    // Write the processed data to a new JSON file
    fs.writeFileSync(outputFilePath, JSON.stringify(processedData, null, 2), 'utf-8');
    console.log(`Processed data has been saved to ${outputFilePath}`);
  } catch (error) {
    console.error("Error processing the JSON file:", error);
  }
};

// Call the function with your file paths
const inputFilePath = 'src/New_Scholastics_F23.json';  // Replace with your input file path
const outputFilePath = 'src/Cleaned_Data.json';  // Replace with your desired output file path
processJsonFile(inputFilePath, outputFilePath);