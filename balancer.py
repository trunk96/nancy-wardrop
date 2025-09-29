class Balancer:
    def __init__(self, server_names=None, sensor_id=None):
        self.server_names = server_names if server_names else []
        self.probabilities = {}
        self.sensor_id = sensor_id

    def balance(self):
        # Implement balancing logic here
        pass


class SimpleBalancer(Balancer):
    def __init__(self, server_names, sensor_id):
        super().__init__(server_names, sensor_id)
        self.probabilities = {}

    def balance(self, latencies_list):
        inverse_latencies = [1.0 / latency if latency > 0 else 0 for latency in latencies_list]
        total_inverse = sum(inverse_latencies)
        if total_inverse > 0:
            for i, srv in enumerate(self.server_names):
                self.probabilities[srv] = inverse_latencies[i] / total_inverse
        if(self.sensor_id == 1): print(f"Sensor {self.sensor_id} updated probabilities: {self.probabilities}")
        return self.probabilities


class WardropBalancer(Balancer):
    def __init__(self, server_names, sensor_id=None, server_rates=None, dt=0.01, sigma=0.05, epsilon=1e-3, delta=1e-3):
        """
        Initializes the balancer with server configuration and algorithm parameters.
        Args:
            server_names (list): List of server names to balance requests across.
            sensor_id (Any, optional): Identifier for the sensor associated with this balancer.
            dt (float, optional): Time step for the balancing algorithm, in seconds. Default is 0.01.
            sigma (float, optional): Parameter deciding the velocity of the Wardrop algorithm in converging to the equilibrium 
                (if too high it may cause instability). Default is 0.05.
            epsilon (float, optional): Small constant to decide when two latencies are considered equal. Default is 1e-3.
            delta (float, optional): Small constant to avoid to end up in negative rates. Default is 1e-3.
            server_rates (dict, optional): Initial request rates for each server. If None, rates are initialized equally. Default is None.
        """
        super().__init__(server_names, sensor_id)
        # self.rates will contain the current request rates to each server
        self.rates = server_rates if server_rates is not None else {}
        # Initialize with equal distribution, but could be changed
        if server_rates is None:
            for serv in server_names:
                self.rates[serv] = 1.0 / len(server_names)
        self.dt = dt
        self.sigma = sigma
        self.epsilon = epsilon
        self.delta = delta
        
    def get_lambda(self):
        return self.lambda_i

    def _compute_r(self, x_pki, l_i, l_j, sigma=None, epsilon=None, delta=None):
        sigma = sigma if sigma is not None else self.sigma
        epsilon = epsilon if epsilon is not None else self.epsilon
        delta = delta if delta is not None else self.delta

        if (l_i - l_j > epsilon) and (x_pki > delta):
            return sigma * x_pki
        else:
            return 0.0       

    def balance(self, latencies_list):
        """
        Adjusts the rates for each server based on the provided list of latencies.
        Args:
            latencies_list (list of float): List of latency values for each server.
        Returns:
            dict: Updated rates for each server, keyed by server name.
        """
        for i in range(len(latencies_list)):
            dx = 0
            for j in range(len(latencies_list)):
                if i != j:
                    r_ij = self._compute_r(self.rates[self.server_names[i]], latencies_list[i], latencies_list[j])
                    r_ji = self._compute_r(self.rates[self.server_names[j]], latencies_list[j], latencies_list[i])
                    dx += r_ji - r_ij
            self.rates[self.server_names[i]] += dx * self.dt
            # Ensure rates are non-negative, even if it should not happen in any case
            if self.rates[self.server_names[i]] < 0:
                self.rates[self.server_names[i]] = 0
        # Normalize rates to ensure they sum to 1 and are within [0,1] (probabilities)
        total = sum(self.rates.values())
        if total > 0:
            for srv in self.server_names:
                self.rates[srv] = max(0.0, self.rates[srv] / total)
        else:
            # If total is zero, assign equal probability to each server
            for srv in self.server_names:
                self.rates[srv] = 1.0 / len(self.server_names)
        return self.rates

            