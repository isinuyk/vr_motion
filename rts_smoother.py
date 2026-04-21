import numpy as np

def rts_smooth(states, covs, Fs):
    xs = states.copy()
    Ps = covs.copy()
    for k in range(len(xs) - 2, -1, -1):
        P_pred = Fs[k] @ Ps[k] @ Fs[k].T
        # Small regularizer to avoid numerical issues on near-singular covariances.
        P_pred = P_pred + np.eye(P_pred.shape[0]) * 1e-9
        G = np.linalg.solve(P_pred.T, (Ps[k] @ Fs[k].T).T).T
        xs[k] = xs[k] + G @ (xs[k + 1] - Fs[k] @ xs[k])
        Ps[k] = Ps[k] + G @ (Ps[k + 1] - P_pred) @ G.T
    return xs, Ps