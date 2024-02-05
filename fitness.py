import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import mysql.connector
from PIL import Image, ImageTk
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

mysql_host="localhost"
mysql_user="root"
mysql_password="yourpassword"
mysql_database="login"

conn = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database
)
c = conn.cursor()
current_username = None

window_width=600
window_height=400

large_font = ("Helvetica", 14)
bold_large_font = ("Helvetica", 16, "bold")

def login(username):
    global current_username
    current_username=username

    c.execute("SELECT * FROM user_credentials WHERE username=%s", (username,))
    user_data=c.fetchone()

    if user_data:
        if user_data[1]==entry_password.get():
            messagebox.showinfo("Success", f"Login successful. Welcome, {username}!")

            c.execute("SELECT * FROM user_profiles WHERE username=%s", (username,))
            profile_data = c.fetchone()

            if not profile_data:
                create_profile(username)
            else:
                show_profile_details(username)
        else:
            messagebox.showerror("Error", "Incorrect password. Please try again.")
    else:
        messagebox.showerror("Error", "Username not found. Please register.")

def create_user():
    username = entry_username.get()
    password = entry_password.get()

    c.execute("SELECT * FROM user_credentials WHERE username=%s", (username,))
    existing_user = c.fetchone()

    if existing_user:
        messagebox.showerror("Error", "Username already exists. Choose a different one.")
    else:
        c.execute("INSERT INTO user_credentials (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful. You can now log in.")
        show_login_window()
        

def show_login_window():
    root.deiconify()
    root.update()

def on_close(profile_creator_window):
    root.deiconify()
    profile_creator_window.destroy()
def on_close_graph(root_graph, canvas, fig):
    root_graph.destroy()
    canvas.get_tk_widget().destroy()
    plt.close(fig)

def calculate_bmi(weight, height):
    """
    Calculate BMI (Body Mass Index) using weight (in kg) and height (in meters).
    Formula: BMI = weight / (height * height)
    """
    if height == 0:
        return 0
    return weight / (height * height)

def show_profile_details(username):
    c.execute("SELECT * FROM user_profiles WHERE username=%s", (username,))
    profile_data = c.fetchone()

    if not profile_data:
        create_profile(username)
    else:
        profile_details_window = tk.Toplevel(root)
        profile_details_window.title("Profile Details")

        profile_details_window.geometry(f"{window_width}x{window_height}")
        profile_details_window.resizable(width=False, height=False)

        bg_image_profile = tk.PhotoImage(file=r"C:\Users\finugalu\Desktop\fitness tracker\of-fitness-equipment-and-personal-grooming-tools-on-a-clean-background-with-copy-space-free-photo.png")
        bg_label_profile = tk.Label(profile_details_window, image=bg_image_profile)
        bg_label_profile.image = bg_image_profile
        bg_label_profile.place(relwidth=1, relheight=1)

        title_label = tk.Label(profile_details_window, text="Profile Details", font=bold_large_font, pady=10)
        title_label.pack()

        details_text = f"Name: {profile_data[2]}\nAge: {profile_data[3]}\nWeight: {profile_data[4]}\nHeight: {profile_data[5]}\nGender: {profile_data[6]}"

        weight = float(profile_data[4])
        height = float(profile_data[5]) / 100.0 
        bmi = calculate_bmi(weight, height)
        details_text += f"\nBMI: {bmi:.2f}"

        details_frame = tk.Frame(profile_details_window, bg="black", bd=10)
        details_frame.pack()

        details_label = tk.Label(details_frame, text=details_text, font=large_font, padx=10, pady=10, bg="black", fg="white")
        details_label.pack()

        btn_workout = tk.Button(details_frame, text="Workout", font=large_font, command=lambda: open_workout_page(username))
        btn_workout.pack(side="left", padx=10, pady=10)

        btn_activity = tk.Button(details_frame, text="Activity", font=large_font, command=lambda: open_activity_page(username))
        btn_activity.pack(side="left", padx=10, pady=10)

        btn_weight_gain = tk.Button(details_frame, text="Weight Gain", font=large_font, command=lambda: open_weight_gain_window(username))
        btn_weight_gain.pack(side="left", padx=10, pady=10)



class ProfileCreator:
    def __init__(self, master, username):
        self.master = master
        master.title("Profile Creator")
        master.geometry(f"{window_width}x{window_height}")
        self.create_button("Create Profile", lambda: self.create_profile(username), row=6)
        master.protocol("WM_DELETE_WINDOW", lambda: on_close(master))

def open_workout_page(username):
    workout_page = tk.Toplevel(root)
    workout_page.title("Workout Page")
    workout_page.geometry(f"{window_width}x{window_height}")
    
    bg_image_profile = tk.PhotoImage(file=r"C:\Users\finugalu\Desktop\fitness tracker\of-fitness-equipment-and-personal-grooming-tools-on-a-clean-background-with-copy-space-free-photo.png")  # Replace with your image file path
    bg_label_profile = tk.Label(workout_page, image=bg_image_profile)
    bg_label_profile.image = bg_image_profile
    bg_label_profile.place(relwidth=1, relheight=1)

    exercises = ["Running", "Cycling", "Walking", "Swimming", "Weightlifting"]
    exercise_var = tk.StringVar(value=exercises[0])

    tk.Label(workout_page, text="Select Exercise:", font=large_font).grid(row=0, column=0, padx=10, pady=10)
    exercise_menu = tk.OptionMenu(workout_page, exercise_var, *exercises)
    exercise_menu.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(workout_page, text="Time Spent (minutes):", font=large_font).grid(row=1, column=0, padx=10, pady=10)
    time_entry = tk.Entry(workout_page, font=large_font)
    time_entry.grid(row=1, column=1, padx=10, pady=10)

    def calculate_calories():
        try:
            time_spent = float(time_entry.get())

            c.execute("SELECT gender FROM user_profiles WHERE username=%s", (username,))
            user_gender = c.fetchone()[0]

            if user_gender == "Male":
                if exercise_var.get() == "Running":
                    calories_burned = time_spent * 11.4  
                elif exercise_var.get() == "Cycling":
                    calories_burned = time_spent * 7.5  
                elif exercise_var.get() == "Walking":
                    calories_burned = time_spent * 8.3  
                elif exercise_var.get() == "Swimming":
                    calories_burned = time_spent * 9.05
                elif exercise_var.get() == "Weightlifting":
                    calories_burned = time_spent * 3.6
                else:
                    calories_burned = time_spent * 10
            elif user_gender == "Female":
                if exercise_var.get() == "Running":
                    calories_burned = time_spent * 10.4 
                elif exercise_var.get() == "Cycling":
                    calories_burned = time_spent * 6.5
                elif exercise_var.get() == "Walking":
                    calories_burned = time_spent * 7.3
                elif exercise_var.get() == "Swimming":
                    calories_burned = time_spent * 8.05
                elif exercise_var.get() == "Weightlifting":
                    calories_burned = time_spent * 2.56
                else:
                    calories_burned = time_spent * 9
            messagebox.showinfo("Calories Burned", f"You burned approximately {calories_burned:.2f} calories.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid numeric value for time spent.")

    calculate_btn = tk.Button(workout_page, text="Calculate Calories", font=large_font, command=calculate_calories)
    calculate_btn.grid(row=2, columnspan=2, pady=10)

def open_activity_page(username):
    activity_page = tk.Toplevel(root)
    activity_page.title("Activity Page")

    activity_page.geometry(f"{window_width}x{window_height}")

    bg_image_activity = tk.PhotoImage(file=r"C:\Users\finugalu\Desktop\fitness tracker\of-fitness-equipment-and-personal-grooming-tools-on-a-clean-background-with-copy-space-free-photo.png")  # Replace with your image file path
    bg_label_activity = tk.Label(activity_page, image=bg_image_activity)
    bg_label_activity.image = bg_image_activity
    bg_label_activity.place(relwidth=1, relheight=1)

    btn_enter_manual_calories = tk.Button(activity_page, text="Enter Manual Calories", font=large_font,
                                          command=lambda: enter_manual_calories(username))
    btn_enter_manual_calories.pack(pady=10)
    btn_plot_daily_calories = tk.Button(activity_page, text="Plot Daily Calories", font=large_font,
                                         command=lambda: plot_daily_calories(username))
    btn_plot_daily_calories.pack(pady=10)

def enter_manual_calories(username):
    today_date = datetime.now().strftime("%Y-%m-%d")
    manual_calories = simpledialog.askinteger("Enter Calories", f"Enter calories burned for {today_date}:", minvalue=0)

    if manual_calories is not None:
        c.execute("INSERT INTO daily_manual_calories (username, date,calories_burned) VALUES (%s, %s, %s)",
                  (username, today_date, manual_calories))
        conn.commit()

        messagebox.showinfo("Manual Calories Entered", f"Manual calories entered for {today_date}. Calories: {manual_calories}")
        
def plot_daily_calories(username):
    c.execute("SELECT date, calories_burned FROM daily_manual_calories WHERE username=%s", (username,))
    data = c.fetchall()

    if not data:
        messagebox.showinfo("No Data", "No manual calorie data available.")
        return

    dates = [entry[0] for entry in data]
    manual_calories = [entry[1] for entry in data]

    fig, ax = plt.subplots()
    ax.plot(dates, manual_calories, marker='o', linestyle='-')
    ax.set(xlabel='Date', ylabel='Calories Burned',
           title='Daily Calories Burned')
    ax.grid()

    root_graph = tk.Toplevel(root)
    root_graph.title("Daily Manual Calories Graph")

    canvas = FigureCanvasTkAgg(fig, master=root_graph)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    toolbar = NavigationToolbar2Tk(canvas, root_graph)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    root_graph.protocol("WM_DELETE_WINDOW", lambda: on_close_graph(root_graph, canvas, fig))


    

def create_profile(username):
    profile_creator_window = tk.Toplevel(root)
    profile_creator_window.title("Profile Creator")
    profile_creator_window.geometry(f"{window_width}x{window_height}")
    profile_creator = ProfileCreator(profile_creator_window, username)
    root.withdraw()

    profile_creator_window.protocol("WM_DELETE_WINDOW", lambda: on_close(profile_creator_window))

class ProfileCreator:
    def __init__(self, master, username):
        self.master = master
        master.title("Profile Creator")
        master.geometry(f"{window_width}x{window_height}")
        self.create_label_entry("Name", row=0)
        self.create_label_entry("Age", row=1)
        self.create_label_entry("Weight", row=2)
        self.create_label_entry("Height", row=3)
        self.gender_var = tk.StringVar()
        self.gender_var.set("Male")
        self.create_label_option_menu("Gender", ["Male", "Female"], row=4)
        self.create_button("Create Profile", lambda: self.create_profile(username), row=6)

    def create_label_entry(self, label, row):
        tk.Label(self.master, text=f"{label}:", font=large_font).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        entry = tk.Entry(self.master, font=large_font)
        entry.grid(row=row, column=1, padx=10, pady=5)

    def create_label_option_menu(self, label, options, row):
        tk.Label(self.master, text=f"{label}:", font=large_font).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        option_menu = tk.OptionMenu(self.master, self.gender_var, *options)
        option_menu.grid(row=row, column=1, padx=10, pady=5)

    def create_label_button(self, label, command, row):
        tk.Label(self.master, text=f"{label}:", font=large_font).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        button = tk.Button(self.master, text="Upload", command=command, font=large_font)
        button.grid(row=row, column=1, padx=10, pady=5)

    def create_button(self, text, command, row):
        button = tk.Button(self.master, text=text, command=command, font=large_font)
        button.grid(row=row, column=0, columnspan=2, pady=10)

    def create_profile(self, username):
        name = self.get_entry_text(0)
        age = self.get_entry_text(1)
        weight = self.get_entry_text(2)
        height = self.get_entry_text(3)
        gender = self.gender_var.get()

        save_profile_to_database(username, name, age, weight, height, gender)
        self.master.destroy()
        root.deiconify()
        show_profile_details(username)

    def get_entry_text(self, index):
        return self.master.grid_slaves(row=index, column=1)[0].get()

def save_profile_to_database(username, name, age, weight, height, gender):
    c.execute("INSERT INTO user_profiles (username, name, age, weight, height, gender) VALUES (%s, %s, %s, %s, %s, %s)",
              (username, name, age, weight, height, gender))
    conn.commit()

def open_weight_gain_window(username):
    weight_gain_window = tk.Toplevel(root)
    weight_gain_window.title("Weight Gain Calculator")

    weight_gain_window.geometry(f"{window_width}x{window_height}")

    bg_image_profile = tk.PhotoImage(file=r"C:\Users\finugalu\Desktop\fitness tracker\of-fitness-equipment-and-personal-grooming-tools-on-a-clean-background-with-copy-space-free-photo.png")  # Replace with your image file path
    bg_label_profile = tk.Label(weight_gain_window, image=bg_image_profile)
    bg_label_profile.image = bg_image_profile
    bg_label_profile.place(relwidth=1, relheight=1)

    tk.Label(weight_gain_window, text="Weight Gain Calculator", font=bold_large_font, pady=10).pack()

    tk.Label(weight_gain_window, text="Current Weight (kg):", font=large_font).pack(pady=10)
    weight_entry = tk.Entry(weight_gain_window, font=large_font)
    weight_entry.pack(pady=10)

    tk.Label(weight_gain_window, text="Target Weight (kg):", font=large_font).pack(pady=10)
    target_weight_entry = tk.Entry(weight_gain_window, font=large_font)
    target_weight_entry.pack(pady=10)

    tk.Label(weight_gain_window, text="Target Time (days):", font=large_font).pack(pady=10)
    target_time_entry = tk.Entry(weight_gain_window, font=large_font)
    target_time_entry.pack(pady=10)

    calculate_calories_btn = tk.Button(weight_gain_window, text="Calculate Calories", font=large_font,
                                       command=lambda: calculate_calories_for_weight_gain(username, weight_entry.get(), target_weight_entry.get(), target_time_entry.get()))
    calculate_calories_btn.pack(pady=10)

def calculate_calories_for_weight_gain(username, current_weight, target_weight, target_time):
    try:
        current_weight = float(current_weight)
        target_weight = float(target_weight)
        target_time = float(target_time)

        if current_weight <= 0 or target_weight <= 0 or target_time <= 0:
            messagebox.showerror("Invalid Input", "Please enter valid positive values for weights and time.")
            return
        calorie_surplus = (target_weight - current_weight) * 7700 / target_time
        messagebox.showinfo("Calories for Weight Gain", f"To gain weight, you need to eat approximately {calorie_surplus:.2f} calories per day.")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numeric values for weights and time.")

root = tk.Tk()
root.title("Fitness Tracker - Login")

bg_image = tk.PhotoImage(file=r"C:\Users\finugalu\Desktop\fitness tracker\fitness.png")
bg_label = tk.Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)

frame_login = tk.Frame(root)
frame_login.place(relx=0.5, rely=0.5, anchor="center")

label_username = tk.Label(frame_login, text="Username:", font=large_font)
label_username.grid(row=0, column=0, padx=15, pady=15)
entry_username = tk.Entry(frame_login, font=large_font, bd=2, relief="groove")
entry_username.grid(row=0, column=1, padx=15, pady=15)

label_password = tk.Label(frame_login, text="Password:", font=large_font)
label_password.grid(row=1, column=0, padx=15, pady=15)
entry_password = tk.Entry(frame_login, show="*", font=large_font, bd=2, relief="groove")
entry_password.grid(row=1, column=1, padx=15, pady=15)

btn_login = tk.Button(frame_login, text="Login", command=lambda: login(entry_username.get()), font=large_font)
btn_login.grid(row=2, columnspan=2, pady=15)

btn_register = tk.Button(frame_login, text="Register", command=create_user, font=large_font)
btn_register.grid(row=3, columnspan=2, pady=15)

try:
    root.geometry(f"{window_width}x{window_height}")
    root.resizable(width=False, height=False)
    root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
    root.mainloop()
except Exception as e:
    print("An error occurred:", e)
