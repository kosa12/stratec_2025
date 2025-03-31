from file_operations import read_rocket_data, read_planetary_data, read_solar_system_data
from calculations import compute_stage_two_data, compute_travel_parameters, compute_angular_positions, compute_optimal_transfer_window
from display import display_stage_two_results, display_travel_parameters, display_angular_positions, display_stage_five_results

def main():
    print("Planetary Travel Calculator - Stages Two, Three, Four, and Five")
    print("===============================================================")

    # Load data
    a = read_rocket_data("../Rocket_Data.txt")
    if a is None:
        return

    planet_data = read_planetary_data("../Planetary_Data.txt")
    if not planet_data:
        return

    orbit_data = read_solar_system_data("../Solar_System_Data.txt")
    if not orbit_data:
        return

    # Stage Two
    stage_two_results = compute_stage_two_data(planet_data, a)
    display_stage_two_results(stage_two_results)

    # Stage Three
    while True:
        start = input("\nEnter starting planet (or 'q' to quit): ").strip()
        if start.lower() == 'q':
            break
        dest = input("Enter destination planet: ").strip()
        if dest.lower() == 'q':
            break
        if start not in planet_data or dest not in planet_data or start not in orbit_data or dest not in orbit_data:
            print(">> Error: Invalid planet name(s).")
            print(">> Choose from:", list(planet_data.keys()))
            continue
        
        params = compute_travel_parameters(start, dest, planet_data, orbit_data, a)
        display_travel_parameters(params)

    # Stage Four
    while True:
        try:
            t_days_input = input("\nEnter time in days to compute planetary positions (or 'q' to quit): ").strip()
            if t_days_input.lower() == 'q':
                break
            t_days = float(t_days_input)
            if t_days < 0:
                print(">> Error: Time must be non-negative.")
                continue
            positions = compute_angular_positions(orbit_data, t_days)
            display_angular_positions(positions, t_days)
            break
        except ValueError:
            print(">> Error: Please enter a valid number of days.")

    # Stage Five
    while True:
        start = input("\nEnter starting planet for optimal transfer (or 'q' to quit): ").strip()
        if start.lower() == 'q':
            print("Goodbye!")
            break
        dest = input("Enter destination planet: ").strip()
        if dest.lower() == 'q':
            print("Goodbye!")
            break
        if start not in planet_data or dest not in planet_data or start not in orbit_data or dest not in orbit_data:
            print(">> Error: Invalid planet name(s).")
            print(">> Choose from:", list(planet_data.keys()))
            continue
        
        t_optimal_days, params = compute_optimal_transfer_window(start, dest, planet_data, orbit_data, a)
        display_stage_five_results(start, dest, t_optimal_days, params, orbit_data)
        break

if __name__ == "__main__":
    main()