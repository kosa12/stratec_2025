import os
import re
from calculations import calculate_escape_velocity, parse_mass

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
    """Read solar system data and return {planet: (period_days, r_orbit_AU)}."""
    orbit_data = {}
    if not os.path.exists(file_path):
        print(f">> Error: '{file_path}' not found!")
        return orbit_data
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if not line.strip():
                    continue
                match = re.match(r'(\w+):\s*period\s*=\s*([\d.]+)\s*days,\s*orbital radius\s*=\s*([\d.]+)\s*AU', line.strip())
                if match:
                    planet, period_str, r_orbit_str = match.groups()
                    orbit_data[planet] = (float(period_str), float(r_orbit_str))
    except IOError as e:
        print(f">> Error: Unable to read '{file_path}': {str(e)}")
        return orbit_data
    return orbit_data
