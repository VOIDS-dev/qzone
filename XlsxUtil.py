import openpyxl
import pandas as pd
from bleach._vendor.html5lib.constants import entities

# projectId(int), sourceUrl(string[]), projectName(string), creationTime(datetime), owner(staff.qqid), staffs({[role: string]: staff.qqid[]), priority(0-3)
# , severity(0-3), ETA(datetime), status(new, active, complete, close)
WORKSHEET_BOOKING = "总表"
# qqid(int), name(string), nickname(string), skillset, role, timezone, description, oshi
WORKSHEET_MEMBER = "成员表"

XLSX_FILENAME = "英翻菜单.xlsx"

class BookingEntity():    
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
    
    def dict(self):
        return self.__dict__
    
    def toDto(self):
        return BookingDto(projectId=self.projectId.value, sourceUrl= self.sourceUrl.value, projectName=self.projectName.value, creationTime=self.creationTime.value
                          , owner=self.owner.value, staffs=self.staffs.value, priority=self.priority.value, severity=self.severity.value
                          , ETA=self.ETA.value, status=self.status.value)
        
class BookingDto():    
    def __init__(self, projectId="", sourceUrl="", projectName="", creationTime=""
                  , owner="", staffs="", priority="", severity="", ETA="", status=""):
        
        self.projectId = projectId
        self.sourceUrl = sourceUrl
        self.projectName = projectName
        self.creationTime = creationTime
        self.owner = owner
        self.staffs = staffs
        self.priority = priority
        self.severity = severity
        self.ETA = ETA
        self.status = status
    
    def dict(self):
        return self.__dict__
        
    def printEntity(self):
        print(self.projectId.value, self.sourceUrl.value, self.projectName.value, self.creationTime.value, self.owner.value
              , self.staffs.value, self.priority.value, self.severity.value, self.ETA.value, self.status.value)
        
class MemberEntity():
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        
    def dict(self):
        return self.__dict__

class MemberDto():
    def __init__(self, qqid="", name="", nickname="", skillset="", role=""
                 , timezone="", description="", oshi=""):
        
        self.qqid = qqid
        self.name = name
        self.nickname = nickname
        self.skillset = skillset
        self.role = role
        self.timezone = timezone
        self.description = description
        self.oshi = oshi

    def dict(self):
        return self.__dict__


class XlsxUtil:
    def __init__(self):
         self.wb = openpyxl.load_workbook(XLSX_FILENAME)
         self.bookingWs = self.wb[WORKSHEET_BOOKING]
         self.memberWs = self.wb[WORKSHEET_MEMBER]
    
    def loadBookingSheet(self):       
        ws = self.bookingWs
        i = 0
        entities = []
        for row in ws.rows:
            if i == 0:
                i+=1
                continue
            else:
                entity =  BookingEntity(projectId=row[0], sourceUrl=row[1], projectName=row[2], creationTime=row[3]
                                        , owner=row[4], staffs=row[5], priority=row[6], severity=row[7], ETA=row[8], status=row[9])
                entities.append(entity)
        
        return entities
    def insertBookingSheet(self, dto, numRow):
        insertTo(dto, numRow, self.bookingWs)
        return self.loadBookingSheet()
    
    def loadMemberSheet(self):       
        ws = self.memberWs
        i = 0
        entities = []
        for row in ws.rows:
            if i == 0:
                i+=1
                continue
            else:
                entity =  MemberEntity(qqid=row[0], name=row[1], nickname=row[2], skillset=row[3], role=row[4]
                                       , timezone=row[5], description=row[6], oshi=row[7])
                entities.append(entity)
        
        return entities
    
    def insertMemberSheet(self, dto, numRow):
        insertTo(dto, numRow, self.memberWs)
        return self.loadMemberSheet()
    
    def insertTo(self, dto, numRow, sheet):
        dict = dto.dict()
        numCol = 0
        for key,value in dict:
            sheet.cell(col=numCol,row=numRow,value=value)
            numCol += 1
        
    
    def save(self):
        self.wb.save(XLSX_FILENAME)

xlsxUtil = XlsxUtil() 
print(xlsxUtil.loadBookingSheet()[0].__dict__)
print(BookingDto().dict())