# Grade_Calaculator 
Grade Calculator is a lightweight, Python-based web application designed for students to efficiently manage and estimate grade distributions across multiple terms and courses. It features a high-impact visual interface and supports complex recursive grade structures (nested sub-categories).

🚀 Key Features
Initialization Modal: Upon startup, a frosted-glass dialog guides you to either import an existing CSV data file or start a fresh configuration.

Intuitive Card UI: Uses oversized fonts and responsive rectangular cards to display terms and courses for a premium visual experience.

Multi-level Grade Editor:

Supports infinite levels of "Sub-categories" (e.g., Assignments -> Quizzes -> Quiz 1).

Real-time Calculation: Automatically summarizes scores for each category based on child items and updates the course total instantly.

Flat Weighting Logic: Categories act strictly as organizational tools. All weights for scored items are set relative to the 100% course total, simplifying manual entries.

Data Persistence: Export your entire configuration to a standard CSV file for backup and re-import it whenever needed.

Wide Layout Optimization: Designed specifically for desktop browsers to provide a clean, distraction-free navigation experience.

🛠️ Tech Stack
Streamlit: For the interactive and fast-loading web frontend.

Pandas: For efficient data manipulation and CSV parsing.

CSS/HTML Injection: Custom styles for large card interactions, anchor-based positioning, and UI enhancements.

📦 Installation & Usage
1. Prerequisites
Ensure you have Python 3.8+ installed in your environment.

2. Install Dependencies
Run the following command in your terminal:

Bash

pip install streamlit pandas
3. Run the App
Navigate to the directory containing your file and run:

Bash

streamlit run your_filename.py
Replace your_filename.py with the actual name of your script.

📖 User Guide
Initialization: Choose to "Import previous CSV" or "Start from Scratch."

Manage Terms: Click the "📂" cards to enter a term or the "➕ Add Term" card to create a new one.

Course Navigation: View all courses within a specific term. Click a course card to open the detail editor.

Edit Grade Breakdown:

➕ Scored Item: Represents a specific assignment or exam.

📂 Sub-category: Create a folder to group similar items.

Weight (W): Enter the percentage this item contributes to the Course Total (100%).

Actual Score (G): Enter the score received (0-100).

Save & Export: Click the red "Save & Update Data" button at the bottom to commit changes, then use the sidebar to download a backup CSV.

📐 Data Structure
The exported CSV contains the following columns:

Semester: Name of the academic term.

Course: Name of the course.
   
Path: The hierarchical path (e.g., Assignments/Quizzes/Quiz1).

Weight: The item's percentage weight relative to the course total.

Grade: The actual score achieved for that item.

Tip: To maintain accuracy, ensure that the total weights of all items within a course or category add up to your intended distribution (usually 100%).

Happy GPA tracking!
