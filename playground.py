import torch
import torch.nn as nn
import model
import data_loader
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
import numpy as np


# setup parameters
input_size = 8
num_epochs = 800
learning_rate = 0.0001
batch_size = 1024
device = 'cuda' if torch.cuda.is_available() else 'cpu'
train_data_dir = 'dataset/pathloss_v1_train_ev.csv'
test_data_dir = 'dataset/pathloss_v1_test_ev.csv'
valid_data_dir = 'dataset/pathloss_v1_valid_ev.csv'

# load dataset
train_dataloader = data_loader.load_pathloss_dataset(train_data_dir, batch_size, True, 4)
test_dataloader = data_loader.load_pathloss_dataset(test_data_dir, batch_size, True, 4)
valid_dataloader = data_loader.load_pathloss_dataset(valid_data_dir, batch_size, True, 4)

# load model
model = model.VanillaNetwork(input_size).cuda()

# loss and optimizer
criterion = nn.MSELoss().cuda() # cross entropy loss
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)

# train
for epoch in range(num_epochs):
    for i, data in enumerate(train_dataloader):
        x_data, y_data = data
        x_data = x_data.cuda()
        y_data = y_data.cuda()
        y_data = y_data.unsqueeze(-1)
        pred = model(x_data)
        loss = criterion(pred, y_data)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (epoch+1) % 5 == 0:
            print('Epoch [{}/{}], Loss: {:.4f}'.format(epoch + 1, num_epochs, loss.item()))

    if (epoch+1) % 10 == 0:
        with torch.no_grad():
            total_label = []
            total_pred = []
            for i, data in enumerate(test_dataloader):
                x_data, y_data = data
                x_data = x_data.cuda()
                y_data = y_data.cuda()
                pred = model(x_data)
                pred = pred.squeeze(-1)
                rssi = x_data[:, 0]
                rssi = rssi.cpu().numpy()
                y_data = y_data.cpu().numpy()
                pred = pred.cpu().numpy()

                total_label += y_data.tolist()
                total_pred += pred.tolist()

                # plt.title("epoch : {}".format(epoch+1))
                # plt.scatter(y_data, rssi, c='b')
                # plt.scatter(pred, rssi, c='y')
                # plt.show()

            print("MSE Score : {}".format(mean_squared_error(total_label, total_pred))) # 평균제곱 오차가음 낮을수록 좋음
            print("R2 Score : {}".format(r2_score(total_label, total_pred)))