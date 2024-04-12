import random

# Activity class representing a scheduled activity
class Activity:
    def __init__(self, name, enrollment):
        self.name = name
        self.enrollment = enrollment

# Room class representing a room with capacity
class Room:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity

# Schedule class representing a complete schedule with assignments
class Schedule:
    def __init__(self, activities, rooms, timeslots):
        self.assignments = []
        for activity in activities:
            self.assignments.append((activity, random.choice(rooms), random.choice(timeslots), random.choice(list(facilitators.keys()))))

    def fitness(self):
        score = 0
        assigned_facilitators = {}  # Track facilitator workload
        for activity, room, timeslot, facilitator in self.assignments:
            # Room size penalties
            if room.capacity < activity.enrollment:
                score -= 0.5
            elif room.capacity > 3 * activity.enrollment:
                score -= 0.2
            elif room.capacity > 6 * activity.enrollment:
                score -= 0.4
            else:
                score += 0.3

            # Facilitator preferences and workload
            if activity.name in facilitators[facilitator]["preferred"]:
                score += 0.5
            elif activity.name in facilitators[facilitator]["other"]:
                score += 0.2
            else:
                score -= 0.1

            if timeslot not in assigned_facilitators:
                assigned_facilitators[timeslot] = set()
            assigned_facilitators[timeslot].add(facilitator)

        # Check for conflicts and workload across timeslots
        for timeslot, assigned_facilitators_set in assigned_facilitators.items():
            if len(assigned_facilitators_set) > 1:
                score -= 0.2  # Multiple activities for a facilitator in the same timeslot

        for facilitator, activity_list in assigned_facilitators.items():
            total_activities = len(activity_list)
            if total_activities > 4:
                score -= 0.5
            elif total_activities in [1, 2] and facilitator != "Tyler":
                score -= 0.4

        # Activity-specific adjustments (SLA 101 & 191)
        sla101_timeslots = [t for _, _, t, _ in self.assignments if "SLA101" in activity.name]
        sla191_timeslots = [t for _, _, t, _ in self.assignments if "SLA191" in activity.name]

        if len(sla101_timeslots) == 2 and len(sla191_timeslots) == 2:  # Check if both lists have 2 elements
            if abs(sla101_timeslots[0] - sla101_timeslots[1]) > 4:
                score += 0.5
            elif sla101_timeslots[0] == sla101_timeslots[1]:
                score -= 0.5
            if abs(sla191_timeslots[0] - sla191_timeslots[1]) > 4:
                score += 0.5 
            elif sla191_timeslots[0] == sla191_timeslots[1]:
                score -= 0.5 

        for i in range(len(sla101_timeslots)):
            for j in range(len(sla191_timeslots)):
                time_diff = abs(sla101_timeslots[i] - sla191_timeslots[j])
                if time_diff == 1: 
                    score += 0.25
                elif time_diff == 0:
                    score -= 0.25
                elif time_diff == 2: # Consecutive timeslots
                    rooms = [r for _, r, _, _ in self.assignments if "SLA101" in activity.name or "SLA191" in activity.name]
                    if (rooms[0] in ["Roman", "Beach"] and rooms[1] not in ["Roman", "Beach"]) or (rooms[1] in ["Roman", "Beach"] and rooms[0] not in ["Roman", "Beach"]):
                        score -= 0.4
                    else:
                        score += 0.5 

        return score
    
# Define facilitators with preferences and cross-over options
facilitators = {
    "Lock": {"preferred": ["SLA100", "SLA191", "SLA291"], "other": []},
    "Glen": {"preferred": ["SLA100", "SLA191", "SLA201", "SLA303", "SLA304"], "other": []},
    "Banks": {"preferred": ["SLA100", "SLA191", "SLA201", "SLA291", "SLA303", "SLA304"], "other": []},
    "Richards": {"preferred": [], "other": ["SLA100", "SLA191", "SLA201", "SLA291", "SLA304", "SLA394", "SLA451"]},
}

# Fitness function to evaluate a schedule


# Generate a population of random schedules
def generate_population(num_schedules, activities, rooms, timeslots):
    return [Schedule(activities, rooms, timeslots) for _ in range(num_schedules)]

# Select two parents from the population
def select_parents(population):
    return random.choices(population, k=2)

# Perform single-point crossover between parents
def crossover(parent1, parent2):
    split_point = random.randint(1, len(parent1.assignments) - 1)
    child1 = Schedule([], [], [])
    child2 = Schedule([], [], [])
    child1.assignments = parent1.assignments[:split_point] + parent2.assignments[split_point:]
    child2.assignments = parent2.assignments[:split_point] + parent1.assignments[split_point:]
    return child1, child2

# Mutate a schedule by randomly changing room or facilitator assignment
def mutate(schedule, rooms):
    index = random.randint(0, len(schedule.assignments) - 1)
    activity, room, timeslot, _ = schedule.assignments[index]
    # Randomly change room or facilitator
    if random.random() < 0.5:
        schedule.assignments[index] = (activity, random.choice(rooms), timeslot, random.choice(list(facilitators.keys())))
    else:
        schedule.assignments[index] = (activity, room, timeslot, random.choice(list(facilitators.keys())))

# Main function to run the genetic algorithm
def main():
    # Example usage (replace with actual data)
    activities = [
        Activity("SLA100A", 50),
        Activity("SLA191B", 50),
        Activity("SLA201", 50), 
        Activity("SLA291", 50),
        # ... add all other activities here
    ]
    rooms = [
    Room("Slater 003", 45),
    Room("Roman 216", 30),
    Room("Loft 206", 75),
    Room("Roman 201", 50),
    Room("Loft 310", 108),
    Room("Beach 201", 60),
    Room("Beach 301", 75),
    Room("Logos 325", 450),
    Room("Frank 119", 60)
]
    timeslots = ["10 AM", "11 AM", ...]

    population_size = 500
    generations = 100
    mutation_rate = 0.01

    population = generate_population(population_size, activities, rooms, timeslots)
    best_schedule = max(population, key=lambda s: s.fitness())
    best_fitness = best_schedule.fitness()
    generation_best_fitness = best_fitness

    for generation in range(generations):
        new_population = []
        for _ in range(population_size // 2):
            parent1, parent2 = select_parents(population)
            child1, child2 = crossover(parent1, parent2)
            if random.random() < mutation_rate:
                mutate(child1, rooms)
            if random.random() < mutation_rate:
                mutate(child2, rooms)
            new_population.extend([child1, child2])
        population = new_population

        # Track best schedule and fitness
        current_best_schedule = max(population, key=lambda s: s.fitness())
        current_best_fitness = current_best_schedule.fitness()
        if current_best_fitness > best_fitness:
            best_schedule = current_best_schedule
            best_fitness = current_best_fitness

        # Adjust mutation rate and check for termination
        if generation >= 100 and (current_best_fitness - generation_best_fitness) / generation_best_fitness < 0.01:
            break
        else:
            generation_best_fitness = current_best_fitness
            # Adjust mutation rate here (e.g., mutation_rate /= 2)

    # Print best schedule
    print("Best schedule fitness:", best_fitness)
    for activity, room, timeslot, facilitator in best_schedule.assignments:
        print(f"{activity.name}: {room.name} - {timeslot} ({facilitator})")

# Run the main function
if __name__ == "__main__":
    main()
