# main.py
import simpy
import random
import matplotlib.pyplot as plt
import os

# Setup & Skeleton
# Create results folder if it doesn't exist (in same directory)
if not os.path.exists("./results"):
    os.makedirs("./results")

# Constants & Seed
RANDOM_SEED = 42    # For reproducibility
SIM_TIME = 100    # Total simulation time in minutes
TREATMENT_TIME = 10    # Avg treatment time for a patient (minutes)

# Patient Function
wait_times = []  # List to track wait times

def patient(env, name, doctors):
    #Simulate a patient arriving, waiting, being treated, and leaving.
    arrival_time = env.now
    print(f"{name} arrives at {arrival_time:.2f} minutes")

    with doctors.request() as request:
        yield request
        wait = env.now - arrival_time
        wait_times.append(wait)
        print(f"{name} starts treatment at {env.now:.2f} after waiting {wait:.2f} minutes")
        # Treatment duration (exponential)
        yield env.timeout(random.expovariate(1.0 / TREATMENT_TIME))
        print(f"{name} leaves at {env.now:.2f} minutes")


def setup(env, num_doctors=2, interval_patients=5):
    doctors = simpy.Resource(env, num_doctors)
    i = 0
    while True:
        i += 1
        env.process(patient(env, f"Patient {i}", doctors))
        yield env.timeout(random.expovariate(1.0 / interval_patients))
