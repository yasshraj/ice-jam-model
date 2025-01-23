import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# reading the data from the CSV file into a DataFrame -----------------------------------------------------------
data = pd.read_csv("/Volumes/My Passport/shape file/merged_ice_data1_nocolum.csv")

# Split your data into independent (X) and dependent (y) variables ----------------------------------------------
X = data['discharge(cfs)']
y = data['IceFraction1']

# Reshape X to a 2D array
X = X.values.reshape(-1, 1)

# Create a linear regression model and fit the data into it
model = LinearRegression()
model.fit(X, y)

# Get the slope (m) and intercept (b) of the regression line ----------------------------------------------------
m = model.coef_[0]
b = model.intercept_

# Creating the regression equation ---------------------------------------------------------------------------------
equation = f'y = {m:f}x + {b:f}'
print(equation)

# Plotting the data and the regression line --------------------------------------------------------------------------
plt.scatter(X, y, label='Data Points')
plt.plot(X, model.predict(X), color='red', label=f'Regression Line (y = {m:f}x + {b:f})')
plt.xlabel('Water Discharge')
plt.ylabel('Ice Fraction')
plt.title('Linear Regression')
plt.legend()
plt.show()
