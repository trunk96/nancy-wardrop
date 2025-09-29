# Load Balancer with Wardrop Equilibrium

This project implements different load balancing algorithms for distributing requests across multiple servers. It includes implementations of a simple balancer based on inverse latency and an advanced balancer based on Wardrop equilibrium.

## Overview

This project is part of **Work Package 6 (WP6)** of the **NANCY** project and is designed to simulate and compare different load balancing strategies in an environment with distributed sensors sending requests to multiple servers.

## Implemented Algorithms

### 1. SimpleBalancer
A load balancer that uses inverse latencies to calculate routing probabilities:
- Calculates probabilities proportional to the inverse of each server's latency
- Servers with lower latency receive higher probabilities
- Simple to implement and computationally efficient

### 2. WardropBalancer
An advanced balancer based on **Wardrop equilibrium** that converges to an optimal equilibrium:
- Implements the Wardrop algorithm for dynamic load balancing
- Converges to an equilibrium where all utilized servers have the same latency
- Uses discrete differential equations to dynamically update routing rates
- Configurable parameters to control convergence speed and stability

## Project Structure

```
.
├── balancer.py         # Load balancing class implementations
├── main_test.py        # Simulation and test script
├── README.md          # Project documentation
└── .gitignore         # Git ignore file
```

## Installation

### Prerequisites
- Python 3.7+
- NumPy
- Matplotlib (for visualizations)

### Setup
```bash
git clone <repository-url>
cd nancy-wardrop
pip install numpy matplotlib
```

## Usage

### Basic Usage

```python
from balancer import WardropBalancer, SimpleBalancer

# Server configuration
server_names = ["srv1", "srv2", "srv3"]

# Simple balancer
simple_balancer = SimpleBalancer(server_names, sensor_id=1)
probabilities = simple_balancer.balance([0.1, 0.2, 0.15])  # latencies
print(f"Probabilities: {probabilities}")

# Wardrop balancer
wardrop_balancer = WardropBalancer(
    server_names=server_names,
    sensor_id=1,
    dt=0.01,        # time step
    sigma=0.05,     # convergence speed
    epsilon=1e-3,   # latency equality threshold
    delta=1e-3      # negative rate threshold
)
rates = wardrop_balancer.balance([0.1, 0.2, 0.15])
print(f"Rates: {rates}")
```

### Complete Simulation

Run the simulation with multiple sensors and visualize latency evolution:

```bash
python main_test.py
```

The simulation:
1. Creates 30 sensors, each with its own balancer
2. Simulates 1000 steps of data generation and balancing
3. Visualizes latency evolution over time
4. Introduces a disturbance at step 400 to test adaptability

### Configuration Parameters

#### WardropBalancer

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `server_names` | list | - | List of server names |
| `sensor_id` | Any | None | Sensor identifier |
| `server_rates` | dict | None | Initial rates per server (uniform distribution if None) |
| `dt` | float | 0.01 | Algorithm time step |
| `sigma` | float | 0.05 | Convergence speed (too high values cause instability) |
| `epsilon` | float | 1e-3 | Threshold to consider two latencies equal |
| `delta` | float | 1e-3 | Threshold to avoid negative rates |

#### Simulation

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `n_sensors` | int | 20 | Number of sensors in the simulation |
| `steps` | int | 200 | Number of simulation steps |
| `capacity_server1` | int | 800 | First server capacity (req/sec) |
| `capacity_server2` | int | 1000 | Second server capacity (req/sec) |
| `balancer_type` | str | "wardrop" | Balancer type ("simple" or "wardrop") |

## Wardrop Algorithm - Technical Details

The Wardrop algorithm implements the user-equilibrium principle from game theory:

### Basic Principle
- Each user (sensor) chooses the path that minimizes their own cost
- At equilibrium, all utilized paths have the same cost
- Unused paths have greater or equal cost

### Implementation
The algorithm updates rates using the differential equation:

```
dx_i/dt = Σ(j≠i) [r_ji - r_ij]
```

Where:
- `x_i` is the routing rate to server i
- `r_ij` is the transfer rate from server i to server j
- `r_ij = σ * x_i` if `latency_i - latency_j > ε` and `x_i > δ`, otherwise 0

### Advantages
- **Guaranteed convergence** to optimal equilibrium
- **Adaptivity** to changing network conditions
- **Stability** with appropriate parameters
- **Fairness** in resource utilization

## Output Examples

### Latency Graph
The simulation produces a graph showing:
- Server latency evolution over time
- Threshold line to identify overload
- Effect of disturbances on system stability
- Balancer recovery capability

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is part of the NANCY project (funded by Smart Networks and Services Joint Undertaking (SNS JU) under the European Union's Horizon Europe research and innovation programme under Grant Agreement No 101096456).


## References

- Wardrop, J. G. (1952). "Some Theoretical Aspects of Road Traffic Research"
- Roughgarden, T. (2005). "Selfish Routing and the Price of Anarchy"