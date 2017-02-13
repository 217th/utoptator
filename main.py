# https://www.tutorialspoint.com/python/

from filloriginaldata import (CreateDictDevs, CreateDictPriors, CreateDictTaskTypes, CreateArrayLabourQuotas)
import copy
import random
import utptr_classes
import utptr_to_file
import time

silentMode = "babble"  # Режим тишины. "silent" - сокращённые сообщения. "babble" - полные сообщения
dictTaskTypes = CreateDictTaskTypes()
dictPriors = CreateDictPriors()
dictDevs = CreateDictDevs(silentMode)
listLabourHoursQuotas = CreateArrayLabourQuotas(list(dictDevs.keys()), silentMode)


def CreateTasksArray(n, silentMode="silent"):
    tasksArray = []
    if n > 0:
        for i in range(n):
            task = utptr_classes.Task(dictPriors, dictTaskTypes, dictDevs, "silent")
            tasksArray.append(task)
    else:
        print('Попросили слишком мало задач. Массив задач не заполнен.')
    return (tasksArray)

originalTasksArray = CreateTasksArray(100, silentMode)

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

tasksList = []
for group in taskGroups:
    for task in group.tasks:
        tasksList.append([group.groupId, group.importance, task.taskId, task.taskPrior, task.taskType, task.taskEstimates, task.taskScore])
    utptr_to_file.writeTasks(tasksList)

candId = 0  # Потом нужно будет где-то сделать приращение
cands = [utptr_classes.Candidate(candId, listLabourHoursQuotas, False, "silent")]

for group in taskGroups:
    if group.tasks:
        for task in group.tasks:
            cands[0].tryToPutSingleTask(task, group.groupId, "silent")
        cands[0].isComplete = True

# Анализируем нулевой список кандидатов и определяем диагнозы для групп
if cands[0].tasks:
    for group in taskGroups:
        amountIn = 0
        amountOut = 0
        for task in originalTasksArray:
            if (task.taskType in group.meta[0]) and (task.taskPrior in group.meta[1]) and (
                        cands[0].candId in task.candsTaskIncluded):
                amountIn += 1
            elif (task.taskType in group.meta[0]) and (task.taskPrior in group.meta[1]) and (
                        cands[0].candId in task.candsTaskExcluded):
                amountOut += 1
        if (amountIn == 0) and (amountOut == 0):
            cands[0].diagnosisForGroup[group] = "noTasksInGroup"
        elif (amountIn > 0) and (amountOut == 0):
            cands[0].diagnosisForGroup[group] = "completelyIn"
        elif (amountIn == 0) and (amountOut > 0):
            cands[0].diagnosisForGroup[group] = "completelyOut"
        elif (amountIn > 0) and (amountOut > 0) and (amountIn / (amountIn + amountOut) >= 0.9):
            cands[0].diagnosisForGroup[group] = "partiallyIn09"
        elif (amountIn > 0) and (amountOut > 0) and (amountIn / (amountIn + amountOut) >= 0.6) and (
                amountIn / (amountIn + amountOut) < 0.9):
            cands[0].diagnosisForGroup[group] = "partiallyIn06"
        elif (amountIn > 0) and (amountOut > 0) and (amountIn / (amountIn + amountOut) >= 0.3) and (
                amountIn / (amountIn + amountOut) < 0.6):
            cands[0].diagnosisForGroup[group] = "partiallyIn03"
        elif (amountIn > 0) and (amountOut > 0) and (amountIn / (amountIn + amountOut) > 0) and (
                amountIn / (amountIn + amountOut) < 0.3):
            cands[0].diagnosisForGroup[group] = "partiallyIn00"
        print("Группа № %s %s. +%s -%s %s" % (group.groupId, group.importance, amountIn, amountOut, cands[0].diagnosisForGroup[group]))

# Случай, если ВСЕ задачи вошли в кандидат 0
    if (("completelyOut" not in cands[0].diagnosisForGroup.values())
        and ("partiallyIn09" not in cands[0].diagnosisForGroup.values())
        and ("partiallyIn06" not in cands[0].diagnosisForGroup.values())
        and ("partiallyIn03" not in cands[0].diagnosisForGroup.values())
        and ("partiallyIn00" not in cands[0].diagnosisForGroup.values())):
        print("Все задачи вошли")
# Нужно что-то делать в ситуации, когда ВСЕ ЗАДАЧИ ВОШЛИ

# Случай, если ВСЕ задачи НЕ вошли в кандидат 0
    elif (("completelyIn" not in cands[0].diagnosisForGroup.values())
            and ("partiallyIn09" not in cands[0].diagnosisForGroup.values())
            and ("partiallyIn06" not in cands[0].diagnosisForGroup.values())
            and ("partiallyIn03" not in cands[0].diagnosisForGroup.values())
            and ("partiallyIn00" not in cands[0].diagnosisForGroup.values())):
            print("Все задачи НЕ вошли")
# Нужно что-то делать в ситуации, когда ВСЕ ЗАДАЧИ НЕ ВОШЛИ

    else:

        def cleanCandsFromClones():
            for cand in reversed(cands):
                if cands.index(cand) > 0:
                    for candPrev in cands[0: cands.index(cand)]:
                        if (cand.checkSum == candPrev.checkSum) and (cand.lastGroupId == candPrev.lastGroupId):
                            print("Дубли | id %s, checkSum %s, lastGroup %s | id %s, checkSum %s, lastGroup %s" % (cand.candId, cand.checkSum, cand.lastGroupId, candPrev.candId, candPrev.checkSum,candPrev.lastGroupId))
                            cands.pop(cands.index(cand))
                            break

        candsForFile = []

        def fillCandWithGroup(group, basicCand, method, silentmode = "silent"):
            if group.tasks:
                global cands
                global candId
                candId += 1
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

                global candsForFile
                candsForFile.append([time.time(),
                                     cands[-1].candId,
                                     cands[-1],
                                     len(cands[-1].tasks),
                                     cands[-1].additionalTo,
                                     cands[-1].lastGroupId,
                                     cands[-1].checkSum])

            return ()

# Находим первую группу, которая вошла полностью (чтобы на ней потом строить следующие группы),
# либо частично (чтобы сделать сколько-то вариантов, а потом на них строить следуюющие группы).
# Как только найдём и заведём доп. группы, рвём цикл.
        for group in taskGroups:
            if cands[0].diagnosisForGroup[group] == "noTasksInGroup":
                pass
            elif cands[0].diagnosisForGroup[group] == "completelyOut":
                pass
            elif cands[0].diagnosisForGroup[group] == "completelyIn":
                fillCandWithGroup(group, False, "direct")
                break
            else:  # Если группа вошла ЧАСТИЧНО, в ней обязательно более 1 задачи
                if group.importance == "h":
                    for i in range(len(group.tasks) + 1): fillCandWithGroup(group, False, "scroll")
                    for i in range(len(group.tasks) * 2): fillCandWithGroup(group, False, "shuffle")
                elif group.importance == "n":
                    for i in range(len(group.tasks) + 1): fillCandWithGroup(group, False, "scroll")
                    for i in range(len(group.tasks) + 1): fillCandWithGroup(group, False, "shuffle")
                elif group.importance == "l":
                    for i in range(len(group.tasks) + 1): fillCandWithGroup(group, False, "shuffle")
                cleanCandsFromClones()
                break

        for basicCand in cands:
            if basicCand.lastGroupId < len(taskGroups)-1:
                for group in taskGroups:
                    if group.groupId == basicCand.lastGroupId+1:
                        if group.tasks:
                            if group.importance == "h":
                                fillCandWithGroup(group, basicCand, "direct")
                                for i in range(len(group.tasks) + 1): fillCandWithGroup(group, basicCand, "scroll")
                                for i in range(len(group.tasks) * 2): fillCandWithGroup(group, basicCand, "shuffle")
                            elif group.importance == "n":
                                fillCandWithGroup(group, basicCand, "direct")
                                for i in range(len(group.tasks) + 1): fillCandWithGroup(group, basicCand, "scroll")
                                for i in range(len(group.tasks) + 1): fillCandWithGroup(group, basicCand, "shuffle")
                            elif group.importance == "l":
                                fillCandWithGroup(group, basicCand, "direct")
                                for i in range(len(group.tasks) + 1): fillCandWithGroup(group, basicCand, "shuffle")
                            cleanCandsFromClones()

# Выводим список кандидатов ДО СКЛЕЙКИ
    utptr_to_file.writeCands("cands.csv", candsForFile)

    print("-----------------------До склейки-----------------------")
    for cand in cands:
        cand.printCandidate()

    print("-----------------------Цепочки-----------------------")
    chains = []
    for cand in cands:
        if cand.additionalTo == False:
            chains.append([False, cand.candId])
        else:
            chains.append([cand.additionalTo.candId, cand.candId])
    chains.sort(key=lambda x: x[1], reverse=False)
    print(chains)

'''
# Склеиваем список кандидатов
    for i in range(len(taskGroups)):
        for cand in reversed(cands):
            if cand.additionalTo:
                # Приклеиваем к более позднему всё из более раннего
                # hoursUnused остаётся от позднего
                # lastGroupId остаётся от позднего
                cand.tasks.extend(cand.additionalTo.tasks)
                cand.additionalTo = cand.additionalTo.additionalTo

    cleanCandsFromClones()

# !!!
# После склейки почему-то теряются вложенные кандидаты одной и той же группы, настроенные по-разному. Нужно исследовать.
# !!!


# Выводим список кандидатов ПОСЛЕ СКЛЕЙКИ
    print("-----------------------После склейки-----------------------")
    for cand in cands:
        cand.printCandidate()
'''








'''

else:
    print("Ни одной задачи не вошло в состав-кандидат.")

'''