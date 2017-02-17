import csv
import xlwt
import time

def writeReportToXLS(settings, allTasks, rawCandsList, finalCandsList, finalCandsTasksList):
    wb = xlwt.Workbook()
    styleY = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
    styleR = xlwt.easyxf('pattern: pattern solid, fore_colour red;')

    ws = wb.add_sheet('settings', cell_overwrite_ok = True)
    ws.write(0, 0, "hoursAvailable:")
    ws.write(0, 1, str(settings[0]))

    ws = wb.add_sheet('allTasks', cell_overwrite_ok = True)
    header = ["groupId",
                     "groupImportance",
                     "taskId",
                     "taskPrior",
                     "taskType",
                     "taskEstimates",
                     "taskScore",
                     "relConcurrent",
                     "relAlternative",
                     "relSequent"]
    for i in range(len(header)):
        ws.write(0, i, header[i])
    for i in range(len(allTasks)):
        for j in range(len(allTasks[i])):
            ws.write(i+1, j, str(allTasks[i][j]))

    ws = wb.add_sheet('rawCands', cell_overwrite_ok = True)
    for cand in rawCandsList:
        ws.write(cand[1], cand[2] * 8, str(cand[0]))
        if len(cand) > 7:
            ws.write(cand[1], cand[2]*8+1, str(cand[1]), styleY)
        else:
            ws.write(cand[1], cand[2]*8+1, str(cand[1]), styleR)
        ws.write(cand[1], cand[2]*8+2, str(cand[2]))
        ws.write(cand[1], cand[2]*8+3, str(cand[3]))
        ws.write(cand[1], cand[2]*8+4, str(cand[4]))
        ws.write(cand[1], cand[2]*8+5, str(cand[5]))
        ws.write(cand[1], cand[2]*8+6, cand[6])
        if len(cand) > 7:
            ws.write(cand[1], cand[2] * 8 + 7, cand[7])

    ws = wb.add_sheet('finalCands', cell_overwrite_ok = True)
    header = ["candId",
                     "len(tasks)",
                     "candScore",
                     "hoursUnused",
                     "checkSum"]
    for i in range(len(header)):
        ws.write(0, i, header[i])
    for i in range(len(finalCandsList)):
        for j in range(len(finalCandsList[i])):
            ws.write(i+1, j, str(finalCandsList[i][j]))

    for cand in finalCandsTasksList:
        ws = wb.add_sheet('cand'+str(cand[0][0]), cell_overwrite_ok=True)

        # Метаданные конкретного кандидата
        ws.write(0, 0, "candId:")
        ws.write(0, 1, str(cand[0][0]))
        ws.write(1, 0, "len(tasks):")
        ws.write(1, 1, str(cand[0][1]))
        ws.write(2, 0, "score:")
        ws.write(2, 1, str(cand[0][2]))
        ws.write(3, 0, "hoursUnused:")
        ws.write(3, 1, str(cand[0][3]))
        ws.write(4, 0, "checkSum:")
        ws.write(4, 1, str(cand[0][4]))

        header = ["taskId",
                "taskPrior",
                "taskType",
                "taskEstimates",
                "taskScore",
                "relConcurrent",
                "relAlternative",
                "relSequent"
              ]
        for i in range(len(header)):
            ws.write(6, i, header[i])

        for i in range(len(cand)):
            ws.write(i+7, 0, str(cand[i][5]))
            ws.write(i+7, 1, str(cand[i][6]))
            ws.write(i+7, 2, str(cand[i][7]))
            ws.write(i+7, 3, str(cand[i][8]))
            ws.write(i+7, 4, str(cand[i][9]))
            ws.write(i+7, 5, str(cand[i][10]))
            ws.write(i+7, 6, str(cand[i][11]))
            ws.write(i+7, 7, str(cand[i][12]))

    wb.save("results/try." + time.strftime("%Y.%m.%d.%H.%M.%S", time.localtime()) + ".xls")