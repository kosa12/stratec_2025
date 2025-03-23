import math
import os
import re

G = 6.67e-11  # Grav const in m^3 kg^-1 s^-2
EARTH_MASS = 5.972e24  # Earth mass in kg

def calculate_escape_velocity(mass_kg, radius_km):
    """Calculate escape velocity given mass in kg and radius in km."""
    try:
        radius_m = radius_km * 1000
        velocity = math.sqrt((2 * G * mass_kg) / radius_m)
        return velocity
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def parse_mass(mass_str):
    """Parse mass string to kg, handling both kg and Earth units."""
    try:
        mass_str = mass_str.strip()
        if 'kg' in mass_str:
            mass_str = mass_str.replace('kg', '').strip()
            if '*' in mass_str:
                parts = mass_str.split('*')
                base = float(parts[0].strip())
                exponent_part = parts[1].strip()
                if '^' in exponent_part:
                    exp = float(exponent_part.split('^')[1])
                    return base * (10 ** exp)
                else:
                    return base * float(exponent_part)
            else:
                return float(mass_str)
        else:
            return float(mass_str.split()[0]) * EARTH_MASS
    except (ValueError, TypeError):
        return None

def read_rocket_data(file_path):
    """Read rocket data file and return number of engines and acceleration per engine."""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found!")
        return None, None
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if len(lines) < 2:
                print("Error: Rocket data file must have at least two lines.")
                return None, None
            num_engines_line = lines[0].strip()
            acc_line = lines[1].strip()
            if not num_engines_line.startswith("Number of rocket engines:"):
                print("Error: First line must start with 'Number of rocket engines:'")
                return None, None
            if not acc_line.startswith("Acceleration per engine:"):
                print("Error: Second line must start with 'Acceleration per engine:'")
                return None, None
            num_engines = int(num_engines_line.split(':')[1].strip())
            acc_str = acc_line.split(':')[1].strip()
            acc_per_engine = float(acc_str.split()[0])  # e.g., "10 m/s^2" -> 10
            return num_engines, acc_per_engine
    except Exception as e:
        print(f"Error reading rocket data: {str(e)}")
        return None, None

def process_planetary_data(file_path):
    """Process planetary data file and return escape velocities."""
    results = {}
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found!")
        return results
    try:
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, 1):
                if not line.strip():
                    continue
                match = re.match(r'(\w+):\s*diameter\s*=\s*([\d.]+)\s*km,\s*mass\s*=\s*([^,]+)', line.strip())
                if not match:
                    print(f"Warning: Skipping malformed line {line_number}: {line.strip()}")
                    continue
                planet, diameter_str, mass_str = match.groups()
                diameter_km = float(diameter_str)
                mass_kg = parse_mass(mass_str.strip())
                if mass_kg is None:
                    print(f"Warning: Invalid mass for {planet}: {mass_str}")
                    continue
                radius_km = diameter_km / 2
                v_escape = calculate_escape_velocity(mass_kg, radius_km)
                if v_escape is not None:
                    results[planet] = v_escape
                else:
                    print(f"Warning: Could not calculate velocity for {planet}")
    except IOError as e:
        print(f"Error: Could not read file '{file_path}': {str(e)}")
    return results

def display_results(results):
    """Display results in a formatted table."""
    if not results:
        print("No results to display!")
        return
    print("\nPlanetary Escape Data:")
    print("-" * 70)
    print(f"{'Planet':<15} {'Escape Velocity (km/s)':>20} {'Time (s)':>15} {'Distance (km)':>15}")
    print("-" * 70)
    for planet in sorted(results):
        v_escape, t, d = results[planet]
        v_km_s = v_escape / 1000
        d_km = d / 1000
        print(f"{planet:<15} {v_km_s:>20.1f} {t:>15.1f} {d_km:>15.1f}")

def main():
    """Main function to run the application."""
    print("Planetary Escape Velocity Calculator - Stage Two")
    print("================================================")
    while True:
        planetary_file = input("\nEnter path to planetary data file (or 'q' to quit): ")
        if planetary_file.lower() == 'q':
            print("Goodbye!")
            break
        rocket_file = input("Enter path to rocket data file: ")
        num_engines, acc_per_engine = read_rocket_data(rocket_file)
        if num_engines is None or acc_per_engine is None:
            continue
        a = num_engines * acc_per_engine
        results = process_planetary_data(planetary_file)
        if not results:
            continue

        for planet in results:
            v_escape = results[planet]
            t = v_escape / a
            d = 0.5 * a * t**2
            results[planet] = (v_escape, t, d)
        display_results(results)

if __name__ == "__main__":
    main()