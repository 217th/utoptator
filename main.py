# https://www.tutorialspoint.com/python/

from filloriginaldata import (CreateDictDevs, CreateDictPriors, CreateDictTaskTypes, CreateArrayLabourQuotas)
import copy
import random
import utptr_classes
import utptr_to_file

silentMode = "babble"  # Режим тишины. "silent" - сокращённые сообщения. "babble" - полные сообщения
dictTaskTypes = CreateDictTaskTypes()
dictPriors = CreateDictPriors()
dictDevs = CreateDictDevs(silentMode)
listLabourHoursQuotas = CreateArrayLabourQuotas(list(dictDevs.keys()), silentMode)


def сreateTasksArray(n, silentMode="silent"):
    tasksArray = []
    if n > 0:
        for i in range(n):
            task = utptr_classes.Task(dictPriors, dictTaskTypes, dictDevs, "silent")
            tasksArray.append(task)
    else:
        print('Попросили слишком мало задач. Массив задач не заполнен.')
    return (tasksArray)

originalTasksArray = сreateTasksArray(200, silentMode)

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

    def cleanCandsFromClones(silentMode="silent"):
        global cands
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
                        cands.pop(cands.index(cand))
                        break

    def fillCandWithGroup(group, basicCand, method, silentmode="silent"):
        global candId
        global cands
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
        cleanCandsFromClones("silent")

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
                    cleanCandsFromClones("silent")

    print("-----------------------До склейки-----------------------")
    for cand in cands:
        cand.printCandidate()

# ▼▼▼▼▼▼▼▼▼ Склейка в один проход, удаление всех кандидатов, заканчивающихся непоследней группой ▼▼▼▼▼▼▼▼▼▼

    candsAssembled = copy.deepcopy(cands)
    for i in range(len(taskGroups)):
        for cand in reversed(candsAssembled):
            if cand.additionalTo:
                # Приклеиваем к более позднему всё из более раннего
                # hoursUnused остаётся от позднего
                # lastGroupId остаётся от позднего
                cand.tasks.extend(cand.additionalTo.tasks)
                cand.additionalTo = cand.additionalTo.additionalTo

    candsAssembled.sort(key=lambda x: x.lastGroupId, reverse=True)
    for cand in reversed(candsAssembled):
        if cand.lastGroupId < taskGroups[-1].groupId:
            candsAssembled.pop(candsAssembled.index(cand))

# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

    print("-----------------------После склейки-----------------------")
    for cand in candsAssembled:
        cand.printCandidate()

else:
    print("Все группы задач пусты.")

'''
# Экспорт списка задач в файл
tasksList = []
for group in taskGroups:
    for task in group.tasks:
        tasksList.append([group.groupId, group.importance, task.taskId, task.taskPrior, task.taskType, task.taskEstimates, task.taskScore])
    utptr_to_file.writeTasks(tasksList)
'''