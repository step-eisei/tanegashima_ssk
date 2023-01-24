import distance_class
import time

while(True):
    distance=distance_class.Distance(17,12)
    distance.reading()
    print(distance.distance)
    time.sleep(1)
