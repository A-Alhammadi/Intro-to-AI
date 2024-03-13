import csv
import time
import heapq

from collections import deque

# Step 1: Load adjacencies
def load_adjacencies(filename):
    adjacencies = {}
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split(' ')
            town1, town2 = parts[0], parts[1]
            if town1 not in adjacencies:
                adjacencies[town1] = []
            if town2 not in adjacencies:
                adjacencies[town2] = []
            adjacencies[town1].append(town2)
            adjacencies[town2].append(town1) 
    return adjacencies

# Step 2: Load coordinates
def load_coordinates(filename):
    coordinates = {}
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')  # Adjusting to comma-delimited
        for row in reader:
            if len(row) != 3:  # Check if row has exactly 3 elements
                print(f"Skipping malformed line: {row}")
                continue
            town = row[0]  
            lat, lon = map(float, row[1:])   # Convert strings to floats
            coordinates[town] = (lat, lon)
    return coordinates


# Utility function to calculate distance between two points
def calculate_distance(coord1, coord2):
    from math import radians, cos, sin, asin, sqrt
    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    
    # Haversine formula
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371  # Radius of Earth in kilometers
    return c * r

# Implement search algorithm 1 (Breadth-First)
def breadth_first_search(adjacencies, start, goal):
    visited = set()
    queue = deque([(start, [start])])

    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path
        for neighbor in adjacencies[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None

# Implement search algorithm 2 (Depth-First)
def depth_first_search(adjacencies, start, goal, path=None, visited=None):
    if visited is None:
        visited = set()
    if path is None:
        path = [start]
    
    visited.add(start)
    
    if start == goal:
        return path
    
    for neighbor in adjacencies[start]:
        if neighbor not in visited:
            result = depth_first_search(adjacencies, neighbor, goal, path + [neighbor], visited)
            if result is not None:
                return result
    return None

# Implement search algorithm 3 (ID-DFS)
def depth_limited_search(adjacencies, start, goal, limit, path=None, visited=None):
    if visited is None:
        visited = set()
    if path is None:
        path = [start]

    visited.add(start)
    
    if start == goal:
        return path
    if limit <= 0:
        return None

    for neighbor in adjacencies[start]:
        if neighbor not in visited:
            result = depth_limited_search(adjacencies, neighbor, goal, limit-1, path + [neighbor], visited)
            if result is not None:
                return result
    return None

def iterative_deepening_dfs(adjacencies, start, goal, max_depth):
    for depth in range(max_depth):
        visited = set()
        result = depth_limited_search(adjacencies, start, goal, depth, visited=visited)
        if result is not None:
            return result
    return None


def heuristic(node, goal, coordinates):
    # This is a simple heuristic function that could be the straight-line distance
    # between the current node and the goal.
    return calculate_distance(coordinates[node], coordinates[goal])

# Implement search algorithm 4 (Best-First)
def best_first_search(adjacencies, start, goal, coordinates):
    visited = set()
    # Priority queue, elements are tuples: (heuristic, node, path)
    priority_queue = [(heuristic(start, goal, coordinates), start, [start])]

    while priority_queue:
        # Select the node with the lowest heuristic value
        _, current, path = heapq.heappop(priority_queue)
        if current == goal:
            return path

        if current not in visited:
            visited.add(current)
            for neighbor in adjacencies[current]:
                if neighbor not in visited:
                    # Add new nodes to the priority queue with updated heuristic
                    heapq.heappush(priority_queue, (heuristic(neighbor, goal, coordinates), neighbor, path + [neighbor]))
    
    return None

# Implement search algorithm 5 (A-star)
def a_star_search(adjacencies, start, goal, coordinates):
    visited = set()
    # Priority queue, elements are tuples: (cost + heuristic, cost, node, path)
    priority_queue = [(heuristic(start, goal, coordinates), 0, start, [start])]

    while priority_queue:
        # Select the node with the lowest combined cost and heuristic value
        _, cost, current, path = heapq.heappop(priority_queue)
        if current == goal:
            return path

        if current not in visited:
            visited.add(current)
            for neighbor in adjacencies[current]:
                if neighbor not in visited:
                    # Calculate new cost from start to neighbor
                    new_cost = cost + calculate_distance(coordinates[current], coordinates[neighbor])
                    # Add new nodes to the priority queue with updated cost and heuristic
                    heapq.heappush(priority_queue, (new_cost + heuristic(neighbor, goal, coordinates), new_cost, neighbor, path + [neighbor]))
    
    return None




# Main program
def main():
    adjacencies = load_adjacencies('Adjacencies.txt')
    coordinates = load_coordinates('coordinates.csv')
    start_town = input("Enter starting town: ")
    end_town = input("Enter ending town: ")

    if start_town not in adjacencies or end_town not in adjacencies:
        print("One or both towns are not in the database.")
        return

    print("Select search method:\n1. Breadth-first search\n2. Depth-first search\n3. ID-DFS search\n4. Best-first search\n5. A* search")
    choice = int(input("Enter your choice (1-5): "))

    start_time = time.perf_counter()
    if choice == 1:
        route = breadth_first_search(adjacencies, start_town, end_town)
    elif choice == 2:
        route = depth_first_search(adjacencies, start_town, end_town)
    elif choice == 3:
        max_depth = len(adjacencies)  # You can adjust this value as needed
        route = iterative_deepening_dfs(adjacencies, start_town, end_town, max_depth)
    elif choice == 4:
        route = best_first_search(adjacencies, start_town, end_town, coordinates)
    elif choice == 5:
        route = a_star_search(adjacencies, start_town, end_town, coordinates)
    else:
        print("Invalid choice. Please select a valid search method.")
    end_time = time.perf_counter()

    if route:
        print("Route:", " -> ".join(route))
        print(f"Time taken: {end_time - start_time:.6f} seconds")
        total_distance = sum(calculate_distance(coordinates[route[i]], coordinates[route[i+1]]) for i in range(len(route)-1))
        print("Total distance:", total_distance, "km")
    else:
        print("No route found.")

if __name__ == "__main__":
    main()
