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


originalTasksArray = CreateTasksArray(20, silentMode)

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
firstCand = utptr_classes.Candidate(candId, listLabourHoursQuotas)

for group in taskGroups:
    if group.tasks:
        for task in group.tasks:
            firstCand.tryToPutSingleTask(task, "bubble")

# Анализируем список кандидатов и определяем диагнозы для групп
if firstCand.tasks:
    firstCand.printCandidate()
    print("------------------------------")
    for group in taskGroups:
        amountIn = 0
        amountOut = 0
        for task in originalTasksArray:
            if (task.taskType in group.meta[0]) and (task.taskPrior in group.meta[1]) and (
                        firstCand.candId in task.candsTaskIncluded):
                amountIn += 1
            elif (task.taskType in group.meta[0]) and (task.taskPrior in group.meta[1]) and (
                        firstCand.candId in task.candsTaskExcluded):
                amountOut += 1
        if (amountIn == 0) and (amountOut == 0):
            firstCand.diagnosisForGroup[group] = "noTasksInGroup"
        elif (amountIn > 0) and (amountOut == 0):
            firstCand.diagnosisForGroup[group] = "completelyIn"
        elif (amountIn == 0) and (amountOut > 0):
            firstCand.diagnosisForGroup[group] = "completelyOut"
        elif (amountIn > 0) and (amountOut > 0) and (amountIn / (amountIn + amountOut) >= 0.9):
            firstCand.diagnosisForGroup[group] = "partiallyIn09"
        elif (amountIn > 0) and (amountOut > 0) and (amountIn / (amountIn + amountOut) >= 0.6) and (
                amountIn / (amountIn + amountOut) < 0.9):
            firstCand.diagnosisForGroup[group] = "partiallyIn06"
        elif (amountIn > 0) and (amountOut > 0) and (amountIn / (amountIn + amountOut) >= 0.3) and (
                amountIn / (amountIn + amountOut) < 0.6):
            firstCand.diagnosisForGroup[group] = "partiallyIn03"
        elif (amountIn > 0) and (amountOut > 0) and (amountIn / (amountIn + amountOut) > 0) and (
                amountIn / (amountIn + amountOut) < 0.3):
            firstCand.diagnosisForGroup[group] = "partiallyIn00"
        print("Группа № %s %s. +%s -%s %s" % (group.groupId, group.importance, amountIn, amountOut, firstCand.diagnosisForGroup[group]))

# Случай, если ВСЕ задачи вошли
    if (("completelyOut" not in firstCand.diagnosisForGroup.values())
        and ("partiallyIn09" not in firstCand.diagnosisForGroup.values())
        and ("partiallyIn06" not in firstCand.diagnosisForGroup.values())
        and ("partiallyIn03" not in firstCand.diagnosisForGroup.values())
        and ("partiallyIn00" not in firstCand.diagnosisForGroup.values())):
        print("Все задачи вошли")
# Нужно что-то делать в ситуации, когда ВСЕ ЗАДАЧИ ВОШЛИ

# Случай, если первые сколько-то групп вошли
    elif ("completelyIn" in firstCand.diagnosisForGroup.values()):
        tempGroupList = []
        for group in taskGroups:
            if firstCand.diagnosisForGroup[group] == "completelyIn":
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
        pass










'''
    def tryToFillCands(listOfPrevFixedTasks, scenType, n):
        candId += 1
        nextCand = utptr_classes.Candidate(candId, listLabourHoursQuotas)


        pass


    for group in firstCand.diagnosisForGroup.keys():
        if (group.importance is "h") and (firstCand.diagnosisForGroup[group] == "completelyIn"):



        if (group.importance is "h") and (firstCand.diagnosisForGroup[group] != "completelyIn"):
            print("Важная группа %s, не полностью вошла" % (group.groupId))
#            tryToFillCands(listOfPrevFixedTasks, "minus1", len(group.tasks))


else:
    print("Ни одной задачи не вошло в состав-кандидат.")

'''



    # Дальше необходимо прописать действия для разных диагнозов в зависимости от важности групп. Наверное, при этом нужно вынести какие-то предшествующие действия в функции или методы, чтобы потом было проще оборачивать их в циклы
