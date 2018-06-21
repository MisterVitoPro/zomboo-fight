'''
Created on 07.06.2011

@author: Anthony
'''

class Animate():
    def __init__(self):
        self.info = None
        
    
    offsets = {"north" : ((0, 0), (24, 0), (51, 0)), 
                "northWest" : ((0, 35), (26, 35), (51, 35)),
                "west" : ((0, 69), (25, 69), (52, 69)),
                "southWest" : ((0, 102), (24, 102), (47, 102)),
                "south" : ((0, 136), (24, 136), (49, 136), (75, 136))}
    
    imageSizes = {"north" : (24, 32),
                "northWest" : (24, 32),
                "west" : (26, 32),
                "southWest" : (23, 32),
                "south" : (24, 32)}
