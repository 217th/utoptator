# https://www.tutorialspoint.com/python/

from filloriginaldata import (CreateDictDevs, CreateDictPriors, CreateDictTaskTypes, CreateArrayLabourQuotas)
import copy
import random
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
'''
for group in taskGroups:
    group.fillAndSort(originalTasksArray, "babble")

'''
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
'''

candId = 0  # Потом нужно будет где-то сделать приращение
cands = [utptr_classes.Candidate(candId, listLabourHoursQuotas, False, "silent")]

for group in taskGroups:
    if group.tasks:
        for task in group.tasks:
            cands[0].tryToPutSingleTask(task, group.groupId, "bubble")
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
            print("---")
            for cand in reversed(cands):
                if cands.index(cand) > 0:
                    if not cand.tasks:
                        print("Пустой кандидат: %s, %s" % (cand.candId, cand.checkSum))
                        cands.pop(cands.index(cand))
                    else:
                        for candPrev in cands[0: cands.index(cand)]:
                            if cand.checkSum == candPrev.checkSum:
                                print("Кандидаты-дубли: %s, %s = %s, %s" % (cand.candId, cand.checkSum, candPrev.candId, candPrev.checkSum))
                                cands.pop(cands.index(cand))
                                break

        def fillCandWithGroup(group, basicCand, method):

            if group.tasks:
                global cands
                global candId
                candId += 1

                if method == "direct":
                    if basicCand == False:
                        cands.append(utptr_classes.Candidate(candId, listLabourHoursQuotas, False, "silent"))
                    else:
                        cands.append(utptr_classes.Candidate(candId, basicCand.hoursUnused, basicCand, "silent"))
                    group.tasks.sort(key=lambda x: x.taskEstimatesSum, reverse=True)
                    for task in group.tasks:
                        cands[-1].tryToPutSingleTask(task, group.groupId, "silent")

                elif method == "scroll":
                    if basicCand == False:
                        cands.append(utptr_classes.Candidate(candId, listLabourHoursQuotas, False, "silent"))
                    else:
                        cands.append(utptr_classes.Candidate(candId, basicCand.hoursUnused, basicCand, "silent"))
                    group.scroll("silent")
                    for task in group.tasks:
                        cands[-1].tryToPutSingleTask(task, group.groupId, "silent")

                elif method == "shuffle":
                    if basicCand == False:
                        cands.append(utptr_classes.Candidate(candId, listLabourHoursQuotas, False, "silent"))
                    else:
                        cands.append(utptr_classes.Candidate(candId, basicCand.hoursUnused, basicCand, "silent"))
                    random.shuffle(group.tasks)
                    for task in group.tasks:
                        cands[-1].tryToPutSingleTask(task, group.groupId, "silent")

            return ()

# Нужно сделать, чтобы если ни одна задача не добавлена в состав-кандидат, он удалялся.
# Может быть, вынести это в функцию очистки от дублей.


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
                group = next((x for x in taskGroups if x.groupId == basicCand.lastGroupId+1), None)
                if group.tasks:

                    if group.importance == "h":
                        candId += 1
                        cands.append(utptr_classes.Candidate(candId, basicCand.hoursUnused, basicCand, "silent"))
                        group.tasks.sort(key=lambda x: x.taskEstimatesSum, reverse=True)
                        for task in group.tasks:
                            cands[-1].tryToPutSingleTask(task, group.groupId, "silent")
                        for i in range(len(group.tasks) + 1):
                            candId += 1
                            cands.append(utptr_classes.Candidate(candId, basicCand.hoursUnused, basicCand, "silent"))
                            group.scroll("silent")
                            for task in group.tasks:
                                cands[-1].tryToPutSingleTask(task, group.groupId, "silent")
                        for i in range(len(group.tasks) * 2):
                            candId += 1
                            cands.append(utptr_classes.Candidate(candId, basicCand.hoursUnused, basicCand, "silent"))
                            random.shuffle(group.tasks)
                            for task in group.tasks:
                                cands[-1].tryToPutSingleTask(task, group.groupId, "silent")
                    elif group.importance == "n":
                        candId += 1
                        cands.append(utptr_classes.Candidate(candId, basicCand.hoursUnused, basicCand, "silent"))
                        group.tasks.sort(key=lambda x: x.taskEstimatesSum, reverse=True)
                        for task in group.tasks:
                            cands[-1].tryToPutSingleTask(task, group.groupId, "silent")
                        for i in range(len(group.tasks) + 1):
                            candId += 1
                            cands.append(utptr_classes.Candidate(candId, basicCand.hoursUnused, basicCand, "silent"))
                            group.scroll("silent")
                        for task in group.tasks:
                            cands[-1].tryToPutSingleTask(task, group.groupId, "silent")
                        for i in range(len(group.tasks) + 1):
                            candId += 1
                            cands.append(utptr_classes.Candidate(candId, basicCand.hoursUnused, basicCand, "silent"))
                            random.shuffle(group.tasks)
                            for task in group.tasks:
                                cands[-1].tryToPutSingleTask(task, group.groupId, "silent")
                    elif group.importance == "l":
                        candId += 1
                        cands.append(utptr_classes.Candidate(candId, basicCand.hoursUnused, basicCand, "silent"))
                        group.tasks.sort(key=lambda x: x.taskEstimatesSum, reverse=True)
                        for task in group.tasks:
                            cands[-1].tryToPutSingleTask(task, group.groupId, "silent")
                        for i in range(len(group.tasks) + 1):
                            candId += 1
                            cands.append(utptr_classes.Candidate(candId, basicCand.hoursUnused, basicCand, "silent"))
                            random.shuffle(group.tasks)
                            for task in group.tasks:
                                cands[-1].tryToPutSingleTask(task, group.groupId, "silent")
                    cleanCandsFromClones()


# Далее нужно прописать порядок работы с НЕпервыми группами. Такие кандидаты должны наследовать задачи из кандидатов, содержащих задачи из предыдущих групп



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
            nextCand = utptr_classes.Candidate(candId, listLabourHoursQuotas, False, "silent")
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
        nextCand = utptr_classes.Candidate(candId, listLabourHoursQuotas, False, "silent")


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
