from file_operations import read_rocket_data, read_planetary_data, read_solar_system_data
from calculations import compute_stage_two_data, compute_travel_parameters
from display import display_stage_two_results, display_travel_parameters

def main():
    print("Planetary Travel Calculator - Stages Two and Three")
    print("==================================================")

    a = read_rocket_data("../Rocket_Data.txt")
    if a is None:
        return

    planet_data = read_planetary_data("../Planetary_Data.txt")
    if not planet_data:
        return

    orbit_data = read_solar_system_data("../Solar_System_Data.txt")
    if not orbit_data:
        return

    stage_two_results = compute_stage_two_data(planet_data, a)
    display_stage_two_results(stage_two_results)


    while True:
        start = input("\nEnter starting planet (or 'q' to quit): ").strip()
        if start.lower() == 'q':
            print("Goodbye!")
            break
        dest = input("Enter destination planet: ").strip()
        if dest.lower() == 'q':
            print("Goodbye!")
            break
        if start not in planet_data or dest not in planet_data or start not in orbit_data or dest not in orbit_data:
            print(">> Error: Invalid planet name(s). \n>> Choose from:", list(planet_data.keys()))
            continue
        
        params = compute_travel_parameters(start, dest, planet_data, orbit_data, a)
        display_travel_parameters(params)

if __name__ == "__main__":
    main()