import numpy as np



def r2_score(y_true, y_pred):
    corr_matrix = np.corrcoef(y_true, y_pred)
    corr = corr_matrix[0, 1]
    return corr ** 2

class LinearRegression:

    def __init__(self, learning_rate=0.001,n_iters=1000):
        self.lr = learning_rate
        self.n_iters = n_iters
        self.weights = None
        self.bias = None

    def fit(self, X,y):
        n_samples, n_features = X.shape


        # Using init parameters
        self.weights = np.zeros(n_features)
        self.bias = 0

        # Optimization Method to improve the MSE or accuracy
        # Gradient Descent
        for _ in range(self.n_iters):
            y_predicted = np.dot(X, self.weights) + self.bias

            # Gradient Formula
            dw = (1 / n_samples) * np.dot(X.T, (y_predicted - y))
            db = (1 / n_samples) * np.sum(y_predicted - y)


            # Update parameters

            self.weights = self.lr * dw
            self.bias  = self.lr * db

    def predict(self, X):
        y_approximate = np.dot(X, self.weights)+self.bias
        return y_approximate