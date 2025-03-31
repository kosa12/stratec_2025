import math
from constants import G, EARTH_MASS, AU_TO_M, DAYS_PER_YEAR, MAX_WAIT_YEARS, INITIAL_TIME_YEARS

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
    """Compute travel parameters from start to dest planet (Stage Three/Five)."""
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

def compute_optimal_transfer_window(start, dest, planet_data, orbit_data, a, step_days=1):
    """Find optimal transfer window within 10 years from t0 + 100 years."""
    t_start_days = INITIAL_TIME_YEARS * DAYS_PER_YEAR
    max_wait_days = MAX_WAIT_YEARS * DAYS_PER_YEAR
    t_max_days = t_start_days + max_wait_days

    # Convert positions to radians for calculations
    def get_position(t_days, period):
        omega = 360.0 / period  # degrees/day
        return math.radians((omega * t_days) % 360)  # radians

    def distance_at_time(t_days):
        theta_start = get_position(t_days, orbit_data[start][0])
        theta_dest = get_position(t_days, orbit_data[dest][0])
        r_start = orbit_data[start][1] * AU_TO_M
        r_dest = orbit_data[dest][1] * AU_TO_M
        d = math.sqrt(r_start**2 + r_dest**2 - 2 * r_start * r_dest * math.cos(theta_dest - theta_start))
        return d

    def intersects_planet(t_days, other_planet):
        if other_planet == start or other_planet == dest:
            return False
        theta_start = get_position(t_days, orbit_data[start][0])
        theta_dest = get_position(t_days, orbit_data[dest][0])
        theta_other = get_position(t_days, orbit_data[other_planet][0])
        r_start = orbit_data[start][1] * AU_TO_M
        r_dest = orbit_data[dest][1] * AU_TO_M
        r_other = orbit_data[other_planet][1] * AU_TO_M
        radius_other = planet_data[other_planet][0] * 1000

        dx = r_dest * math.cos(theta_dest) - r_start * math.cos(theta_start)
        dy = r_dest * math.sin(theta_dest) - r_start * math.sin(theta_start)
        line_length = math.sqrt(dx**2 + dy**2)

        t = ((r_other * math.cos(theta_other) - r_start * math.cos(theta_start)) * dx +
             (r_other * math.sin(theta_other) - r_start * math.sin(theta_start)) * dy) / (line_length**2)
        t = max(0, min(1, t))

        x_closest = r_start * math.cos(theta_start) + t * dx
        y_closest = r_start * math.sin(theta_start) + t * dy
        dist_to_other = math.sqrt((x_closest - r_other * math.cos(theta_other))**2 +
                                  (y_closest - r_other * math.sin(theta_other))**2)
        return dist_to_other < radius_other

    min_distance = float('inf')
    optimal_t_days = t_start_days
    found_valid = False

    for t in range(int(t_start_days), int(t_max_days) + 1, step_days):
        d = distance_at_time(t)
        collision = False
        for planet in planet_data:
            if intersects_planet(t, planet):
                collision = True
                break
        if not collision and d < min_distance:
            min_distance = d
            optimal_t_days = t
            found_valid = True

    if not found_valid:
        return None, None

    orbit_data_at_t = {planet: (data[0], data[1]) for planet, data in orbit_data.items()}
    params = compute_travel_parameters(start, dest, planet_data, orbit_data_at_t, a)
    return optimal_t_days, params