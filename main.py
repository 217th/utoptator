# https://www.tutorialspoint.com/python/

from filloriginaldata import (createDictDevs, createDictPriors, createDictTaskTypes, createArrayLabourQuotas)
import copy
import random
import utptr_classes
import utptr_to_file

silentMode = "babble"  # Режим тишины. "silent" - сокращённые сообщения. "babble" - полные сообщения
dictTaskTypes = createDictTaskTypes()
dictPriors = createDictPriors()
dictDevs = createDictDevs(silentMode)
listLabourHoursQuotas = createArrayLabourQuotas(list(dictDevs.keys()), silentMode)


def сreateTasksArray(n, silentMode="silent"):
    tasksArray = []
    if n > 0:
        for i in range(n):
            task = utptr_classes.Task(dictPriors, dictTaskTypes, dictDevs, "silent")
            tasksArray.append(task)
        for task in tasksArray:
            print("setRandomRelations %s %s" % (task.taskId, tasksArray.index(task)))
            task.setRandomRelations(tasksArray)
    else:
        print('Попросили слишком мало задач. Массив задач не заполнен.')
    return (tasksArray)

originalTasksArray = сreateTasksArray(100, silentMode)

taskGroups = []
i = 0

'''
for groupMeta in [     # ТЕСТОВЫЙ НАБОР МЕТАДАННЫХ
    [[2], [0], "h"], [[2], [1], "h"], [[2], [2], "n"],
    [[3, 1], [5], "l"]
    ]:
        taskGroups.append(utptr_classes.Group(i, groupMeta[0], groupMeta[1], groupMeta[2]))
        i += 1
del groupMeta
'''

for groupMeta in [  # ПРОМЫШЛЕННЫЙ НАБОР МЕТАДАННЫХ
    [[2], [0], "h"], [[2], [1], "h"], [[2], [2], "h"], [[2], [3], "n"], [[2], [4], "n"], [[2], [5], "l"],
    # Вся поддержка
    [[3], [0], "h"], [[1], [0], "h"], [[3], [1], "h"], [[1], [1], "h"], [[3], [2], "h"], [[1], [2], "h"],
    # Немедл., оч. выс., выс. - сначала ошибки, потом разработка
    [[3, 1], [3], "n"],  # Высокенький - ошибки и разработка в одной группе
    [[3, 1], [4], "n"],  # Нормальный - ошибки и разработка в одной группе
    [[3, 1], [5], "l"]  # Низкий - ошибки и разрбаботка в одной группе
    ]:
        taskGroups.append(utptr_classes.Group(i, groupMeta[0], groupMeta[1], groupMeta[2], "bubble"))
        i += 1
del groupMeta

for group in taskGroups:
    group.fillAndSort(originalTasksArray, "babble")

if any(len(x.tasks)>0 for x in taskGroups):
    candId = -1
    cands = []
    forFileRawCandMetaArray = []

    def cleanCandsFromClones(cands, silentMode="silent"):
        for cand in reversed(cands):
            if cands.index(cand) > 0:
                for candPrev in cands[0: cands.index(cand)]:
                    if (cand.checkSum == candPrev.checkSum) and\
                            (cand.lastGroupId == candPrev.lastGroupId) and\
                            (cand.additionalTo == candPrev.additionalTo):
                        if silentMode is not "silent":
                            print("Дубли | id %s, checkSum %s, lastGroup %s | id %s, checkSum %s, lastGroup %s" % (
                            cand.candId, cand.checkSum, cand.lastGroupId, candPrev.candId, candPrev.checkSum,
                            candPrev.lastGroupId))

                        for i, j in enumerate(forFileRawCandMetaArray):
                            if j[1] == cand.candId:
                                forFileRawCandMetaArray[i].append("del")

                        cands.pop(cands.index(cand))
                        break
        return(cands)

    def fillCandWithGroup(group, basicCand, method, silentmode="silent"):
        global candId
        global cands
        global forFileRawCandMetaArray
        candId += 1
        if group.tasks:
            if basicCand == False:
                cands.append(utptr_classes.Candidate(candId, listLabourHoursQuotas, False, silentmode))
            else:
                cands.append(utptr_classes.Candidate(candId, basicCand.hoursUnused, basicCand, silentmode))
            if method == "direct":
                group.tasks.sort(key=lambda x: x.taskEstimatesSum, reverse=True)
                for task in group.tasks:
                    cands[-1].tryToPutSingleTask(task, group.groupId, silentmode)
            elif method == "scroll":
                group.scroll("silent")
                for task in group.tasks:
                    cands[-1].tryToPutSingleTask(task, group.groupId, silentmode)
            elif method == "shuffle":
                random.shuffle(group.tasks)
                for task in group.tasks:
                    cands[-1].tryToPutSingleTask(task, group.groupId, silentmode)
        else:
            if basicCand == False:
                cands.append(utptr_classes.Candidate(candId, listLabourHoursQuotas, False, silentmode))
            else:
                cands.append(utptr_classes.Candidate(candId, basicCand.hoursUnused, basicCand, silentmode))
            cands[-1].lastGroupId = group.groupId

        # Формат записи: additionalTo, candId, lastGroupId, checkSum, len(tasks), hoursUnused, candScore, method, toBeDeleted
        forFileCandMeta = []
        if cands[-1].additionalTo:
            forFileAddTo = 'addTo '+str(cands[-1].additionalTo.candId)
        else:
            forFileAddTo = False
        forFileCandMeta.extend([
            forFileAddTo,
            cands[-1].candId,
            cands[-1].lastGroupId,
            round(cands[-1].checkSum, 1),
            'amnt '+str(len(cands[-1].tasks)),
            cands[-1].hoursUnused,
            method])
        forFileRawCandMetaArray.append(forFileCandMeta)

        return ()

    if len(taskGroups) > 0:
        group = taskGroups[0]
        if group.importance == "h":
            fillCandWithGroup(group, False, "direct")
            if (len(group.tasks) > len(cands[-1].tasks)):
                for i in range(len(group.tasks) + 1): fillCandWithGroup(group, False, "scroll")
                for i in range(len(group.tasks) * 2): fillCandWithGroup(group, False, "shuffle")
        elif group.importance == "n":
            fillCandWithGroup(group, False, "direct")
            if (len(group.tasks) > len(cands[-1].tasks)):
                for i in range(len(group.tasks) + 1): fillCandWithGroup(group, False, "scroll")
                for i in range(len(group.tasks) + 1): fillCandWithGroup(group, False, "shuffle")
        elif group.importance == "l":
            fillCandWithGroup(group, False, "direct")
            if (len(group.tasks) > len(cands[-1].tasks)):
                for i in range(len(group.tasks) + 1): fillCandWithGroup(group, False, "shuffle")
        cands = cleanCandsFromClones(cands, "silent")

    if len(taskGroups) > 1:
        for group in taskGroups:
            for basicCand in cands:
                if (basicCand.lastGroupId + 1 == group.groupId) and (not basicCand.isUsed):
                    if group.importance == "h":
                        fillCandWithGroup(group, basicCand, "direct")
                        if (len(group.tasks) > len(cands[-1].tasks)):
                            for i in range(len(group.tasks) + 1): fillCandWithGroup(group, basicCand, "scroll")
                            for i in range(len(group.tasks) * 2): fillCandWithGroup(group, basicCand, "shuffle")
                    elif group.importance == "n":
                        fillCandWithGroup(group, basicCand, "direct")
                        if (len(group.tasks) > len(cands[-1].tasks)):
                            for i in range(len(group.tasks) + 1): fillCandWithGroup(group, basicCand, "scroll")
                            for i in range(len(group.tasks) + 1): fillCandWithGroup(group, basicCand, "shuffle")
                    elif group.importance == "l":
                        fillCandWithGroup(group, basicCand, "direct")
                        if (len(group.tasks) > len(cands[-1].tasks)):
                            for i in range(len(group.tasks) + 1): fillCandWithGroup(group, basicCand, "shuffle")
                    basicCand.isUsed = True
                    cands = cleanCandsFromClones(cands, "silent")

# ▼▼▼▼▼▼▼▼▼ Склейка в один проход, удаление всех кандидатов, заканчивающихся непоследней группой ▼▼▼▼▼▼▼▼▼▼

    candsAssembled = copy.deepcopy(cands)
    for i in range(len(taskGroups)):
        for cand in reversed(candsAssembled):
            if cand.additionalTo:
                # Приклеиваем к более позднему всё из более раннего
                # hoursUnused остаётся от позднего
                # lastGroupId остаётся от позднего
                cand.tasks.extend(cand.additionalTo.tasks)
                cand.checkSum += cand.additionalTo.checkSum
                cand.additionalTo = cand.additionalTo.additionalTo

    candsAssembled.sort(key=lambda x: x.lastGroupId, reverse=True)
    for cand in reversed(candsAssembled):
        if cand.lastGroupId < taskGroups[-1].groupId:
            candsAssembled.pop(candsAssembled.index(cand))

# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

    print("-----------------------После склейки-----------------------")
    for cand in candsAssembled:
        cand.printCandidate()

    # Заполнение исходного списка задач для экспорта в файл
    forFileTasksList = []
    for group in taskGroups:
        for task in group.tasks:
            forFileTasksList.append([
                group.groupId,
                group.importance,
                task.taskId,
                task.taskPrior,
                task.taskType,
                task.taskEstimates,
                round(task.taskScore, 1),
                [t.taskId for t in task.relConcurrent if t is not False],
                [t.taskId for t in task.relAlternative if t is not False],
                [t.taskId for t in task.relSequent if t is not False]
            ])

    # Заполнение списка настроек попытки для экспорта в файл
    forFileTrySettings = []
    forFileTrySettings.append(listLabourHoursQuotas)

    # Заполнение массива с мета-информацией по итоговым кандидатам для экспорта в файл
    forFileFinalCandMetaArray = []
    for cand in candsAssembled:
        forFileFinalCandMetaArray.append([
            cand.candId,
            len(cand.tasks),
            round(cand.getScore(), 1),
            cand.hoursUnused,
            round(cand.checkSum, 1)])

    # Заполнение массива с подробной информацией о задачах, вошедших в финальные кандидаты, для экспорта в файл
    forFileFinalCandsTasksList = []
    for cand in candsAssembled:
        forFileSingleFinalCandTasksList = []
        for task in cand.tasks:
            forFileSingleFinalCandTasksList.append([
                cand.candId,
                len(cand.tasks),
                round(cand.getScore(), 1),
                cand.hoursUnused,
                round(cand.checkSum, 1),
                task.taskId,
                task.taskPrior,
                task.taskType,
                task.taskEstimates,
                task.taskScore,
                [t.taskId for t in task.relConcurrent if t is not False],
                [t.taskId for t in task.relAlternative if t is not False],
                [t.taskId for t in task.relSequent if t is not False]
                ])
        forFileFinalCandsTasksList.append(forFileSingleFinalCandTasksList)

    utptr_to_file.writeReportToXLS(forFileTrySettings, forFileTasksList, forFileRawCandMetaArray, forFileFinalCandMetaArray, forFileFinalCandsTasksList)
    print(forFileFinalCandsTasksList)

else:
    print("Все группы задач пусты.")

# Необходимо разбираться, почему итоговые кандидаты часто получают одинаковые, часто нулевые, контрольные суммы