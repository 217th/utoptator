"""
Код для проверки, есть ли в списке объектов класса хотя бы один элемент с заданным значением атрибута

class Mmm:
    def __init__(self, nnn):
        self.nnn = nnn

n = []
for i in range(10):
    n.append(Mmm(i*2))
    print("Элемент %s, значение %s" % (i, n[i].nnn))

print(any(x.nnn <4 for x in n))

"""

'''
        tasksPrior0Array = [t for t in tasksArray if (t[1] == 0)]
        tasksTotalEstimates = [x + y for x, y in zip(tasksTotalEstimates, t[3])]

        group = next((x for x in taskGroups if x.groupId == basicCand.lastGroupId+1), None)
'''


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




    
    
# ▼▼▼▼▼▼▼▼▼▼▼ Начало функции для заполнения массива задач длиной n ▼▼▼▼▼▼▼▼▼▼▼▼
# ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼

# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
# ▲▲▲▲▲▲▲▲▲ Конец функции для заполнения массива задач длиной n ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲


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
