from file_operations import read_rocket_data, read_planetary_data, read_solar_system_data
from calculations import compute_stage_two_data, compute_travel_parameters, compute_angular_positions, compute_optimal_transfer_window, compute_dynamic_transfer_window, compute_rocket_trajectory
from display import display_stage_two_results, display_travel_parameters, display_angular_positions, display_stage_five_results, display_stage_six_results
import io
import sys

def capture_output(func, *args):
    """Capture print output as a string for GUI display."""
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    func(*args)
    sys.stdout = old_stdout
    return buffer.getvalue()

def run_stage_two(planet_data, a):
    """Compute and return Stage Two results as a string."""
    stage_two_results = compute_stage_two_data(planet_data, a)
    return capture_output(display_stage_two_results, stage_two_results)

def run_stage_three(start, dest, planet_data, orbit_data, a):
    """Compute and return Stage Three travel parameters as a string."""
    params = compute_travel_parameters(start, dest, planet_data, orbit_data, a)
    return capture_output(display_travel_parameters, params)

def run_stage_four(orbit_data, t_days):
    """Compute and return Stage Four angular positions as a string."""
    positions = compute_angular_positions(orbit_data, t_days)
    return capture_output(display_angular_positions, positions, t_days)

def run_stage_five(start, dest, planet_data, orbit_data, a):
    """Compute and return Stage Five optimal transfer window as a string."""
    t_optimal_days, params = compute_optimal_transfer_window(start, dest, planet_data, orbit_data, a)
    return capture_output(display_stage_five_results, start, dest, t_optimal_days, params, orbit_data)

def run_stage_six(start, dest, planet_data, orbit_data, a):
    """Compute and return Stage Six dynamic transfer window and trajectory data."""
    t_optimal_days, params = compute_dynamic_transfer_window(start, dest, planet_data, orbit_data, a)
    text_output = capture_output(display_stage_six_results, start, dest, t_optimal_days, params, orbit_data)
    if t_optimal_days is None:
        return text_output, None, None, None, None
    trajectory, all_positions, t_start, t_end = compute_rocket_trajectory(start, dest, planet_data, orbit_data, a, t_optimal_days)
    return text_output, trajectory, all_positions, t_start, t_end

if __name__ == "__main__":
    print("This module is intended to be imported by gui.py. Please run gui.py to launch the application.")