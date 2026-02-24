import numpy as np

def rts_smooth(states, covs, Fs):
    xs=states.copy(); Ps=covs.copy()
    for k in range(len(xs)-2,-1,-1):
        P_pred=Fs[k]@Ps[k]@Fs[k].T
        G=Ps[k]@Fs[k].T@np.linalg.inv(P_pred)
        xs[k]=xs[k]+G@(xs[k+1]-Fs[k]@xs[k])
        Ps[k]=Ps[k]+G@(Ps[k+1]-P_pred)@G.T
    return xs,Ps