import utptr_classes
import openpyxl

fileName = 'input/input.xlsx'

def readDevs(firstRow = 4, lastRow = 28):
    devsArray = []
    wb = openpyxl.load_workbook(fileName)
    if "Разработчики" in wb.get_sheet_names():
        ws = wb.get_sheet_by_name("Разработчики")
        colDevId = ws['A']
        colDevType = ws['B']
        colDevName = ws['C']
        colDevHoursPrimary = ws['D']
        colDevHoursSecondary = ws['E']
        colDevHoursExcess = ws['F']

        devsArray = []

        for i in range(firstRow, lastRow):
            devsArray.append(utptr_classes.Dev(colDevId[i].value,
                  colDevType[i].value,
                  colDevName[i].value,
                  colDevHoursPrimary[i].value,
                  colDevHoursSecondary[i].value,
                  colDevHoursExcess[i].value))

    else:
        print("Нет листа с разработчиками")

    return devsArray