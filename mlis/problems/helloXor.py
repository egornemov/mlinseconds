# HelloXor is a HelloWorld of Machine Learning.
import time
import random
import torch
import torchvision
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
sys.path.append('./../utils')
import solutionmanager as sm
from gridsearch import GridSearch

class SolutionModel(nn.Module):
    def __init__(self, input_size, output_size, hidden_size):
        super(SolutionModel, self).__init__()
        self.input_size = input_size
        sm.SolutionManager.print_hint("Hint[1]: Xor can not be learned with only one layer")
        self.hidden_size = hidden_size
        self.linear = nn.Linear(input_size, self.hidden_size)
        self.bilinear = nn.Bilinear(self.hidden_size, self.hidden_size, output_size)

    def forward(self, x):
        x1 = self.linear(x)
        x2 = F.sigmoid(x1)
        x3 = self.bilinear(x1, x2)
        x4 = F.sigmoid(x3)
        return x4

class Solution():
    def __init__(self):
        self.lr = 2
        self.lr_grid = [0.1, 1.0, 2, 3, 5, 8]
        self.hidden_size = 5
        self.hidden_size_grid = [2, 3, 5, 10]
        self.grid_search = GridSearch(self).set_enabled(False)

    def create_model(self, input_size, output_size):
        return SolutionModel(input_size, output_size, self.hidden_size)

    # Return number of steps used
    def train_model(self, model, train_data, train_target, context):
        step = 0
        # Put model in train mode
        model.train()
        while True:
            time_left = context.get_timer().get_time_left()
            # No more time left, stop training
            if time_left < 0.1:
                break
            sm.SolutionManager.print_hint("Hint[2]: Learning rate is too small", step)
            optimizer = optim.SGD(model.parameters(), lr=self.lr)
            data = train_data
            target = train_target
            # model.parameters()...gradient set to zero
            optimizer.zero_grad()
            # evaluate model => model.forward(data)
            output = model(data)
            # if x < 0.5 predict 0 else predict 1
            predict = output.round()
            # Number of correct predictions
            correct = predict.eq(target.view_as(predict)).long().sum().item()
            # Total number of needed predictions
            total = target.view(-1).size(0)
            if correct == total:
                break
            # calculate loss
            loss = ((output-target)**2).sum()
            self.grid_search.log_step_value('loss', loss.item(), step)
            # calculate deriviative of model.forward() and put it in model.parameters()...gradient
            loss.backward()
            # print progress of the learning
            self.print_stats(step, loss, correct, total)
            # update model: model.parameters() -= lr * gradient
            optimizer.step()
            step += 1
        return step

    def print_stats(self, step, loss, correct, total):
        if step % 1000 == 0:
            print("Step = {} Prediction = {}/{} Error = {}".format(step, correct, total, loss.item()))

###
###
### Don't change code after this line
###
###
class Limits:
    def __init__(self):
        self.time_limit = 2.0
        self.size_limit = 100
        self.test_limit = 1.0

class DataProvider:
    def __init__(self):
        self.number_of_cases = 10

    def create_data(self):
        data = torch.FloatTensor([
            [0.0, 0.0],
            [0.0, 1.0],
            [1.0, 0.0],
            [1.0, 1.0]
            ])
        target = torch.FloatTensor([
            [0.0],
            [1.0],
            [1.0],
            [0.0]
            ])
        return (data, target)

    def create_case_data(self, case):
        data, target = self.create_data()
        return sm.CaseData(case, Limits(), (data, target), (data, target))

class Config:
    def __init__(self):
        self.max_samples = 1000

    def get_data_provider(self):
        return DataProvider()

    def get_solution(self):
        return Solution()

# If you want to run specific case, put number here
sm.SolutionManager(Config()).run(case_number=-1)
