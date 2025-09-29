import numpy as np
import matplotlib.pyplot as plt
import time

from balancer import WardropBalancer, SimpleBalancer


def run_simulation(
    n_sensors=20,
    steps=200,
    capacity_server1=800,  # numero richieste al secondo
    capacity_server2=1000,
    balancer_type="wardrop"  # "simple" oppure "wardrop"
):
    server_names = ["srv1", "srv2"]
    
    sensor_lambdas = np.random.randint(10, 51, size=n_sensors) # dati generati a casaccio
    
    # Creiamo i balancer per ogni sensore
    sensors = []
    x_p_s1=0
    x_p_s2=0
    for i in range(n_sensors):
        if balancer_type == "simple":
            sensors.append(SimpleBalancer(server_names, sensor_id=i))
        else:
            sensors.append(WardropBalancer(server_names, 
                                           sensor_id=i,
                                           dt=0.01,
                                           lambda_i = sensor_lambdas[i]))
        x_p_s1 += sensors[i].rates['srv1']*sensor_lambdas[i]
        x_p_s2 += sensors[i].rates['srv2']*sensor_lambdas[i]
        
    
    lat1 = x_p_s1/capacity_server1       
    lat2 = x_p_s2/capacity_server2
    
    latency_history = []
    
    latency_history.append((
        lat1,
        lat2
    ))
    
    latencies = [
                lat1,
                lat2
            ]
    
    for step in range(steps):
        x_p_s1 = 0
        x_p_s2 = 0
        for s in sensors:
            
            # dati generati da questo sensore nello step
            data_generated = np.random.randint(10, 50)
            
            # se è Wardrop, usa rates
            if isinstance(s, WardropBalancer):
                rates = s.balance(latencies)

                rate_srv1 = rates["srv1"]
                rate_srv2 = rates["srv2"]
                
                #print(f"Step: {step}  -  Server #1: {rate_srv1:.3f}  -  Server #2: {rate_srv2:.3f}")
                #time.sleep(1)
                
                x_p_s1 += rate_srv1*s.get_lambda()
                x_p_s2 += rate_srv2*s.get_lambda()
                
            # se è simple, usa probabilità
            else:
                probs = s.balance(latencies)
                p_srv1 = probs.get("srv1", 0.5)
                p_srv2 = probs.get("srv2", 0.5)

                # scelta server
                chosen = np.random.choice(["srv1", "srv2"], p=[p_srv1, p_srv2])
                if chosen == "srv1":
                    lat1 += data_generated
                else:
                    lat2 += data_generated
                    
        # Random Disturbance over the second server
        if step == 400:
            capacity_server2 *= 0.7
        
        lat1 = x_p_s1/capacity_server1
        lat2 = x_p_s2/capacity_server2
        
        latencies = [
                lat1,
                lat2
            ]

        latency_history.append((
            lat1,
            lat2
        ))

    return latency_history

#%%

if __name__ == "__main__":
    history = run_simulation(
        n_sensors=30,
        steps=1000,
        balancer_type="wardrop"
    )

    # Visualizza l'andamento delle latenze
    lat1 = [x[0] for x in history]
    lat2 = [x[1] for x in history]
    plt.figure(figsize=(7,4),dpi=300)
    plt.plot(lat1, label="Server #1 latency")
    plt.plot(lat2, label="Server #2 latency")
    plt.axhline(1.0, color="k", linestyle="--", alpha=1.0, label="latency limit")
    plt.xlabel("Step")
    plt.ylabel("Latency (load / capacity)")
    plt.title("Latency Evolution - Wardrop Balancer")
    plt.legend()
    plt.grid('on')