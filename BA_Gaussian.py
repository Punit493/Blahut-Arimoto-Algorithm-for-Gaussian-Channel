import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simpson
# Model Parameters 
num_inputs = 1000
num_outputs = 1000
num_samples = 5000

# Input grid
c_vals = np.logspace(-1, 1, num_inputs)
delta_c = np.gradient(c_vals)

# Output grid
g_vals = np.linspace(-0.03, 1.2, num_outputs)

b1 = 25e-4
b2 = 0.5
b3 = 4e-4

K = 1.0
n = 5.0

def mean(c):
    return c**n/(c**n + K**n)

def hill_prime(c):
    return n*c**(n-1)*K**n/(c**n + K**n)**2

def noise(c):
    h = mean(c)
    sigma_x = b1 * h
    sigma_y = (b2 * h**1.8) * ((1 - h)**2.2) + b3
    sigma_n = sigma_x + sigma_y
    return np.sqrt(sigma_n)
plt.plot(np.log(c_vals/K), noise(c_vals))
plt.xlabel('log(c/K)')
plt.ylabel('noise(c)')
plt.show()

def distribution(g_vals, c):
    term1 = np.sqrt(1/(2*np.pi*(noise(c))**2))
    term2 = np.exp((-0.5*((g_vals-mean(c))/noise(c))**2))
    return term1*term2

def chantransmat(c_vals, g_vals):
    delta_g = g_vals[1] - g_vals[0]
    Q_kj = np.zeros((len(g_vals), len(c_vals)))
    for j, c in enumerate(c_vals):
        Q_kj[:, j] = distribution(g_vals,c) * delta_g
    Q_kj /= Q_kj.sum(axis=0, keepdims=True)
    return Q_kj

def channel_capacity(Q_kj, tol=1e-3, max_iter=20000):
    epsilon = np.finfo(float).tiny
    num_outputs, num_inputs = Q_kj.shape
    p_j = np.ones(num_inputs) / num_inputs

    for _ in range(max_iter):
        p_k = Q_kj @ p_j
        p_k = np.maximum(p_k, epsilon)
        Q_safe = np.maximum(Q_kj, epsilon)
        log_term = np.sum(Q_safe * np.log(Q_safe / p_k[:, None]), axis=0)
        c_j = np.exp(log_term)
        I_L = np.log(np.sum(p_j * c_j)) / np.log(2)
        I_U = np.log(np.max(c_j)) / np.log(2)
        if abs(I_U - I_L) < tol:
            return I_L, p_j
        p_j *= c_j
        p_j /= np.sum(p_j)
    return I_L, p_j

def compute_mi(x, y):
    return mutual_info_regression(x.reshape(-1, 1), y, discrete_features=False)[0] / np.log(2)

# Build channel matrix
Q = chantransmat(c_vals, g_vals)

# Run BA algorithm for capacity
I_ba, p_opt = channel_capacity(Q)

MI_ba = I_ba

print(f"Mutual Information (BA-optimal, direct)  : {MI_ba:.4f} bits")

# Convert p_opt to PDF
p_pdf = p_opt / delta_c
p_pdf /= simpson(p_pdf, c_vals)



plt.figure(figsize=(8, 5))
plt.plot(c_vals, p_pdf, label='Blahut–Arimoto Optimal $P(c)$', color='green')
plt.xlabel("Input Concentration $c$")
plt.ylabel("Probability Density $P(c)$")
plt.title(f"Input Distributions")
plt.xscale('log')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

#Compute P(g) 
p_c = p_opt
p_c /= simpson(p_c1, c_vals)

P_g = Q @ p_c
P_g /= simpson(P_g, g_vals)

plt.figure(figsize=(8, 5))
plt.plot(g_vals, P_g, label=r'BA', color='red')
plt.xlabel("Output Expression Level $g$")
plt.ylabel("Probability Density $P(g)$")
plt.title("Predicted Output Distribution $P(g)$")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
