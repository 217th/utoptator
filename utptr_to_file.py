'''
# aqua 0x31
# black 0x08
# blue 0x0C
# blue_gray 0x36
# bright_green 0x0B
# brown 0x3C
# coral 0x1D
# cyan_ega 0x0F
# dark_blue 0x12
# dark_blue_ega 0x12
# dark_green 0x3A
# dark_green_ega 0x11
# dark_purple 0x1C
# dark_red 0x10
# dark_red_ega 0x10
# dark_teal 0x38
# dark_yellow 0x13
# gold 0x33
# gray_ega 0x17
# gray25 0x16
# gray40 0x37
# gray50 0x17
# gray80 0x3F
# green 0x11
# ice_blue 0x1F
# indigo 0x3E
# ivory 0x1A
# lavender 0x2E
# light_blue 0x30
# light_green 0x2A
# light_orange 0x34
# light_turquoise 0x29
# light_yellow 0x2B
# lime 0x32
# magenta_ega 0x0E
# ocean_blue 0x1E
# olive_ega 0x13
# olive_green 0x3B
# orange 0x35
# pale_blue 0x2C
# periwinkle 0x18
# pink 0x0E
# plum 0x3D
# purple_ega 0x14
# red 0x0A
# rose 0x2D
# sea_green 0x39
# silver_ega 0x16
# sky_blue 0x28
# tan 0x2F
# teal 0x15
# teal_ega 0x15
# turquoise 0x0F
# violet 0x14
# white 0x09
# yellow 0x0D
'''


import xlwt
import time


def writeReportToXLS(
        settings,
        allTasks,
        rels,
        rawCandsList,
        rawCandsOnlyActiveList,
        rawCandsTasksList,
        finalCandsList,
        finalCandsTasksList,
        finalRelsList):

    wb = xlwt.Workbook()
    styleYellow = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
    styleRed = xlwt.easyxf('pattern: pattern solid, fore_colour red;')
    styleOrange = xlwt.easyxf('pattern: pattern solid, fore_colour orange;')
    styleAqua = xlwt.easyxf('pattern: pattern solid, fore_colour aqua;')

    ws = wb.add_sheet('settings', cell_overwrite_ok = True)
    ws.write(0, 0, "primaryHoursAvailable:")
    ws.write(0, 1, str([x.hoursPrimary for x in settings[0]]))
    ws.write(1, 0, "secondaryHoursAvailable:")
    ws.write(1, 1, str([x.hoursSecondary for x in settings[0]]))
    ws.write(2, 0, "extraHoursAvailable:")
    ws.write(2, 1, str([x.hoursExcess for x in settings[0]]))

    ws = wb.add_sheet('allTasks', cell_overwrite_ok = True)
    header = ["groupId",
              "groupImportance",
              "taskId",
              "taskPrior",
              "taskType",
              "taskEstimates",
              "taskScore",
              "primIsMandatory",
              "secIsPreferred",
              "relConcurrent",
              "relAlternative",
              "relSequent"]
    for i in range(len(header)):
        ws.write(0, i, header[i], styleOrange)
    for i in range(len(allTasks)):
        for j in range(len(allTasks[i])):
            ws.write(i+1, j, str(allTasks[i][j]))

    ws = wb.add_sheet('rels', cell_overwrite_ok = True)
    header = ["type",
                     "subjectTaskId",
                     "subjectTaskGroupId",
                     "assocTaskId"]
    for i in range(len(header)):
        ws.write(0, i, header[i], styleOrange)
    for i in range(len(rels)):
        for j in range(len(rels[i])):
            ws.write(i+1, j, str(rels[i][j]))

    ws = wb.add_sheet('rawCands', cell_overwrite_ok = True)
    for cand in rawCandsList:
        ws.write(cand[1], cand[2] * 8, str(cand[0]))
        if len(cand) > 7:
            ws.write(cand[1], cand[2] * 8 + 1, str(cand[1]), styleYellow)
        else:
            ws.write(cand[1], cand[2] * 8 + 1, str(cand[1]), styleRed)
        ws.write(cand[1], cand[2]*8+2, str(cand[2]))
        ws.write(cand[1], cand[2]*8+3, str(cand[3]))
        ws.write(cand[1], cand[2]*8+4, str(cand[4]))
        ws.write(cand[1], cand[2]*8+5, str(cand[5]))
        ws.write(cand[1], cand[2]*8+6, cand[6])
        if len(cand) > 7:
            ws.write(cand[1], cand[2] * 8 + 7, cand[7])

    ws = wb.add_sheet('rawCandsActive', cell_overwrite_ok = True)
    rawCandsOnlyActiveList.sort(key=lambda x: x[0], reverse=False)
    header = ["additionalTo",
              "candId",
              "lastGroupId",
              "checkSum",
              "numberOfTasks",
              "hoursUnused",
              "method"]
    for i in range(len(header)):
        ws.write(0, i, header[i], styleOrange)
    for i in range(len(rawCandsOnlyActiveList)):
        for j in range(len(rawCandsOnlyActiveList[i])):
            ws.write(i+1, j, str(rawCandsOnlyActiveList[i][j]))

    ws = wb.add_sheet('rawCandsTasks', cell_overwrite_ok = True)
    header = ["candId",
              "groupId",
              "taskId",
              "taskPrior",
              "taskType",
              "taskEstimates",
              "taskScore",
              "relConcurrent",
              "relAlternative",
              "relSequent"]
    for i in range(len(header)):
        ws.write(0, i, header[i], styleOrange)
    for i in range(len(rawCandsTasksList)):
        for j in range(len(rawCandsTasksList[i])):
            if (rawCandsTasksList[i][0] % 2 == 0):
                ws.write(i+1, j, str(rawCandsTasksList[i][j]))
            else:
                ws.write(i+1, j, str(rawCandsTasksList[i][j]), styleAqua)

    ws = wb.add_sheet('finalCands', cell_overwrite_ok = True)
    header = ["candId",
                     "len(tasks)",
                     "candScore",
                     "hoursUnused",
                     "checkSum"]
    for i in range(len(header)):
        ws.write(0, i, header[i], styleOrange)
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
            ws.write(6, i, header[i], styleOrange)

        for i in range(len(cand)):
            ws.write(i+7, 0, str(cand[i][5]))
            ws.write(i+7, 1, str(cand[i][6]))
            ws.write(i+7, 2, str(cand[i][7]))
            ws.write(i+7, 3, str(cand[i][8]))
            ws.write(i+7, 4, str(cand[i][9]))
            ws.write(i+7, 5, str(cand[i][10]))
            ws.write(i+7, 6, str(cand[i][11]))
            ws.write(i+7, 7, str(cand[i][12]))

        header = ["relType",
                "subjTaskId",
                "assocTaskId",
                "isActive"
              ]
        for i in range(len(header)):
            ws.write(6, 9+i, header[i], styleOrange)

        finalRelsForCand = [x for x in finalRelsList if x[0] == cand[0][0]]
        for i in range(len(finalRelsForCand)):
            ws.write(i+7, 9, str(finalRelsForCand[i][1]))
            ws.write(i+7, 10, str(finalRelsForCand[i][2]))
            ws.write(i+7, 11, str(finalRelsForCand[i][3]))
            ws.write(i+7, 12, str(finalRelsForCand[i][4]))

    wb.save("results/try." + time.strftime("%Y.%m.%d.%H.%M.%S", time.localtime()) + ".xls")


def writeDebugData1ToXLS(rels, neatConcurrentTaskGroups, clearConcurrentTaskGroups, relsOverall):
    #   Функция для вывода отладочных данных
    #   1 - выводим промежуточный результат создания межзадачных связей relConcurrent

    wb = xlwt.Workbook()
    styleYellow = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
    styleRed = xlwt.easyxf('pattern: pattern solid, fore_colour red;')
    styleOrange = xlwt.easyxf('pattern: pattern solid, fore_colour orange;')
    styleAqua = xlwt.easyxf('pattern: pattern solid, fore_colour aqua;')

    if rels:
        ws = wb.add_sheet('rels', cell_overwrite_ok = True)
        header = ["type",
                         "subjectTaskId",
                         "subjectTaskGroupId",
                         "assocTaskId"]
        for i in range(len(header)):
            ws.write(0, i, header[i], styleOrange)
        for i in range(len(rels)):
            ws.write(i + 1, 0, str(rels[i].relType))
            ws.write(i + 1, 1, str(rels[i].subjTaskId))
            ws.write(i + 1, 2, str(rels[i].subjTaskGroupId))
            ws.write(i + 1, 3, str(rels[i].assocTaskId))

        ws = wb.add_sheet('neatGroups', cell_overwrite_ok = True)
        for i in range(len(neatConcurrentTaskGroups)):
            for j in range(len(neatConcurrentTaskGroups[i])):
                ws.write(i, j, str(neatConcurrentTaskGroups[i][j]))

        ws = wb.add_sheet('clearGroups', cell_overwrite_ok = True)
        for i in range(len(clearConcurrentTaskGroups)):
            for j in range(len(clearConcurrentTaskGroups[i])):
                ws.write(i, j, str(clearConcurrentTaskGroups[i][j]))

        ws = wb.add_sheet('relsOverall', cell_overwrite_ok = True)
        header = ["type",
                         "subjectTaskId",
                         "subjectTaskGroupId",
                         "assocTaskId"]
        for i in range(len(header)):
            ws.write(0, i, header[i], styleOrange)
        for i in range(len(relsOverall)):
            ws.write(i + 1, 0, str(relsOverall[i].relType))
            ws.write(i + 1, 1, str(relsOverall[i].subjTaskId))
            ws.write(i + 1, 2, str(relsOverall[i].subjTaskGroupId))
            ws.write(i + 1, 3, str(relsOverall[i].assocTaskId))

        wb.save("results/dbg1." + time.strftime("%Y.%m.%d.%H.%M.%S", time.localtime()) + ".xls")


def writeDebugData2ToXLS(rels, neatSequentTaskGroups, clearSequentTaskGroups, relsOverall):
    #   Функция для вывода отладочных данных
    #   2 - выводим промежуточный результат создания межзадачных связей relSequent

    wb = xlwt.Workbook()
    styleYellow = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
    styleRed = xlwt.easyxf('pattern: pattern solid, fore_colour red;')
    styleOrange = xlwt.easyxf('pattern: pattern solid, fore_colour orange;')
    styleAqua = xlwt.easyxf('pattern: pattern solid, fore_colour aqua;')

    if rels:
        ws = wb.add_sheet('rels', cell_overwrite_ok = True)
        header = ["type",
                         "subjectTaskId",
                         "subjectTaskGroupId",
                         "assocTaskId"]
        for i in range(len(header)):
            ws.write(0, i, header[i], styleOrange)
        for i in range(len(rels)):
            ws.write(i + 1, 0, str(rels[i].relType))
            ws.write(i + 1, 1, str(rels[i].subjTaskId))
            ws.write(i + 1, 2, str(rels[i].subjTaskGroupId))
            ws.write(i + 1, 3, str(rels[i].assocTaskId))

        if neatSequentTaskGroups:
            ws = wb.add_sheet('neatGroups', cell_overwrite_ok = True)
            for i in range(len(neatSequentTaskGroups)):
                for j in range(len(neatSequentTaskGroups[i])):
                    ws.write(i, j, str(neatSequentTaskGroups[i][j]))

        if clearSequentTaskGroups:
            ws = wb.add_sheet('clearGroups', cell_overwrite_ok = True)
            for i in range(len(clearSequentTaskGroups)):
                for j in range(len(clearSequentTaskGroups[i])):
                    ws.write(i, j, str(clearSequentTaskGroups[i][j]))

        if relsOverall:
            ws = wb.add_sheet('relsOverall', cell_overwrite_ok = True)
            header = ["type",
                             "subjectTaskId",
                             "subjectTaskGroupId",
                             "assocTaskId"]
            for i in range(len(header)):
                ws.write(0, i, header[i], styleOrange)
            for i in range(len(relsOverall)):
                ws.write(i + 1, 0, str(relsOverall[i].relType))
                ws.write(i + 1, 1, str(relsOverall[i].subjTaskId))
                ws.write(i + 1, 2, str(relsOverall[i].subjTaskGroupId))
                ws.write(i + 1, 3, str(relsOverall[i].assocTaskId))

        wb.save("results/dbg2." + time.strftime("%Y.%m.%d.%H.%M.%S", time.localtime()) + ".xls")