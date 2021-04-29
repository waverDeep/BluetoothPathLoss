import torch
import torch.nn as nn
import model
from data import data_loader
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
import numpy as np
from torch.utils.tensorboard import SummaryWriter
import tensorflow as tf
import tensorboard as tb
tf.io.gfile = tb.compat.tensorflow_stub.io.gfile


def set_tensorboard_writer(name):
    writer = SummaryWriter(name)
    return writer


def close_tensorboard_writer(writer):
    writer.close()


def close_tensorboard_writer(writer):
    writer.close()


# setup parameters
input_size = 8
num_epochs = 800
learning_rate = 1
batch_size = 1024
device = 'cuda' if torch.cuda.is_available() else 'cpu'
train_data_dir = 'dataset/pathloss_v1_train_cs.csv'
test_data_dir = 'dataset/pathloss_v1_test_cs.csv'

# load dataset
train_dataloader = data_loader.load_pathloss_dataset(train_data_dir, batch_size, True, 4)
test_dataloader = data_loader.load_pathloss_dataset(test_data_dir, batch_size, True, 4)

# load model
model = model.VanillaNetwork(input_size).cuda()

# loss and optimizer
criterion = nn.MSELoss().cuda() # cross entropy loss
# criterion = nn.L1Loss().cuda()
# optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
# optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
# optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
optimizer = torch.optim.Adadelta(model.parameters(), lr=learning_rate)

# learning rate scheduler setting
# scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer=optimizer,
#                                               lr_lambda=lambda epoch_l: epoch_l//30,
#                                               last_epoch=-1)


# setup tensorboard
writer = set_tensorboard_writer('runs/model01-vanilla-mseloss-adadelta-lr1-prelu-test01-sscaler')


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
        # scheduler.step()

        # ...학습 중 손실(running loss)을 기록하고
        writer.add_scalar('mseloss training loss',
                          loss / 1000,
                          epoch * len(train_dataloader) + i)

        if (epoch+1) % 5 == 0:
            print('Epoch [{}/{}], Loss: {:.4f}'.format(epoch + 1, num_epochs, loss.item()))

    torch.save({epoch: epoch,
                'model': model,
                'model_state_dict': model.state_dict()},
               "checkpoints/model_adadelta_mse_epoch_{}.pt".format(epoch))

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

            test_mse_score = mean_squared_error(total_label, total_pred)
            test_r2_score = r2_score(total_label, total_pred)
            test_mae_score = mean_absolute_error(total_label, total_pred)
            test_rmse_score = np.sqrt(test_mse_score)

            writer.add_scalar('MSE Score',
                              test_mse_score,
                              epoch)
            writer.add_scalar('R2 Score',
                              test_r2_score,
                              epoch)
            writer.add_scalar('MAE Score',
                              test_mae_score,
                              epoch)
            writer.add_scalar('RMSE Score',
                              test_rmse_score,
                              epoch)

            print("MSE Score : {}".format(test_mse_score)) # 평균제곱 오차가음 낮을수록 좋음
            print("R2 Score : {}".format(test_r2_score))
            print("MAE Score : {}".format(test_mae_score))

close_tensorboard_writer(writer)