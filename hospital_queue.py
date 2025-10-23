# main.py
import simpy
import random
import matplotlib.pyplot as plt
import statistics
import os

# Setup & Skeleton
# Create results folder
if not os.path.exists("./results"):
    os.makedirs("./results")

# Constants
RANDOM_SEED = 42   
SIM_TIME = 100    # Total simulation time in minutes
TREATMENT_TIME = 10    # Avg treatment time for a patient (minutes)

# Global metrics
wait_times = []    # Track wait times
throughput = []   # Track number of patients treated

# Patient process
def patient(env, name, doctors, treatment_time=TREATMENT_TIME):
    #Patient arrives, waits if necessary, gets treatment, leaves.
    arrival_time = env.now

    with doctors.request() as request:
        yield request
        wait = env.now - arrival_time
        wait_times.append(wait)
        
        # Treatment duration 
        yield env.timeout(random.expovariate(1.0 / TREATMENT_TIME))
        
        # Update throughput
        throughput.append(1)


#Hospital setup
def setup(env, num_doctors, arrival_interval, treatment_time=TREATMENT_TIME):
    #Generate patients and assign doctors
    doctors = simpy.Resource(env, capacity=num_doctors)
    i = 0
    while True:
        i += 1
        env.process(patient(env, f"Patient {i}", doctors, treatment_time))
        # Patient arrivals
        yield env.timeout(random.expovariate(1.0 / arrival_interval))


# Run a single scenario
def run_single_scenario(num_doctors, arrival_interval, label, treatment_time=TREATMENT_TIME):
    
    #Run one simulation scenario and return metrics
    wait_times.clear()
    throughput.clear()
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    env.process(setup(env, num_doctors, arrival_interval, treatment_time))
    env.run(until=SIM_TIME)

    # Metrics
    avg_wait = statistics.mean(wait_times) if wait_times else 0
    total_patients = sum(throughput)

    plt.hist(wait_times, bins=10, color='skyblue', edgecolor='black')
    plt.xlabel('Wait Time (minutes)')
    plt.ylabel('Number of Patients')
    plt.title(f'Patient Wait Times ({label})')
    plt.savefig(f'./results/wait_times_{label}.png')
    plt.close()

    return avg_wait, total_patients


# Run multiple scenarios
def run_multiple_scenarios():
    #Run low, medium, high load scenarios + faster treatment scenario
    scenarios = {
        "Low_Load": {"doctors": 3, "arrival_interval": 8, "treatment_time": 10},       # Few patients
        "Medium_Load": {"doctors": 2, "arrival_interval": 5, "treatment_time": 10},    # Normal
        "High_Load": {"doctors": 2, "arrival_interval": 2, "treatment_time": 10},      # Many patients
        "Fast_Treatment": {"doctors": 2, "arrival_interval": 5, "treatment_time": 5},  # Faster doctors
    }

    results = {}
    for label, params in scenarios.items():
        avg_wait, total_patients = run_scenario(params["doctors"], params["arrival_interval"], label, params["treatment_time"])
        results[label] = {"avg_wait": avg_wait, "throughput": total_patients}
