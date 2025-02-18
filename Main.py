
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.Agents import Cardiologist, Psychologist, Pulmonologist, MultidisciplinaryTeam
import json, os

# Load API key from a dotenv file
load_dotenv(dotenv_path='.env')

# Function to process the medical report
def process_medical_report():
    # Get the selected file path
    file_path = file_var.get()
    if not file_path:
        messagebox.showerror("Error", "Please select a medical report file.")
        return

    try:
        # Read the medical report
        with open(file_path, "r") as file:
            medical_report = file.read()

        # Initialize agents
        agents = {
            "Cardiologist": Cardiologist(medical_report),
            "Psychologist": Psychologist(medical_report),
            "Pulmonologist": Pulmonologist(medical_report)
        }

        # Run agents concurrently
        responses = {}
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(get_response, name, agent): name for name, agent in agents.items()}
            
            for future in as_completed(futures):
                agent_name, response = future.result()
                responses[agent_name] = response

        # Generate final diagnosis
        team_agent = MultidisciplinaryTeam(
            cardiologist_report=responses["Cardiologist"],
            psychologist_report=responses["Psychologist"],
            pulmonologist_report=responses["Pulmonologist"]
        )
        final_diagnosis = team_agent.run()

        # Display the final diagnosis in the text area
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "### Final Diagnosis:\n\n" + final_diagnosis)

        # Save the final diagnosis to a file
        txt_output_path = "results/final_diagnosis.txt"
        os.makedirs(os.path.dirname(txt_output_path), exist_ok=True)
        with open(txt_output_path, "w") as txt_file:
            txt_file.write("### Final Diagnosis:\n\n" + final_diagnosis)

        messagebox.showinfo("Success", f"Final diagnosis has been saved to {txt_output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to get agent response
def get_response(agent_name, agent):
    response = agent.run()
    return agent_name, response

# Function to open file dialog and select a medical report
def browse_file():
    file_path = filedialog.askopenfilename(
        title="Select Medical Report",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )
    if file_path:
        file_var.set(file_path)

# Create the main application window
root = tk.Tk()
root.title("Medical Diagnosis Application")
root.geometry("800x600")

# File selection frame
file_frame = tk.Frame(root)
file_frame.pack(pady=10)

tk.Label(file_frame, text="Medical Report:").pack(side=tk.LEFT, padx=5)
file_var = tk.StringVar()
tk.Entry(file_frame, textvariable=file_var, width=50).pack(side=tk.LEFT, padx=5)
tk.Button(file_frame, text="Browse", command=browse_file).pack(side=tk.LEFT, padx=5)

# Process button
process_button = tk.Button(root, text="Process Report", command=process_medical_report, width=20, height=2)
process_button.pack(pady=20)

# Output text area
output_label = tk.Label(root, text="Final Diagnosis:")
output_label.pack(pady=5)

output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=20)
output_text.pack(padx=10, pady=5)

# Run the application
root.mainloop()
