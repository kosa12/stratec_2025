import math
import os
import re

G = 6.67e-11  # Grav const in m^3 kg^-1 s^-2
EARTH_MASS = 5.972e24  # Earth mass in kg
AU_TO_M = 149597870700  # meters per AU

def calculate_escape_velocity(mass_kg, radius_m):
    """Calculate escape velocity in m/s given mass in kg and radius in m."""
    return math.sqrt((2 * G * mass_kg) / radius_m)

def parse_mass(mass_str):
    """Parse mass string to kg, handling kg or Earth mass units."""
    mass_str = mass_str.strip()
    if 'kg' in mass_str:
        mass_str = mass_str.replace('kg', '').strip()
        if '*' in mass_str:
            base, exp_part = mass_str.split('*')
            base = float(base.strip())
            if '^' in exp_part:
                exp = float(exp_part.split('^')[1])
                return base * (10 ** exp)
            else:
                return base * float(exp_part)
        else:
            return float(mass_str)
    else:
        return float(mass_str.split()[0]) * EARTH_MASS

def read_rocket_data(file_path):
    """Read rocket data and return total acceleration in m/s^2."""
    if not os.path.exists(file_path):
        print(f">> Error: '{file_path}' not found!")
        return None

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            num_engines = int(lines[0].split(':')[1].strip())
            acc_per_engine = float(lines[1].split(':')[1].split()[0])  # "10 m/s^2" -> 10
            return num_engines * acc_per_engine
    except IOError as e:
        print(f">> Error: Unable to read '{file_path}': {str(e)}")
        return None

def read_planetary_data(file_path):
    """Read planetary data and return {planet: (radius_km, mass_kg, v_escape_m_s)}."""
    planet_data = {}
    if not os.path.exists(file_path):
        print(f">> Error: '{file_path}' not found!")
        return planet_data
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if not line.strip():
                    continue
                match = re.match(r'(\w+):\s*diameter\s*=\s*([\d.]+)\s*km,\s*mass\s*=\s*([^,]+)', line.strip())
                if match:
                    planet, diam_str, mass_str = match.groups()
                    radius_km = float(diam_str) / 2
                    radius_m = radius_km * 1000
                    mass_kg = parse_mass(mass_str)
                    v_escape_m_s = calculate_escape_velocity(mass_kg, radius_m)
                    planet_data[planet] = (radius_km, mass_kg, v_escape_m_s)
                else:
                    print(f">> Error: Invalid line in '{file_path}': {line.strip()}")
    except IOError as e:
        print(f">> Error: Unable to read '{file_path}': {str(e)}")
        return None
    return planet_data

def read_solar_system_data(file_path):
    """Read solar system data and return {planet: r_orbit_AU}."""
    orbit_data = {}
    if not os.path.exists(file_path):
        print(f">> Error: '{file_path}' not found!")
        return orbit_data
    
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if not line.strip():
                    continue
                match = re.match(r'(\w+):\s*period\s*=\s*[\d.]+\s*days,\s*orbital radius\s*=\s*([\d.]+)\s*AU', line.strip())
                if match:
                    planet, r_orbit_str = match.groups()
                    orbit_data[planet] = float(r_orbit_str)
    except IOError as e:
        print(f">> Error: Unable to read '{file_path}': {str(e)}")
        return None
    return orbit_data

def compute_stage_two_data(planet_data, a):
    """Compute Stage Two data: {planet: (v_escape_m_s, t_s, d_m)}."""
    results = {}
    for planet, (radius_km, mass_kg, v_escape_m_s) in planet_data.items():
        t_s = v_escape_m_s / a
        d_m = 0.5 * a * t_s**2
        results[planet] = (v_escape_m_s, t_s, d_m)
    return results

def display_stage_two_results(results):
    """Display Stage Two results in a formatted table."""
    print("\nPlanetary Escape Data:")
    print("-" * 70)
    print(f"{'Planet':<15} {'Escape Velocity (km/s)':>20} {'Time (s)':>15} {'Distance (km)':>15}")
    print("-" * 70)
    for planet in sorted(results):
        v_escape_m_s, t_s, d_m = results[planet]
        v_km_s = v_escape_m_s / 1000
        d_km = d_m / 1000
        print(f"{planet:<15} {v_km_s:>20.1f} {t_s:>15.1f} {d_km:>15.1f}")

def compute_travel_parameters(start, dest, planet_data, orbit_data, a):
    """Compute travel parameters from start to dest planet (Stage Three)."""
    # Orbital radii in meters
    r_orbit_start = orbit_data[start] * AU_TO_M
    r_orbit_dest = orbit_data[dest] * AU_TO_M
    D_m = abs(r_orbit_dest - r_orbit_start)

    # Planetary radii in meters
    r_start_m = planet_data[start][0] * 1000
    r_dest_m = planet_data[dest][0] * 1000

    # Cruising velocity (max escape velocity) in m/s
    v_cruise_m_s = max(planet_data[start][2], planet_data[dest][2])

    # Acceleration phase
    t_acc_s = v_cruise_m_s / a
    h_acc_m = 0.5 * a * t_acc_s**2

    # Deceleration phase (symmetric)
    t_dec_s = t_acc_s
    h_dec_m = h_acc_m

    # Cruising distance
    d_cruise_m = D_m - r_start_m - r_dest_m - h_acc_m - h_dec_m
    if d_cruise_m < 0:
        d_cruise_m = 0
    t_cruise_s = d_cruise_m / v_cruise_m_s

    # Total travel time
    t_total_s = t_acc_s + t_cruise_s + t_dec_s

    return t_acc_s, h_acc_m, t_cruise_s, h_dec_m, t_dec_s, t_total_s

def display_travel_parameters(params):
    """Display travel parameters with appropriate units (Stage Three)."""
    t_acc, h_acc, t_cruise, h_dec, t_dec, t_total = params
    print(f"\nTime to reach cruising velocity: {t_acc:.1f} s")
    print(f"Distance from starting planet when reaching cruising velocity: {h_acc / 1000:.1f} km")
    print(f"Cruise time: {t_cruise:.1f} s")
    print(f"Distance from destination planet to start deceleration: {h_dec / 1000:.1f} km")
    print(f"Time to decelerate: {t_dec:.1f} s")
    print(f"Total travel time: {t_total:.1f} s")
    days = int(t_total // 86400)
    rem = t_total % 86400
    hours = int(rem // 3600)
    rem %= 3600
    minutes = int(rem // 60)
    seconds = rem % 60
    print(f"Which is {days} days, {hours} hours, {minutes} minutes, {seconds:.1f} seconds")

def main():
    print("Planetary Travel Calculator - Stages Two and Three")
    print("==================================================")

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

    # Stage Two: Compute and display results for all planets
    stage_two_results = compute_stage_two_data(planet_data, a)
    display_stage_two_results(stage_two_results)

    # Stage Three: Interactive travel calculator
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