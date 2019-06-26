class BBox:
    north = None
    south = None
    west = None
    east = None
    

class Africa(BBox):
    north = 38
    south = -41
    west = -18
    east = 56
    
    
class Monrovia(BBox):    
    north = 6.5
    south = 6.2
    west = -10.9
    east = -10.6
    
    
class Puerto_Rico(BBox):
    north = 18.6
    south = 17.8
    west = -67.3
    east = -65
    

bbox = {}
bbox['africa'] = Africa()
bbox['monrovia'] = Monrovia()
bbox['puerto_rico'] = Puerto_Rico()
