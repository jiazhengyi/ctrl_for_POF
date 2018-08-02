#coding:utf-8


from pox.core import core
from pox.lib.revent import *


class my_event (EventMixin):

	def __init__(self):
		core.openflow.addListeners(self)
	
	def _handle_ConnectionUp(self, event):
		print ("connection is up !!!!!!!!!!!\n")



def launch():
	print ("in my event!\n")
	core.register("jia_test", my_event())
