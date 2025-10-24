#Hospital Queue Simulation

import simpy
import random
import matplotlib.pyplot as plt
import statistics
import os


# Setup
# Create results folder 
if not os.path.exists("./results"):
    os.makedirs("./results")

# Constants
RANDOM_SEED = 42
SIM_TIME = 100      # Simulation time in minutes
TREATMENT_TIME = 10   # Avg treatment time per patient (minutes)

# Global metrics
wait_times = []    # Track wait times
throughput = []   # Track number of patients treated


# Patient process
def patient(env, name, doctors, treatment_time=TREATMENT_TIME):
    #Patient arrives, waits, gets treatment, leaves
    arrival_time = env.now

    with doctors.request() as request:
        yield request
        wait = env.now - arrival_time
        wait_times.append(wait)

        # Treatment duration
        yield env.timeout(random.expovariate(1.0 / treatment_time))

        # Update throughput
        throughput.append(1)


# Hospital setup
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
def run_scenario(num_doctors, arrival_interval, label, treatment_time=TREATMENT_TIME):

    #Run simulation for a scenario and return metrics
    wait_times.clear()
    throughput.clear()
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    env.process(setup(env, num_doctors, arrival_interval, treatment_time))
    env.run(until=SIM_TIME)

    # Metrics
    avg_wait = statistics.mean(wait_times) if wait_times else 0
    total_patients = sum(throughput)

    # Visualization: histogram
    plt.hist(wait_times, bins=10, color='skyblue', edgecolor='black')
    plt.xlabel('Wait Time (minutes)')
    plt.ylabel('Number of Patients')
    plt.title(f'Patient Wait Times ({label})')
    plt.savefig(f'./results/wait_times_{label}.png')
    plt.close()

    return avg_wait, total_patients


def run_multiple_scenarios():
    # Run low, medium, high load scenarios + faster treatment scenario
    scenarios = {
        "Low_Load": {"doctors": 3, "arrival_interval": 8, "treatment_time": 10},
        "Medium_Load": {"doctors": 2, "arrival_interval": 5, "treatment_time": 10},
        "High_Load": {"doctors": 2, "arrival_interval": 2, "treatment_time": 10},
        "Fast_Treatment": {"doctors": 2, "arrival_interval": 5, "treatment_time": 5},
    }

    results = {}
    for label, params in scenarios.items():
        avg_wait, total_patients = run_scenario(
            params["doctors"], 
            params["arrival_interval"], 
            label, 
            params["treatment_time"]
        )
        results[label] = {"avg_wait": avg_wait, "throughput": total_patients}

    # Comparative visualization: average wait
    labels = list(results.keys())
    avg_waits = [results[l]["avg_wait"] for l in labels]
    total_patients = [results[l]["throughput"] for l in labels]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, avg_waits, color='orange', alpha=0.7)
    plt.ylabel('Average Wait Time (minutes)')
    plt.title('Average Wait Time Across Scenarios')
    plt.savefig('./results/avg_wait_comparison.png')
    plt.close()

    # Comparative visualization: throughput
    plt.figure(figsize=(8, 5))
    plt.bar(labels, total_patients, color='green', alpha=0.7)
    plt.ylabel('Total Patients Treated')
    plt.title('Throughput Across Scenarios')
    plt.savefig('./results/throughput_comparison.png')
    plt.close()

    # Print results
    print("**Scenario results:**")
    for label, metrics in results.items():
        print(f"{label}: Avg Wait = {metrics['avg_wait']:.2f} min, Throughput = {metrics['throughput']} patients")

    # Save results to file
    with open('./results/simulation_summary.txt', 'w') as f:
        f.write("=== Hospital Simulation Results ===\n\n")
        for label, metrics in results.items():
            f.write(f"{label}:\n")
            f.write(f"  Average Wait Time: {metrics['avg_wait']:.2f} minutes\n")
            f.write(f"  Throughput: {metrics['throughput']} patients\n\n")


# Main execution
if __name__ == "__main__":
    run_multiple_scenarios()


