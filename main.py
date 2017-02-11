# https://www.tutorialspoint.com/python/

from filloriginaldata import (CreateDictDevs, CreateDictPriors, CreateDictTaskTypes, CreateArrayLabourQuotas)
import copy
import utptr_classes

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

for group in taskGroups:
    group.fillAndSort(originalTasksArray, "babble")

# Создание шаблонных сценариев
scenarios = []
for group in taskGroups:
    if group.importance == "h":
        scenarios.append(utptr_classes.Scenario(group, "direct", "babble"))
        scenarios.append(utptr_classes.Scenario(group, "minus1", "babble"))
        scenarios.append(utptr_classes.Scenario(group, "minus1+shuffle", "babble"))
        scenarios.append(utptr_classes.Scenario(group, "shuffle", "babble"))
    if group.importance == "n":
        scenarios.append(utptr_classes.Scenario(group, "direct", "babble"))
        scenarios.append(utptr_classes.Scenario(group, "minus1+shuffle", "babble"))
        scenarios.append(utptr_classes.Scenario(group, "shuffle", "babble"))
    if group.importance == "l":
        scenarios.append(utptr_classes.Scenario(group, "direct", "babble"))
        scenarios.append(utptr_classes.Scenario(group, "shuffle", "babble"))

candId = 0  # Потом нужно будет где-то сделать приращение
cands = [utptr_classes.Candidate(candId, listLabourHoursQuotas)]

for group in taskGroups:
    if group.tasks:
        for task in group.tasks:
            cands[0].tryToPutSingleTask(task, "bubble")

# Анализируем список кандидатов и определяем диагнозы для групп
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

# Случай, если ВСЕ задачи вошли
    if (("completelyOut" not in cands[0].diagnosisForGroup.values())
        and ("partiallyIn09" not in cands[0].diagnosisForGroup.values())
        and ("partiallyIn06" not in cands[0].diagnosisForGroup.values())
        and ("partiallyIn03" not in cands[0].diagnosisForGroup.values())
        and ("partiallyIn00" not in cands[0].diagnosisForGroup.values())):
        print("Все задачи вошли")
# Нужно что-то делать в ситуации, когда ВСЕ ЗАДАЧИ ВОШЛИ

    else:
        for group in taskGroups:
            if taskGroups.index(group) == 0:
                if cands[0].diagnosisForGroup[group] == "completelyIn":
                    candId += 1
                    cands.append(utptr_classes.Candidate(candId, listLabourHoursQuotas))
                    for task in group.tasks:
                        cands[candId].tryToPutSingleTask(task, "silent")
                elif cands[0].diagnosisForGroup[group] == "noTasksInGroup":
                    pass
                elif cands[0].diagnosisForGroup[group] == "completelyOut":
                    pass
                else:   # Если группа вошла ЧАСТИЧНО, в ней обязательно более 1 задачи
                    if group.importance == "h":
                        addedCandIdsList = []
                        for i in range(len(group.tasks)+1):
                            candId += 1
                            cands.append(utptr_classes.Candidate(candId, listLabourHoursQuotas))
                            addedCandIdsList.append(candId)
                            group.scroll("silent")
                            for task in group.tasks:
                                cands[candId].tryToPutSingleTask(task, "silent")
                        for addedCandId in reversed(addedCandIdsList):  # Избавляемся от кандидатов-дублей. По крайней мере тех, что имеют соседние id
                            if cands[addedCandId].getCheckSum() == cands[addedCandId-1].getCheckSum():
                                cands.pop(addedCandId)

# Далее нужно прописать порядок работы с НЕпервыми группами. Такие кандидаты должны наследовать задачи из кандидатов, содержащих задачи из предыдущих групп

# Нужно прописать разные альтернативные сценарии в зависимости от важности группы

            elif taskGroups.index(group) > 0:
                pass

    for cand in cands:
        cand.printCandidate()

'''
# Случай, если первые сколько-то групп вошли
    elif ("completelyIn" in cands[0].diagnosisForGroup.values()):
        tempGroupList = []
        for group in taskGroups:
            if cands[0].diagnosisForGroup[group] == "completelyIn":
                tempGroupList.append(group)
            else:
                break
        if tempGroupList:
            candId += 1
            nextCand = utptr_classes.Candidate(candId, listLabourHoursQuotas)
            for group in tempGroupList:
                for task in group.tasks:
                    nextCand.tryToPutSingleTask(task, "buuble")

# Случай, когда первые группы не вошли, нужно пробовать для них альтернативные заполнения
    else:
        for group in taskGroups:
            if len(group.tasks) == 1:
                pass
            if len(group.tasks) > 1:
                for i in len(group.tasks):
                    pass

'''

'''
    def tryToFillCands(listOfPrevFixedTasks, scenType, n):
        candId += 1
        nextCand = utptr_classes.Candidate(candId, listLabourHoursQuotas)


        pass


    for group in cands[0].diagnosisForGroup.keys():
        if (group.importance is "h") and (cands[0].diagnosisForGroup[group] == "completelyIn"):



        if (group.importance is "h") and (cands[0].diagnosisForGroup[group] != "completelyIn"):
            print("Важная группа %s, не полностью вошла" % (group.groupId))
#            tryToFillCands(listOfPrevFixedTasks, "minus1", len(group.tasks))

else:
    print("Ни одной задачи не вошло в состав-кандидат.")

'''


    # Дальше необходимо прописать действия для разных диагнозов в зависимости от важности групп. Наверное, при этом нужно вынести какие-то предшествующие действия в функции или методы, чтобы потом было проще оборачивать их в циклы
