from pathlib import Path
import numpy as np
import pandas as pd

INPUT = Path("outputs/goemotions/goemotions_pair_boundary_residuals.csv")
OUTPUT = Path("outputs/goemotions/goemotions_pair_residual_permutation.csv")
N_PERM = 5000
SEED = 20261026

if __name__ == "__main__":
    df = pd.read_csv(INPUT)
    rng = np.random.default_rng(SEED)
    rows=[]
    for pair,g in df.groupby("pair"):
        g=g.dropna(subset=["merge_tendency","item_adjusted_cardinality"]).copy()
        x=g["item_adjusted_cardinality"].to_numpy()
        y=g["merge_tendency"].to_numpy()
        slope,intercept=np.polyfit(x,y,1)
        observed=np.std(y-(intercept+slope*x),ddof=1)
        null=[]
        for _ in range(N_PERM):
            yp=rng.permutation(y)
            s,i=np.polyfit(x,yp,1)
            null.append(np.std(yp-(i+s*x),ddof=1))
        null=np.asarray(null)
        rows.append({"pair":pair,"n_raters":len(g),"observed_residual_sd":observed,"null_sd_mean":null.mean(),"null_sd_q025":np.quantile(null,.025),"null_sd_q975":np.quantile(null,.975),"p_upper":(1+np.sum(null>=observed))/(N_PERM+1)})
    out=pd.DataFrame(rows)
    out.to_csv(OUTPUT,index=False)
    print(out.to_string(index=False))
