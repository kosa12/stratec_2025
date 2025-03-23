import math
import os
import re

G = 6.67e-11  # Grav const in m^3 kg^-1 s^-2
EARTH_MASS = 5.972e24  # Earth mass in kg

def calculate_escape_velocity(mass_kg, radius_km):
    try:
        radius_m = radius_km * 1000
        velocity = math.sqrt((2 * G * mass_kg) / radius_m)
        return velocity
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def parse_mass(mass_str):
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

def process_planetary_data(file_path):
    results = {}
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found!")
        return results

    try:
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, 1):
                if not line.strip():
                    continue
                try:
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
                    velocity = calculate_escape_velocity(mass_kg, radius_km)
                    
                    if velocity is not None:
                        results[planet] = velocity
                    else:
                        print(f"Warning: Could not calculate velocity for {planet}")
                except Exception as e:
                    print(f"Warning: Skipping line {line_number}: {line.strip()} - {str(e)}")
    except IOError as e:
        print(f"Error: Could not read file '{file_path}': {str(e)}")
    return results

def display_results(results):
    if not results:
        print("No results to display!")
        return
        
    print("\nPlanetary Escape Velocities:")
    print("-" * 50)
    print(f"{'Planet':<15} {'Escape Velocity (km/s)':>20}")
    print("-" * 50)
    
    for planet, velocity in sorted(results.items()):
        velocity_km_s = velocity / 1000
        print(f"{planet:<15} {velocity_km_s:>20.1f}")

def main():
    print("Planetary Escape Velocity Calculator")
    print("===================================")
    
    while True:
        file_path = input("\nEnter path to planetary data file (or 'q' to quit): ")
        if file_path.lower() == 'q':
            print("Goodbye!")
            break
        results = process_planetary_data(file_path)
        display_results(results)

if __name__ == "__main__":
    main()