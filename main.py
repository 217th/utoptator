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
'''
for group in taskGroups:
    group.fillAndSort(originalTasksArray, "babble")

# Первый (прямой) прогон - не в цикле

candId = 0  # Потом нужно будет где-то сделать приращение
firstCand = utptr_classes.Candidate(candId, listLabourHoursQuotas)

def tryToPutSingleTask(task, silentMode = "silent"):
    taskIsFit = [x <= y for x, y in zip(task.taskEstimates, firstCand.hoursUnused)]
    if False in taskIsFit:
        task.declineFromCand(firstCand.candId, "babble")
        if silentMode is not "silent":
            print("--- Задача %s. Есть часов: %s, надо часов: %s" % (task.taskId, firstCand.hoursUnused, task.taskEstimates))
            print("Задача %s не влезает" % task.taskId)
    else:
        if silentMode is not "silent":
            print("--- Задача %s. Есть часов: %s, надо часов: %s." % (task.taskId, firstCand.hoursUnused, task.taskEstimates))
            print("Задача %s влезает" % task.taskId)
        firstCand.hoursUnused = [y - x for x, y in zip(task.taskEstimates, firstCand.hoursUnused)]
        if silentMode is not "silent":
            print("Остаётся часов:", firstCand.hoursUnused)
        # Используем "двойную запись". Информация о включении заносится как в объект класса Task, так и в объект класса Candidate. Непонятно пока, зачем
        firstCand.acceptTask(task, "babble")
        task.acceptToCand(firstCand.candId, "babble")

for group in taskGroups:
    if group.tasks:
        for task in group.tasks:
            tryToPutSingleTask(task, "bubble")

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
            firstCand.diagnosisForGroup[group.groupId] = "noTasksInGroup"
        elif (amountIn > 0) and (amountOut == 0):
            firstCand.diagnosisForGroup[group.groupId] = "completelyIn"
        elif (amountIn == 0) and (amountOut > 0):
            firstCand.diagnosisForGroup[group.groupId] = "completelyOut"
        elif (amountIn > 0) and (amountOut > 0) and (amountIn / (amountIn + amountOut) >= 0.9):
            firstCand.diagnosisForGroup[group.groupId] = "partiallyIn09"
        elif (amountIn > 0) and (amountOut > 0) and (amountIn / (amountIn + amountOut) >= 0.6) and (amountIn / (amountIn + amountOut) < 0.9):
            firstCand.diagnosisForGroup[group.groupId] = "partiallyIn06"
        elif (amountIn > 0) and (amountOut > 0) and (amountIn / (amountIn + amountOut) >= 0.3) and (amountIn / (amountIn + amountOut) < 0.6):
            firstCand.diagnosisForGroup[group.groupId] = "partiallyIn03"
        elif (amountIn > 0) and (amountOut > 0) and (amountIn / (amountIn + amountOut) > 0) and (amountIn / (amountIn + amountOut) < 0.3):
            firstCand.diagnosisForGroup[group.groupId] = "partiallyIn00"
        print("Группа № %s. +%s -%s %s" % (group.groupId, amountIn, amountOut, firstCand.diagnosisForGroup[group.groupId]))
else:
    print("Ни одной задачи не вошло в состав-кандидат.")

# Создание шаблонных сценариев



# Дальше необходимо прописать действия для разных диагнозов в зависимости от важности групп. Наверное, при этом нужно вынести какие-то предшествующие действия в функции или методы, чтобы потом было проще оборачивать их в циклы



'''	
# Нужно будет после того, как буферный кандидат присвоится реальному кандидату, всем задачам прописать этого кандидата как содержащего/несодержащего
#    task.declineFromCand(bufferCand.candId, "babble")
#                    firstCand.acceptTask(task, "babble")
#                    task.acceptToCand(firstCand.candId, "babble")
'''
