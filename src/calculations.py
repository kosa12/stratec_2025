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

def compute_travel_parameters(start, dest, planet_data, orbit_data, a, t_launch_days=None):
    """Compute travel parameters from start to dest planet (Stage Three/Five/Six)."""
    if t_launch_days is None:
        r_orbit_start = orbit_data[start][1] * AU_TO_M
        r_orbit_dest = orbit_data[dest][1] * AU_TO_M
        D_m = abs(r_orbit_dest - r_orbit_start)
    else:
        # Use launch-time positions for initial distance estimate
        theta_start = math.radians((360.0 / orbit_data[start][0] * t_launch_days) % 360)
        theta_dest = math.radians((360.0 / orbit_data[dest][0] * t_launch_days) % 360)
        r_start = orbit_data[start][1] * AU_TO_M
        r_dest = orbit_data[dest][1] * AU_TO_M
        D_m = math.sqrt(r_start**2 + r_dest**2 - 2 * r_start * r_dest * math.cos(theta_dest - theta_start))

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

def compute_travel_time(start, dest, planet_data, orbit_data, a, t_launch_days):
    """Helper function to compute total travel time in days for dynamic simulation."""
    params = compute_travel_parameters(start, dest, planet_data, orbit_data, a, t_launch_days)
    return params[5] / 86400  # Convert seconds to days

def compute_angular_positions(orbit_data, t_days):
    """Compute angular positions in degrees for all planets at time t_days."""
    positions = {}
    for planet, (period_days, _) in orbit_data.items():
        omega = 360.0 / period_days
        angle = (omega * t_days) % 360
        positions[planet] = angle
    return positions

def compute_optimal_transfer_window(start, dest, planet_data, orbit_data, a, step_days=1):
    """Find optimal transfer window within 10 years from t0 + 100 years (Stage Five)."""
    t_start_days = INITIAL_TIME_YEARS * DAYS_PER_YEAR
    max_wait_days = MAX_WAIT_YEARS * DAYS_PER_YEAR
    t_max_days = t_start_days + max_wait_days

    def get_position(t_days, period):
        omega = 360.0 / period
        return math.radians((omega * t_days) % 360)

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

def compute_dynamic_transfer_window(start, dest, planet_data, orbit_data, a, step_days=1):
    """Find optimal transfer window with dynamic planet motion (Stage Six)."""
    t_start_days = INITIAL_TIME_YEARS * DAYS_PER_YEAR
    max_wait_days = MAX_WAIT_YEARS * DAYS_PER_YEAR
    t_max_days = t_start_days + max_wait_days

    def get_position(t_days, period):
        omega = 360.0 / period
        return math.radians((omega * t_days) % 360)

    def distance_at_time(t_days):
        theta_start = get_position(t_days, orbit_data[start][0])
        theta_dest = get_position(t_days, orbit_data[dest][0])
        r_start = orbit_data[start][1] * AU_TO_M
        r_dest = orbit_data[dest][1] * AU_TO_M
        d = math.sqrt(r_start**2 + r_dest**2 - 2 * r_start * r_dest * math.cos(theta_dest - theta_start))
        return d

    def check_path_collision(t_launch_days):
        t_travel_days = compute_travel_time(start, dest, planet_data, orbit_data, a, t_launch_days)
        t_end_days = t_launch_days + t_travel_days
        step_size = max(1, int(t_travel_days / 100))

        theta_start_launch = get_position(t_launch_days, orbit_data[start][0])
        theta_dest_end = get_position(t_end_days, orbit_data[dest][0])
        r_start = orbit_data[start][1] * AU_TO_M
        r_dest = orbit_data[dest][1] * AU_TO_M

        x_start = r_start * math.cos(theta_start_launch)
        y_start = r_start * math.sin(theta_start_launch)
        x_dest = r_dest * math.cos(theta_dest_end)
        y_dest = r_dest * math.sin(theta_dest_end)

        for t in range(int(t_launch_days), int(t_end_days) + 1, step_size):
            f = (t - t_launch_days) / t_travel_days if t_travel_days > 0 else 0
            f = min(f, 1.0)
            x_rocket = x_start + f * (x_dest - x_start)
            y_rocket = y_start + f * (y_dest - y_start)

            for planet in planet_data:
                if planet == start or planet == dest:
                    continue
                theta_planet = get_position(t, orbit_data[planet][0])
                r_planet = orbit_data[planet][1] * AU_TO_M
                x_planet = r_planet * math.cos(theta_planet)
                y_planet = r_planet * math.sin(theta_planet)
                radius_planet = planet_data[planet][0] * 1000

                dist = math.sqrt((x_rocket - x_planet)**2 + (y_rocket - y_planet)**2)
                if dist < radius_planet:
                    return True
        return False

    min_distance = float('inf')
    optimal_t_days = t_start_days
    found_valid = False

    for t in range(int(t_start_days), int(t_max_days) + 1, step_days):
        d = distance_at_time(t)
        if not check_path_collision(t) and d < min_distance:
            min_distance = d
            optimal_t_days = t
            found_valid = True

    if not found_valid:
        return None, None

    params = compute_travel_parameters(start, dest, planet_data, orbit_data, a, optimal_t_days)
    return optimal_t_days, params

def compute_rocket_trajectory(start, dest, planet_data, orbit_data, a, t_launch_days):
    """Compute rocket's position over time from launch to destination."""
    from constants import AU_TO_M
    t_travel_days = compute_travel_time(start, dest, planet_data, orbit_data, a, t_launch_days)
    t_end_days = t_launch_days + t_travel_days
    step_size = max(0.1, t_travel_days / 100)  # At least 100 steps for smooth animation

    theta_start_launch = math.radians((360.0 / orbit_data[start][0] * t_launch_days) % 360)
    theta_dest_end = math.radians((360.0 / orbit_data[dest][0] * t_end_days) % 360)
    r_start = orbit_data[start][1] * AU_TO_M
    r_dest = orbit_data[dest][1] * AU_TO_M

    x_start = r_start * math.cos(theta_start_launch)
    y_start = r_start * math.sin(theta_start_launch)
    x_dest = r_dest * math.cos(theta_dest_end)
    y_dest = r_dest * math.sin(theta_dest_end)

    trajectory = []
    for t in [t_launch_days + i * step_size for i in range(int(t_travel_days / step_size) + 1)]:
        f = (t - t_launch_days) / t_travel_days if t_travel_days > 0 else 0
        f = min(f, 1.0)
        x_rocket = x_start + f * (x_dest - x_start)
        y_rocket = y_start + f * (y_dest - y_start)
        trajectory.append((t, x_rocket, y_rocket))
    
    # Include planetary positions at each step
    all_positions = {}
    for planet in orbit_data:
        positions = []
        for t in [t_launch_days + i * step_size for i in range(int(t_travel_days / step_size) + 1)]:
            theta = math.radians((360.0 / orbit_data[planet][0] * t) % 360)
            r = orbit_data[planet][1] * AU_TO_M
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            positions.append((x, y))
        all_positions[planet] = positions
    
    return trajectory, all_positions, t_launch_days, t_end_days