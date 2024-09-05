#Created by AbdEl-Rhman Ashraf
#26/08/2024



import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import pyodbc
import re
from datetime import datetime, timedelta

class FlatCombobox(tk.Frame):
    def __init__(self, master, values, **kwargs):
        super().__init__(master, bg='white', highlightthickness=0, bd=0)
        self.values = values
        self.var = tk.StringVar()
        self.var.set("Choose course")
        
        self.label = tk.Label(self, textvariable=self.var, bg='white', fg='gray', anchor='w', font=("Arial", 14))
        self.label.pack(fill='x')
        
        self.arrow = tk.Label(self, text='▼', bg='white', fg='black')
        self.arrow.place(relx=1.0, rely=0, anchor='ne')
        
        self.underline = tk.Frame(self, bg='white', height=1)
        self.underline.pack(fill='x', side='bottom')
        
        self.dropdown_frame = tk.Frame(self.master, bg='white', highlightthickness=1, highlightbackground='black')
        self.listbox = tk.Listbox(self.dropdown_frame, bg='white', fg='black', highlightthickness=0, bd=0, font=("Arial", 14))
        self.listbox.pack(fill='both', expand=True)
        for item in self.values:
            self.listbox.insert('end', item)
        
        self.label.bind('<Button-1>', self.toggle_list)
        self.arrow.bind('<Button-1>', self.toggle_list)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.bind('<FocusIn>', self.on_focus_in)
        self.bind('<FocusOut>', self.on_focus_out)
        
    def toggle_list(self, event=None):
        if self.dropdown_frame.winfo_viewable():
            self.dropdown_frame.place_forget()
        else:
            width = self.winfo_width()
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
            self.dropdown_frame.place(x=x, y=y, width=width)
            self.listbox.focus_set()
            
    def on_select(self, event=None):
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            value = self.listbox.get(index)
            self.var.set(value)
            self.label.config(fg='black')
            self.dropdown_frame.place_forget()
    
    def on_focus_in(self, event=None):
        self.underline.config(bg='white')
    
    def on_focus_out(self, event=None):
        self.underline.config(bg='black')
        self.dropdown_frame.place_forget()
        if self.var.get() == "Choose course":
            self.label.config(fg='gray')

    def get(self):
        return self.var.get()
    
class ExamApp:
    def __init__(self, master):
        self.master = master
        self.master.title("ITI Exam App")
        self.master.attributes('-fullscreen', True)
        self.master.bind("<Escape>", self.end_fullscreen)

        self.answers = {}
        self.question_widgets = []
        self.exam_start_time = None
        self.timer_label = None
        self.current_ssn = None
        self.current_course = None
        self.timer_running = False

        self.set_background_image()
        self.create_widgets()
        self.setup_keyboard_navigation()

    def end_fullscreen(self, event=None):
        self.master.attributes("-fullscreen", False)
        self.master.geometry("1280x720")
        self.master.bind("<F11>", self.toggle_fullscreen)

    def toggle_fullscreen(self, event=None):
        self.master.attributes("-fullscreen", not self.master.attributes('-fullscreen'))

    def set_background_image(self):
        image_path = r"C:\Users\elbre\Desktop\desktop application (Community).png"
        image = Image.open(image_path)

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        image = image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)

        self.bg_image = ImageTk.PhotoImage(image)

        self.bg_label = tk.Label(self.master, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def create_widgets(self):
        
        # SSN entry (frameless with placeholder)
        self.ssn_entry = tk.Entry(self.master, font=("Arial", 14), bd=0, relief=tk.FLAT, bg='white', fg='grey')
        self.ssn_entry.insert(0, "Enter SSN")
        self.ssn_entry.place(relx=0.68, rely=0.48, anchor="center", width=200)  # Adjust width as needed

        # Add a line under the entry to make it look like a material design input
        ssn_line = tk.Frame(self.master, bg='white', height=1)
        ssn_line.place(relx=0.68, rely=0.49, anchor="center", width=200)  # Adjust width to match the entry

        # Bind focus events to handle placeholder behavior
        self.ssn_entry.bind("<FocusIn>", self.on_ssn_entry_focus_in)
        self.ssn_entry.bind("<FocusOut>", self.on_ssn_entry_focus_out)
        
        # Course dropdown (completely flat with no box)
        self.course_dropdown = FlatCombobox(self.master, values=self.get_course_names())
        self.course_dropdown.place(relx=0.68, rely=0.64, anchor="center", width=200)  # Adjust width as needed

        # Start Exam button (floating and without background frame)
        start_button = tk.Button(self.master, text="Start Exam", command=self.generate_exam, font=("Arial", 16, "bold"), bg='#1f7d46', fg='white', activebackground='#45a049', relief=tk.FLAT, bd=0)
        start_button.place(relx=0.77, rely=0.8, anchor="center")

        # Create tooltips
        self.create_tooltip(self.ssn_entry, "Enter your 14-digit Social Security Number")
        self.create_tooltip(self.course_dropdown, "Select the course for your exam")
        self.create_tooltip(start_button, "Click to start the exam")

        # Add hover effect to the button
        start_button.bind("<Enter>", lambda e: e.widget.config(bg='#45a049'))
        start_button.bind("<Leave>", lambda e: e.widget.config(bg='#4CAF50'))
   
    # Add these new methods to your class
    def on_ssn_entry_focus_in(self, event):
        if self.ssn_entry.get() == "Enter SSN":
            self.ssn_entry.delete(0, tk.END)
            self.ssn_entry.config(fg='black')

    def on_ssn_entry_focus_out(self, event):
        if not self.ssn_entry.get():
            self.ssn_entry.insert(0, "Enter SSN")
            self.ssn_entry.config(fg='grey')
        
    def create_tooltip(self, widget, text):
        tooltip = tk.Label(self.master, text=text, background="#ffffff", relief="solid", borderwidth=1)
        tooltip.bind("<Enter>", lambda event: self.show_tooltip(event, tooltip))
        tooltip.bind("<Leave>", lambda event: tooltip.place_forget())
        widget.bind("<Enter>", lambda event: self.show_tooltip(event, tooltip))
        widget.bind("<Leave>", lambda event: tooltip.place_forget())

    def show_tooltip(self, event, tooltip):
        x = event.widget.winfo_rootx() + event.widget.winfo_width()
        y = event.widget.winfo_rooty() + event.widget.winfo_height() // 2
        tooltip.place(x=x, y=y, anchor="w")
      
    def setup_keyboard_navigation(self):
        self.master.bind("<Return>", lambda event: self.start_exam())
        self.master.bind("<Tab>", self.focus_next_widget)
        self.master.bind("<Shift-Tab>", self.focus_previous_widget)

    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def focus_previous_widget(self, event):
        event.widget.tk_focusPrev().focus()
        return "break"

    def get_db_connection(self):
        try:
            conn = pyodbc.connect(
                r'DRIVER={ODBC Driver 17 for SQL Server};'
                r'SERVER=MODARSH;'
                r'DATABASE=PowerBIGP;'
                r'Trusted_Connection=yes;'
            )
            return conn
        except pyodbc.Error as e:
            messagebox.showerror("Database Connection Error", f"Failed to connect to the database: {str(e)}")
            return None

    def get_course_names(self):
        try:
            conn = self.get_db_connection()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            cursor.execute("SELECT Course_Name FROM Course")
            courses = [row[0] for row in cursor.fetchall()]
            return courses
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch courses: {str(e)}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def validate_ssn(self, ssn):
        if re.match(r'^\d{14}$', ssn):
            return True
        else:
            messagebox.showwarning("Invalid SSN", "Please enter a valid 14-digit SSN.")
            return False

    def start_exam(self):
        ssn = self.ssn_entry.get().strip()
        course = self.course_dropdown.get()

        if not self.validate_ssn(ssn):
            return

        if not course:
            messagebox.showwarning("Missing Course", "Please select a course before starting the exam.")
            return

        self.current_ssn = ssn
        self.current_course = course
        self.exam_start_time = datetime.now()
        self.timer_running = True
        self.update_timer()

        self.generate_exam()

    def generate_exam(self):
        ssn = self.ssn_entry.get()
        course_name = self.course_dropdown.get()

        if not self.validate_ssn(ssn):
            return
        if not course_name:
            messagebox.showwarning("Input Error", "Please select a course.")
            return
        
        # Store the SSN and course name
        self.current_ssn = ssn
        self.current_course = course_name

        try:
            conn = self.get_db_connection()
            if conn is None:
                return
            
            cursor = conn.cursor()
            
            # Generate the exam
            cursor.execute("EXEC GenerateExamForStudent @Std_SSN=?, @CourseName=?", (ssn, course_name))
            conn.commit()  # Ensure the exam generation is committed to the database

            # Get the most recent Ex_ID for the given course and student
            cursor.execute("EXEC GetMostRecentExamID @CourseName=?, @Std_SSN=?", (course_name, ssn))
            exam_id_result = cursor.fetchone()
            
            if not exam_id_result:
                messagebox.showerror("Error", "You are not registered in this course.")
                return
            
            exam_id = exam_id_result[0]
            
            # Get exam questions
            cursor.execute("EXEC GetQuestionsByCourseName @Ex_ID=?", exam_id)
            exam_questions = cursor.fetchall()

            # Process the questions to ensure uniqueness
            unique_questions = {}
            for question in exam_questions:
                q_id = question[1]  # Assuming question[1] is the question ID
                if q_id not in unique_questions:
                    unique_questions[q_id] = question  # Store the unique question

            # Convert the dictionary back to a list
            exam_questions = list(unique_questions.values())

            if not exam_questions:
                messagebox.showwarning("Exam Error", "No questions generated for this exam.")
                return

            # Check if the first row is an error message
            if len(exam_questions) == 1 and len(exam_questions[0]) == 1 and isinstance(exam_questions[0][0], str):
                messagebox.showerror("Error", exam_questions[0][0])
                return
        
            self.create_exam_interface(exam_questions, cursor)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate exam: {str(e)}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    def create_exam_interface(self, exam_questions, cursor):
        # Clear existing widgets
        for widget in self.master.winfo_children():
            widget.destroy()

        # Recreate the background
        self.set_background_image()

        # Create a semi-transparent overlay
        overlay = tk.Canvas(self.master, bg='white', bd=0, highlightthickness=0)
        overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        overlay.create_rectangle(0, 0, overlay.winfo_reqwidth(), overlay.winfo_reqheight())

        # Create a frame for the exam content
        exam_frame = tk.Frame(overlay, bg='white')
        exam_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)

        # Add a canvas with scrollbar for questions
        canvas = tk.Canvas(exam_frame, bg='white')
        scrollbar = ttk.Scrollbar(exam_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.question_widgets = []
        for idx, question in enumerate(exam_questions, start=1):
            self.create_question_widget(scrollable_frame, idx, question, cursor)

        submit_button = tk.Button(exam_frame, text="Submit", command=self.submit_exam,
                                font=("Helvetica", 14, "bold"), bg='#4CAF50', fg='white', 
                                activebackground='#45a049', padx=20, pady=10, bd=0)
        submit_button.pack(side=tk.BOTTOM, pady=20)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create timer label
        self.timer_label = tk.Label(exam_frame, text="", font=("Helvetica", 16), bg='white', fg='#333333')
        self.timer_label.pack(side=tk.TOP, pady=10)

        # Start the timer
        self.exam_start_time = datetime.now()
        self.update_timer()

    def update_timer(self):
        if self.exam_start_time:
            elapsed_time = datetime.now() - self.exam_start_time
            remaining_time = timedelta(hours=1) - elapsed_time
            if remaining_time.total_seconds() <= 0:
                self.submit_exam()
            else:
                minutes, seconds = divmod(remaining_time.seconds, 60)
                self.timer_label.config(text=f"Time remaining: {minutes:02d}:{seconds:02d}")
                self.master.after(1000, self.update_timer)

    def create_question_widget(self, parent, idx, question, cursor):
        question_frame = tk.Frame(parent, bg='#F5F7F8', bd=2, relief=tk.GROOVE)
        question_frame.pack(fill="x", padx=10, pady=10)

        question_label = tk.Label(question_frame, text=f"Q{idx}: {question[2]}", 
                                  font=("Helvetica", 12, "bold"), bg='#F5F7F8', fg='#333333',
                                  anchor="w", wraplength=700, justify=tk.LEFT)
        question_label.pack(fill="x", padx=10, pady=10)

        widget = self.create_mcq_widget(question_frame, question, cursor)
        widget.pack(fill="x", padx=10, pady=10)
        self.question_widgets.append(widget)
        return widget

    def create_mcq_widget(self, parent, question, cursor):
        answer_var = tk.StringVar(value="")
        cursor.execute("GetChoices @Q_ID = ?", (question[1],))
        choices = cursor.fetchall()
        
        frame = tk.Frame(parent, bg='#F5F7F8')
        frame.pack(fill="x")
        
        for choice in choices:
            choice_rb = tk.Radiobutton(frame, text=choice[0], variable=answer_var, value=choice[0],
                                       font=("Helvetica", 11), bg='#F5F7F8', anchor="w", wraplength=650)
            choice_rb.pack(fill="x", padx=40, pady=2)

        self.answers[question[1]] = answer_var
        return frame

    def submit_exam(self):
        print("Submit button clicked")  # Debug print
        
        if not messagebox.askyesno("Confirm Submission", "Are you sure you want to submit your exam?"):
            print("Submission cancelled by user")  # Debug print
            return

        print("User confirmed submission")  # Debug print
        print(f"SSN: {self.current_ssn}, Course: {self.current_course}")  # Debug print
        print(f"Answers: {self.answers}")  # Debug print

        try:
            conn = self.get_db_connection()
            if conn is None:
                print("Failed to establish database connection")  # Debug print
                return
            
            cursor = conn.cursor()

            # Get the most recent Ex_ID for the given course
            cursor.execute("""
                SELECT TOP 1 e.Ex_ID 
                FROM Exam e
                JOIN Course c ON e.Crs_ID = c.Crs_ID
                WHERE c.Course_Name = ?
                ORDER BY e.Ex_ID DESC
            """, self.current_course)
            exam_id_result = cursor.fetchone()
            
            if not exam_id_result:
                messagebox.showerror("Error", "Could not find the exam ID.")
                return
            
            exam_id = exam_id_result[0]
            print(f"Retrieved Exam ID: {exam_id}")  # Debug print

            for q_id, answer_var in self.answers.items():
                answer = answer_var.get() if answer_var.get() else ""
                print(f"Submitting answer: SSN={self.current_ssn}, Ex_ID={exam_id}, Q_ID={q_id}, Answer={answer}")  # Debug print
                print(f"Executing: EXEC SubmitExamAnswers @Std_SSN={self.current_ssn}, @Ex_ID={exam_id}, @Q_ID={q_id}, @Answers='{answer}'")  # Debug print
                cursor.execute("{CALL SubmitExamAnswers(?, ?, ?, ?)}", 
                            (int(self.current_ssn), int(exam_id), int(q_id), answer))
                conn.commit()
            
            messagebox.showinfo("Success", "Exam submitted successfully!")
            
            # Clear existing widgets and return to initial state
            for widget in self.master.winfo_children():
                widget.destroy()
            
            self.set_background_image()
            self.create_widgets()
            
            # Reset exam-related variables
            self.answers = {}
            self.question_widgets = []
            self.exam_start_time = None
            self.timer_label = None
            self.current_ssn = None
            self.current_course = None

        except pyodbc.Error as e:
            error_message = f"Database error: {str(e)}"
            messagebox.showerror("Error", error_message)
            print(f"Database error details: {error_message}")  # Debug print
            
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            messagebox.showerror("Error", error_message)
            print(f"Exception details: {error_message}")  # Debug print
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            print("Database connection closed")  # Debug print

if __name__ == "__main__":
    print("Starting Exam App...")  # Debug print
    root = tk.Tk()
    app = ExamApp(root)
    root.mainloop()
    
    ## to make the app an exe file:
    ## 1. pip install auto-py-to-exe
    ## 2. auto-py-to-exe
    ## 3. select the main.py file
    ## 4. select the output folder
    ## 5. select the icon (optional)
    ## 6. click convert exe
    ## 7. wait for the process to finish
    ## 8. the exe file will be in the output folder
    
    
    
