import pandas as pd
import matplotlib.pyplot as plt
test_cols = pd.read_csv("code/data/test.csv")
test_preds = pd.read_csv("code/submissions/submission.csv")


print("Number of NaNs:", test_cols.isna().sum()[test_cols.isna().sum() != 0])

test_w_preds = pd.concat([test_cols, test_preds], axis = 1)

print(test_w_preds.head())

plt.scatter(test_w_preds["Ins_Age"], test_w_preds["Response"])
#plt.show()

