class myClass():
    def myfunc1(self,a, b, c, d):
        return a + b + c + d

    def myfunc2(self,a, b):
        return a + b

def runAlgo(*algo):
    for i in algo:
        if i is 10:
            print "Success"
        else :
            print "Fail"


if __name__ == "__main__":
    algo = myClass()
    r = algo.myfunc1(1,2,3,4)
    s = algo.myfunc2(1,2)

    runAlgo(r,s)
