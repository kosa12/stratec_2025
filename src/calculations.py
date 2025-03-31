import math
from constants import G, EARTH_MASS, AU_TO_M

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

def compute_stage_two_data(planet_data, a):
    """Compute Stage Two data: {planet: (v_escape_m_s, t_s, d_m)}."""
    results = {}
    for planet, (radius_km, mass_kg, v_escape_m_s) in planet_data.items():
        t_s = v_escape_m_s / a
        d_m = 0.5 * a * t_s**2
        results[planet] = (v_escape_m_s, t_s, d_m)
    return results

def compute_travel_parameters(start, dest, planet_data, orbit_data, a):
    """Compute travel parameters from start to dest planet (Stage Three)."""
    r_orbit_start = orbit_data[start][1] * AU_TO_M
    r_orbit_dest = orbit_data[dest][1] * AU_TO_M
    D_m = abs(r_orbit_dest - r_orbit_start)

    r_start_m = planet_data[start][0] * 1000
    r_dest_m = planet_data[dest][0] * 1000

    v_cruise_m_s = max(planet_data[start][2], planet_data[dest][2])

    t_acc_s = v_cruise_m_s / a
    h_acc_m = 0.5 * a * t_acc_s**2

    t_dec_s = t_acc_s
    h_dec_m = h_acc_m

    d_cruise_m = D_m - r_start_m - r_dest_m - h_acc_m - h_dec_m
    if d_cruise_m < 0:
        d_cruise_m = 0
    t_cruise_s = d_cruise_m / v_cruise_m_s

    t_total_s = t_acc_s + t_cruise_s + t_dec_s

    return t_acc_s, h_acc_m, t_cruise_s, h_dec_m, t_dec_s, t_total_s

def compute_angular_positions(orbit_data, t_days):
    """Compute angular positions in degrees for all planets at time t_days."""
    positions = {}
    for planet, (period_days, _) in orbit_data.items():
        omega = 360.0 / period_days
        angle = (omega * t_days) % 360
        positions[planet] = angle
    return positions