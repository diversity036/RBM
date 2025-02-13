## Backpropagation for Neural Network ##
## Shiyu Dong
## shiyud@andrew.cmu.edu

import sys
import numpy as np
import math
import matplotlib.pyplot as plt
import time
import argparse
import random
import pickle
class AutoEncoder():

	def Initialization(self, args):

		self.NumOfv  = args.visible													# num of input
		self.NumOfh  = args.hidden													# num of hidden layer
		self.rate        = args.rate          				# learning rate
		self.NumOfEpoch  = args.epoch									# num of epoch
		self.p = args.dropout
		self.sum_error  = 0
		C = np.sqrt(6)/np.sqrt(self.NumOfv + self.NumOfh)
		self.w = np.random.uniform(-C, C, [self.NumOfh, self.NumOfv]) #w: 100*784
		self.b = np.zeros(self.NumOfh)
		self.c = np.zeros(self.NumOfv)
		
		self.train_loss = []
		self.valid_loss = []
				
	def TrainFeedForward(self, inputs):

		pre_activation_h = np.dot(self.w, inputs) + self.b 
		activation_h = self.Sigmoid(pre_activation_h) #size:100
		pre_activation_a = np.dot(self.w.transpose(), activation_h) + self.c
		activation_a = self.Sigmoid(pre_activation_a)

		return activation_h, activation_a
	
		
		
	def BackProp(self, inputs, activation_h, activation_a):
		
		delta2 =  inputs-activation_a # size: 784
		delta1 = np.dot(self.w, delta2)*activation_h*(1-activation_h) # size: 100
		self.w += np.tile(delta2, (self.NumOfh, 1))*np.tile(activation_h, (784,1)).transpose()*self.rate + np.tile(delta1, (784, 1)).transpose()*np.tile(inputs, (self.NumOfh,1))*self.rate
		self.b += delta1
		self.c += delta2



	def Train(self, train_list):
			
		sum_error = 0	
		for l in train_list:
			line = l.split(',')
			target = int(line[-1])
			del line[-1]
			
			inputs = np.array(map(float, line))
			inputs = inputs>0.5
			inputs = inputs.astype(int)
			
			mask = np.random.rand(*inputs.shape) < self.p 
			d_inputs = inputs*mask
			activation_h, activation_a = self.TrainFeedForward(d_inputs)
			error = inputs*np.log(activation_a)+(1-inputs)*np.log(1-activation_a)
			sum_error += -sum(error.transpose())
			self.BackProp(d_inputs, activation_h, activation_a)
		
		return sum_error

	
	
	def Valid(self, valid_list):
	
		sum_error = 0	
		for l in valid_list:
			line = l.split(',')
			target = int(line[-1])
			del line[-1]
			
			inputs = np.array(map(float, line))
			inputs = inputs>0.5
			inputs = inputs.astype(int)
			mask = np.random.rand(*inputs.shape) < self.p 
			d_inputs = inputs*mask
			activation_h, activation_a = self.TrainFeedForward(d_inputs)
			error = inputs*np.log(activation_a)+(1-inputs)*np.log(1-activation_a)
			sum_error += -sum(error.transpose())
			
		
		return sum_error
		

		
	def Main(self, args):
	
		self.Initialization(args)
		
		train_list = open(args.filename[0]).readlines()
		valid_list = open(args.filename[1]).readlines()
		test_list  = open(args.filename[2]).readlines()
		
		self.NumOfTrain = len(train_list)
		self.NumOfValid = len(valid_list)
		self.NumOfTest  = len(test_list)
		
		n = 1
		
		while(n <= self.NumOfEpoch):
				
			random.shuffle(train_list)
			train_error = self.Train(train_list)/self.NumOfTrain
			valid_error  = self.Valid(valid_list)/self.NumOfValid
			print "epoch--", n, "training error: ", train_error, "valid_error: ", valid_error
			self.train_loss.append(train_error)
			self.valid_loss.append(valid_error)
				
			n += 1 
			
		
		print "training finished!"
		weight = self.w
		bias = self.b
		
		f = open('ae.pickle', 'wb')
		pickle.dump(weight, f)
		pickle.dump(bias, f)


	def Sigmoid(self, z):
		a = 1/(1 + np.exp(-z))
		return a


	def Loss(self, t, a):		
		return sum(t*np.log(a))
		
		
	def Plot(self):
		t = np.arange(0, self.NumOfEpoch, 1)
		plt.plot(t, self.train_loss, 'r--', t, self.valid_loss, 'b--')
		plt.show()

		
	def PlotWeight(self):
	
		for i in range(self.NumOfh):
			fig = plt.subplot(np.ceil(np.sqrt(self.NumOfh)), np.ceil(np.sqrt(self.NumOfh)) , i)
			fig.axes.get_xaxis().set_visible(False)
			fig.axes.get_yaxis().set_visible(False)
			a = self.w[i,:]
			mina = min(a)
			maxa = max(a)
			a = 255*(a - mina)/(maxa-mina)
			fig.imshow(a.reshape(28,28), cmap='gray')
		plt.show()
				

if __name__ == "__main__":

	start_time = time.time()
	parser = argparse.ArgumentParser(description='script for testing')
	parser.add_argument('filename', nargs='+')
	parser.add_argument('--dropout', '-d', type=float, default=1, help='the dropout vallues')
	parser.add_argument('--rate', '-r', type=float, default=0.01, help='The learning rate')
	parser.add_argument('--epoch', '-e', type=int, default=50, help='the number of epoch')
	parser.add_argument('--visible', '-v', type=int, default=784, help='the number of visible units')
	parser.add_argument('--hidden', type=int, default=100, help='the number of hidden units')
	args = parser.parse_args()
	AE = AutoEncoder()
	AE.Main(args)
	AE.Plot()
	AE.PlotWeight()
	print("--- %s seconds ---" % (time.time() - start_time))

	