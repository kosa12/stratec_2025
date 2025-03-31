import tkinter as tk
from tkinter import ttk, messagebox
from main import run_stage_two, run_stage_three, run_stage_four, run_stage_five, run_stage_six
from constants import AU_TO_M

class PlanetaryTravelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Planetary Travel Calculator")
        self.root.geometry("1000x800")

        self.rocket_acc = None
        self.planet_data = {}
        self.orbit_data = {}
        self.load_data()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill="both")

        self.create_stage_two_tab()
        self.create_stage_three_tab()
        self.create_stage_four_tab()
        self.create_stage_five_tab()
        self.create_stage_six_tab()

    def load_data(self):
        from file_operations import read_rocket_data, read_planetary_data, read_solar_system_data
        self.rocket_acc = read_rocket_data("../Rocket_Data.txt")
        if self.rocket_acc is None:
            messagebox.showerror("Error", "Failed to load rocket data.")
            self.root.quit()
        self.planet_data = read_planetary_data("../Planetary_Data.txt")
        if not self.planet_data:
            messagebox.showerror("Error", "Failed to load planetary data.")
            self.root.quit()
        self.orbit_data = read_solar_system_data("../Solar_System_Data.txt")
        if not self.orbit_data:
            messagebox.showerror("Error", "Failed to load solar system data.")
            self.root.quit()

    def create_stage_two_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Stage Two - Escape Data")
        self.stage_two_text = tk.Text(tab, height=20, width=80)
        self.stage_two_text.pack(pady=10)
        run_button = ttk.Button(tab, text="Compute Escape Data", command=self.compute_stage_two)
        run_button.pack(pady=5)

    def create_stage_three_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Stage Three - Travel Parameters")
        ttk.Label(tab, text="Starting Planet:").pack(pady=5)
        self.start_planet_three = ttk.Combobox(tab, values=list(self.planet_data.keys()))
        self.start_planet_three.pack()
        ttk.Label(tab, text="Destination Planet:").pack(pady=5)
        self.dest_planet_three = ttk.Combobox(tab, values=list(self.planet_data.keys()))
        self.dest_planet_three.pack()
        self.stage_three_text = tk.Text(tab, height=15, width=80)
        self.stage_three_text.pack(pady=10)
        run_button = ttk.Button(tab, text="Compute Travel Parameters", command=self.compute_stage_three)
        run_button.pack(pady=5)

    def create_stage_four_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Stage Four - Angular Positions")
        ttk.Label(tab, text="Time (days):").pack(pady=5)
        self.time_four = ttk.Entry(tab)
        self.time_four.pack()
        self.stage_four_text = tk.Text(tab, height=15, width=80)
        self.stage_four_text.pack(pady=10)
        run_button = ttk.Button(tab, text="Compute Positions", command=self.compute_stage_four)
        run_button.pack(pady=5)

    def create_stage_five_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Stage Five - Optimal Transfer")
        ttk.Label(tab, text="Starting Planet:").pack(pady=5)
        self.start_planet_five = ttk.Combobox(tab, values=list(self.planet_data.keys()))
        self.start_planet_five.pack()
        ttk.Label(tab, text="Destination Planet:").pack(pady=5)
        self.dest_planet_five = ttk.Combobox(tab, values=list(self.planet_data.keys()))
        self.dest_planet_five.pack()
        self.stage_five_text = tk.Text(tab, height=15, width=80)
        self.stage_five_text.pack(pady=10)
        run_button = ttk.Button(tab, text="Compute Optimal Transfer", command=self.compute_stage_five)
        run_button.pack(pady=5)

    def create_stage_six_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Stage Six - Dynamic Transfer")

        input_frame = ttk.Frame(tab)
        input_frame.pack(pady=5)
        ttk.Label(input_frame, text="Starting Planet:").pack(pady=5)
        self.start_planet_six = ttk.Combobox(input_frame, values=list(self.planet_data.keys()))
        self.start_planet_six.pack()
        ttk.Label(input_frame, text="Destination Planet:").pack(pady=5)
        self.dest_planet_six = ttk.Combobox(input_frame, values=list(self.planet_data.keys()))
        self.dest_planet_six.pack()

        self.stage_six_text = tk.Text(tab, height=10, width=80)
        self.stage_six_text.pack(pady=5)

        self.canvas = tk.Canvas(tab, width=600, height=400, bg="black")
        self.canvas.pack(pady=10)

        button_frame = ttk.Frame(tab)
        button_frame.pack(pady=5)
        run_button = ttk.Button(button_frame, text="Compute Dynamic Transfer", command=self.compute_stage_six)
        run_button.pack(side=tk.LEFT, padx=5)
        self.start_button = ttk.Button(button_frame, text="Start Animation", command=self.start_animation, state="disabled")
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(button_frame, text="Stop Animation", command=self.stop_animation, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.trajectory = None
        self.all_positions = None
        self.t_start = None
        self.t_end = None
        self.anim_index = 0
        self.animation_running = False
        self.animation_id = None

    def compute_stage_two(self):
        self.stage_two_text.delete(1.0, tk.END)
        results = run_stage_two(self.planet_data, self.rocket_acc)
        self.stage_two_text.insert(tk.END, results)

    def compute_stage_three(self):
        start = self.start_planet_three.get().strip()
        dest = self.dest_planet_three.get().strip()
        if not start or not dest:
            messagebox.showerror("Error", "Please select both planets.")
            return
        if start not in self.planet_data or dest not in self.planet_data:
            messagebox.showerror("Error", f"Invalid planet(s). Choose from: {list(self.planet_data.keys())}")
            return
        self.stage_three_text.delete(1.0, tk.END)
        results = run_stage_three(start, dest, self.planet_data, self.orbit_data, self.rocket_acc)
        self.stage_three_text.insert(tk.END, results)

    def compute_stage_four(self):
        t_days_input = self.time_four.get().strip()
        try:
            t_days = float(t_days_input)
            if t_days < 0:
                messagebox.showerror("Error", "Time must be non-negative.")
                return
            self.stage_four_text.delete(1.0, tk.END)
            results = run_stage_four(self.orbit_data, t_days)
            self.stage_four_text.insert(tk.END, results)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of days.")

    def compute_stage_five(self):
        start = self.start_planet_five.get().strip()
        dest = self.dest_planet_five.get().strip()
        if not start or not dest:
            messagebox.showerror("Error", "Please select both planets.")
            return
        if start not in self.planet_data or dest not in self.planet_data:
            messagebox.showerror("Error", f"Invalid planet(s). Choose from: {list(self.planet_data.keys())}")
            return
        self.stage_five_text.delete(1.0, tk.END)
        results = run_stage_five(start, dest, self.planet_data, self.orbit_data, self.rocket_acc)
        self.stage_five_text.insert(tk.END, results)

    def compute_stage_six(self):
        start = self.start_planet_six.get().strip()
        dest = self.dest_planet_six.get().strip()
        if not start or not dest:
            messagebox.showerror("Error", "Please select both planets.")
            return
        if start not in self.planet_data or dest not in self.planet_data:
            messagebox.showerror("Error", f"Invalid planet(s). Choose from: {list(self.planet_data.keys())}")
            return
        self.stage_six_text.delete(1.0, tk.END)
        self.canvas.delete("all")
        text_output, trajectory, all_positions, t_start, t_end = run_stage_six(start, dest, self.planet_data, self.orbit_data, self.rocket_acc)
        self.stage_six_text.insert(tk.END, text_output)
        if trajectory is not None:
            self.trajectory = trajectory
            self.all_positions = all_positions
            self.t_start = t_start
            self.t_end = t_end
            self.anim_index = 0
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
        else:
            self.start_button.config(state="disabled")
            self.stop_button.config(state="disabled")

    def start_animation(self):
        if not self.trajectory or not self.all_positions or self.animation_running:
            return
        self.animation_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.animate_rocket()

    def stop_animation(self):
        if self.animation_running and self.animation_id is not None:
            self.root.after_cancel(self.animation_id)
            self.animation_running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

    def animate_rocket(self):
        if not self.animation_running:
            return

        self.canvas.delete("all")
        canvas_width = 600
        canvas_height = 400
        scale = canvas_width / (max([data[1] for data in self.orbit_data.values()]) * AU_TO_M * 2)

        self.canvas.create_oval(canvas_width/2-5, canvas_height/2-5, canvas_width/2+5, canvas_height/2+5, fill="yellow")

        if self.anim_index >= len(self.trajectory):
            self.anim_index = 0
        t, x_rocket, y_rocket = self.trajectory[self.anim_index]

        for planet, positions in self.all_positions.items():
            x_planet, y_planet = positions[self.anim_index]
            x = canvas_width/2 + x_planet * scale
            y = canvas_height/2 - y_planet * scale
            size = max(5, min(20, self.planet_data[planet][0] * scale * 1000 / AU_TO_M * 100))
            self.canvas.create_oval(x-size, y-size, x+size, y+size, fill="grey" if planet not in [self.start_planet_six.get(), self.dest_planet_six.get()] else "green" if planet == self.start_planet_six.get() else "red")
            self.canvas.create_text(x, y-size-10, text=planet, fill="white")

        x_r = canvas_width/2 + x_rocket * scale
        y_r = canvas_height/2 - y_rocket * scale
        self.canvas.create_oval(x_r-3, y_r-3, x_r+3, y_r+3, fill="white")
        self.canvas.create_text(x_r, y_r-15, text=f"t={t:.1f} days", fill="white")

        self.anim_index += 1
        self.animation_id = self.root.after(50, self.animate_rocket)

def main():
    root = tk.Tk()
    app = PlanetaryTravelGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()