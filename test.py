import numpy as np
import pandas as pd

a = pd.DataFrame(
    {
        "A": [1,2,3,4],
        "B": pd.Timestamp("20130102"),
        "C": pd.Series(1, index=list(range(4)), dtype="float32"),
        "D": np.array([3] * 4, dtype="int32"),
        "E": pd.Categorical(["test", "train", "test", "train"]),
        "F": "foo",
    }
)

print(a)
print(a[a["F"] == "foo"]["A"].sort_values(ascending=True).values[-1])