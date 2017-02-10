'''
def GetCandidate(tasksArray, hourQuotas, ruleSet = "simple", silentMode = True):
    if ruleSet == "simple":     # Простейший вариант последовательного включения
        tasksPrior0Array = [t for t in tasksArray if (t[1] == 0)]
        tasksPrior1Array = [t for t in tasksArray if (t[1] == 1)]
        tasksPrior2Array = [t for t in tasksArray if (t[1] == 2)]
        tasksPrior3Array = [t for t in tasksArray if (t[1] == 3)]
        tasksPrior4Array = [t for t in tasksArray if (t[1] == 4)]
        tasksPrior5Array = [t for t in tasksArray if (t[1] == 5)]
        print ("------------------------------")
        print ("Приоритет 0:\n", tasksPrior0Array)
        print ("Приоритет 1:\n", tasksPrior1Array)
        print ("Приоритет 2:\n", tasksPrior2Array)
        print ("Приоритет 3:\n", tasksPrior3Array)
        print ("Приоритет 4:\n", tasksPrior4Array)
        print ("Приоритет 5:\n", tasksPrior5Array)
        print ("------------------------------")        

        if len(tasksPrior0Array) > 0:
            tasksTotalEstimates = [0] * (max(hourQuotas)+1)
            for t in tasksPrior0Array:
                tasksTotalEstimates = [x + y for x, y in zip(tasksTotalEstimates, t[3])]
                tasksPrior0AreFit = [x <= y for x, y in zip(tasksTotalEstimates, hourQuotas)]

            if not silentMode:
                print("Приоритет 0. Сумма оценок и влезаемость:", tasksTotalEstimates, tasksPrior0AreFit)
            if False in tasksPrior0AreFit:
                print ("Приоритет 0 не влезает")
            else:
                print ("Приоритет 0 влезает")
        else:
            print("Нет задач с приоритетом 0.")    
    return ([]) '''

    
    
''' 
# ▼▼▼▼▼▼▼▼▼▼▼ Начало функции для заполнения массива задач длиной n ▼▼▼▼▼▼▼▼▼▼▼▼
# ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼

    import random
  
    for i in range(n):
        # Формат строки массива: id задачи, id типа задачи, id приоритета, лист с оценками, ценность задачи для дальнейшего расчёта ценности листа

        taskId = int(str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))) # Сгенерили правдоподобно выглядищий номер задачи
        taskPrior = random.choice(list(dictPriors.keys())) # Выбрали приоритет задачи
        taskType = random.choice(list(dictTaskTypes.keys())) # Выбрали тип задачи

        taskEstimates = [] # Генерируем оценки по задаче для каждого разработчика _только из справочника_. Так, чтобы id записи с оценкой в массиве третьего уровня соответствовал id разработчика из справочника
        for j in range(0, 1+max(list(dictDevs.keys()))):
            if j in dictDevs: # Проверяем, есть ли значение j среди ключей справочника разработчиков; если есть, то присваиваем рандомную оценку (с очень большим весом нуля)
                taskEstimates.append(random.choice([0]*9 + list(range(1,11))))
            else: # Если в справочнике нет разработчика с таким ID
                taskEstimates.append(0)

        taskScore = GetTaskScore(taskPrior, taskEstimates)

        if silentMode is not "silent":
            print("-----\nЗадача: %s Тип: %s Приоритет: %s Ценность: %s" % (taskId, taskType, taskPrior, taskScore))
            print("Часы по задаче: %s " % taskEstimates)

        tasksArray.append([taskId, taskPrior, taskType, taskEstimates, taskScore])
    if silentMode is not "silent": print("------------------------------\nВсе задачи в массиве:\n", tasksArray)
    return (tasksArray)

# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
# ▲▲▲▲▲▲▲▲▲ Конец функции для заполнения массива задач длиной n ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
'''


''' Кусок про заполнение кандидата ДО перехода на классы Task и Candidate.
if silentMode is not "silent": print("------------------------------")

candidates = []                 # Список списков задач, для каждого д.б. указаны суммарный score, % утилизации разработчиков (для начала - только в сумме, потом - по каждому разработчику индивидуально) 
hoursUnused = copy.deepcopy(listLabourHoursQuotas)

for groupMeta in tasksGroupsMeta:
    print("-----\nМетаданные группы (тип задачи, приоритет):", groupMeta)
    tasksGroup = []
    for task in originalTasksArray:
        for taskType in groupMeta[0]:
            for taskPrior in groupMeta[1]:
                if (taskType == task.taskType) and (taskPrior == task.taskPrior):
                    tasksGroup.append(task)
                    task.append(sum(task[3]))   # Добавляем в запись задачи сумму трудозатрат (5-м полем)

    if tasksGroup:
        candidatesFromGroup = []
        print("Группа:", tasksGroup)
        
        tasksGroup.sort(key=lambda x: x[5], reverse = True) # Сортируем группу по убыванию затрат
        
        candidatesAreEnough = False
        while not candidatesAreEnough:
            singleCandidate = []        # Состав-кандидат, включающий пока только задачи из взятой группы, описываемой groupMeta, посчитанный единственным способом

            for task in tasksGroup:
                taskIsFit = [x <= y for x, y in zip(task[3], hoursUnused)]
                if False in taskIsFit:
                    print("Есть часов: %s, надо часов: %s" % (hoursUnused, task[3]))
                    print("Задача %s не влезает" % task)
                else:
                    print("Есть часов: %s, надо часов: %s." % (hoursUnused, task[3]))
                    print("Задача %s влезает" % task)
                    singleCandidate.append(task)
                    hoursUnused = [y - x for x, y in zip(task[3], hoursUnused)]
                    print("Остаётся часов:", hoursUnused)

            if ((len(singleCandidate)>0) and (len(singleCandidate) == len(tasksGroup))):
                print("Группа вошла целиком")
                candidatesFromGroup.append(singleCandidate)
            elif ((len(singleCandidate)>0) and (len(singleCandidate) != len(tasksGroup))):
                print("Группа не вошла целиком, вошло только:", singleCandidate)
                candidatesFromGroup.append(singleCandidate)
            elif (len(singleCandidate) == 0):
                print("Из группы не вошло ничего.")

            candidatesAreEnough = True
        
        
        candidates.append(candidatesFromGroup)
    else:
        print("Группа пуста") '''
		
		
'''


macroScen = []
macroScenarios = []

for i in range(len(taskGroups)+1):
	
	print(i, end=" ")

'''

'''
		
for scenH in scenarios:
    for scenN in scenarios:
        for scenL in scenarios:
            if ((taskGroups[scenH.targetGroupId].importance == "h")
			and (taskGroups[scenN.targetGroupId].importance == "n")
			and (taskGroups[scenL.targetGroupId].importance == "l")):
				print("Макросценарий: 1) гр %s - сцен %s %s 2) гр %s - сцен %s %s 3) гр %s - сцен %s %s" % (scenH.targetGroupId, scenH.scenType, scenH.taskI, scenN.targetGroupId, scenN.scenType, scenN.taskI, scenL.targetGroupId, scenL.scenType, scenL.taskI))
				macroScenarios.append([scenH, scenN, scenL])

print("------------------------------\nВсего сценариев: %s, макросценариев: %s\n------------------------------" % (len(scenarios), len(macroScenarios)))
'''
'''
i = 0
candidates = []
for macroScen in macroScenarios:
    bufferCand = utptr_classes.Candidate(i, listLabourHoursQuotas, "bubble")
    bufferCand.execMacroScen(macroScen, "bubble")
''' 
'''    


    for scen in macroScen:
        bufferCand = scen.execute(hoursUnused, "bubble")
        hoursUnused = bufferCand.hoursUnused
        


    bufferCand.candId = i
    candidates.append(bufferCand)
    i += 1

for cand in candidates:
    print("Кандидат: ", cand.candId)
    for task in cand.tasks:
        print(task.taskId)'''