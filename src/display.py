from calculations import compute_angular_positions

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

def display_angular_positions(positions, t_days):
    """Display angular positions of planets at time t_days."""
    print(f"\nPlanetary Positions at t = {t_days} days:")
    print("-" * 50)
    print(f"{'Planet':<15} {'Angular Position (degrees)':>30}")
    print("-" * 50)
    for planet in sorted(positions):
        angle = positions[planet]
        print(f"{planet:<15} {angle:>30.2f}")

def display_stage_five_results(start, dest, t_optimal_days, params, orbit_data):
    """Display Stage Five results including travel parameters and transfer window."""
    from constants import INITIAL_TIME_YEARS, DAYS_PER_YEAR
    if t_optimal_days is None:
        print(f"\nNo optimal transfer window found between {start} and {dest} within 10 years.")
        return
    
    wait_days = t_optimal_days - (INITIAL_TIME_YEARS * DAYS_PER_YEAR)
    wait_years = wait_days / DAYS_PER_YEAR
    print(f"\nOptimal Transfer Window from {start} to {dest}:")
    print(f"Start time: {INITIAL_TIME_YEARS} years + {wait_years:.2f} years ({wait_days:.1f} days)")
    display_travel_parameters(params)
    positions = compute_angular_positions(orbit_data, t_optimal_days)
    display_angular_positions(positions, t_optimal_days)

def display_stage_six_results(start, dest, t_optimal_days, params, orbit_data):
    """Display Stage Six results including travel parameters and dynamic transfer window."""
    from constants import INITIAL_TIME_YEARS, DAYS_PER_YEAR
    if t_optimal_days is None:
        print(f"\nNo optimal transfer window found between {start} and {dest} within 10 years with dynamic motion.")
        return
    
    wait_days = t_optimal_days - (INITIAL_TIME_YEARS * DAYS_PER_YEAR)
    wait_years = wait_days / DAYS_PER_YEAR
    print(f"\nOptimal Transfer Window from {start} to {dest} (Stage Six - Dynamic):")
    print(f"Start time: {INITIAL_TIME_YEARS} years + {wait_years:.2f} years ({wait_days:.1f} days)")
    display_travel_parameters(params)
    positions = compute_angular_positions(orbit_data, t_optimal_days)
    display_angular_positions(positions, t_optimal_days)