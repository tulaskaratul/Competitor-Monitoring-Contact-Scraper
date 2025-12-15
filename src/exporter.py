import pandas as pd

def export_csv(data, path):
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
