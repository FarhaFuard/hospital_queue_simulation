import simpy

# Simulation parameters
NUM_DOCTORS = 2
SIM_TIME = 100

# Placeholder for patient process
def patient(env, name):
    pass


# Placeholder for hospital setup
def setup(env):
    pass

# Run simulation
env = simpy.Environment()
env.process(setup(env))
env.run(until=SIM_TIME)
