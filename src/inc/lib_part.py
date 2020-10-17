import esp32

class partmgr:

    def __init__(self):
        self.parts = []

    def getparts(self):
        pa = []
        if len(self.parts)<1:
           try:
            p1 = esp32.Partition.find(type=esp32.Partition.TYPE_APP)
            for p in p1:
                pa.append(p.info())
           except:
            pass
           try:
            p1 = esp32.Partition.find(type=esp32.Partition.TYPE_DATA)
            for p in p1:
                pa.append(p.info())
           except:
            pass
           self.parts = sorted(pa,key=lambda x: x[2])
        return self.parts

    def getbootpart(self):
           try:
            p1 = esp32.Partition(esp32.Partition.BOOT)
            return p1.info()
           except:
            return self.getrunningpart()
           return None

    def getrunningpart(self):
           try:
            p1 = esp32.Partition(esp32.Partition.RUNNING)
            return p1.info()
           except:
            pass
           return None

    def isotasupported(self):
        try:
            p1 = esp32.Partition(esp32.Partition.RUNNING).get_next_update()
            return p1
        except:
            pass
        return False

class OTA:

    def __init__(self):
        self.SEC_SIZE = 4096
        self.success = False
        self.part = None

    def initota(self):
        try:
         self.part = esp32.Partition(esp32.Partition.RUNNING).get_next_update()
        except:
         self.part = None
        if self.part is not None and self.part:
         self.success = True
        else:
         self.success = False

    def writedata(self,blocknum,buffer): #align buffer to SEC_SIZE
        if self.success:
         try:
          self.part.writeblocks(blocknum,buffer)
         except Exception as e:
          self.success = False
        return self.success

    def endota(self):
        if self.success:
         try:
          self.part.set_boot()
         except:
          self.success = False
        return self.success

