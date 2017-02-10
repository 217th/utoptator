class Task:

# Атрибуты класса Task. Заполняются в конструкторе.
#   taskId - номер задачи (int, генерируется случайно)
#   taskPrior - приоритет (int, выбирается случайно из словаря)
#   taskType - тип (int, выбирается случайно из словаря)
#   taskEstimates - оценки (list, заполняются случайно только для разработчиков, которые есть в словаре)
#   taskEstimatesSum - общая сумма трудозатрат по задаче (int)
#   taskScore - ценность (float, рассчитывается из приоритета и оценок)
#   candsTaskIncluded - список id состав-кандидатов, куда задача вошла (list)
#   candsTaskExcluded - список id состав-кандидатов, куда задача НЕ вошла (list)
#
# Методы класса Task.
#   acceptToCand - включить задачу в состав-кандидат
#   declineFromCand - пометить задачу как не включённую в состав-кандидат

    def hl(self, funcName, color = "g"):
        silentMode = False
        if not silentMode:
            if color == "g":
                return("\x1b[0;36;42m" + "(" + funcName + "):" + "\x1b[0m" + " ")
            if color == "r":
                return("\x1b[0;36;41m" + "(" + funcName + "):" + "\x1b[0m" + " ")
            if color == "y":
                return("\x1b[0;36;43m" + "(" + funcName + "):" + "\x1b[0m" + " ")
            if color == "b":
                return("\x1b[0;36;44m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        else: return("")

    def __init__(self, dictPriors, dictTaskTypes, dictDevs, silentMode = "silent"):
        import random, copy

        self.taskId = int(str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))) # Сгенерили правдоподобно выглядищий номер задачи
        self.taskPrior = random.choice(list(dictPriors.keys())) # Выбрали приоритет задачи
        self.taskType = random.choice(list(dictTaskTypes.keys())) # Выбрали тип задачи
        
        taskEstimates = [] # Генерируем оценки по задаче для каждого разработчика _только из справочника_. Так, чтобы id записи с оценкой соответствовал id разработчика из справочника
        for j in range(0, 1+max(list(dictDevs.keys()))):
            if j in dictDevs: # Проверяем, есть ли значение j среди ключей справочника разработчиков; если есть, то присваиваем рандомную оценку (с очень большим весом нуля)
                taskEstimates.append(random.choice([0]*9 + list(range(1,11)) + list(range(1, 11))))
            else: # Если в справочнике нет разработчика с таким ID
                taskEstimates.append(0)
        self.taskEstimates = copy.deepcopy(taskEstimates)
        del taskEstimates
        
        self.taskEstimatesSum = sum(self.taskEstimates)
        
        if self.taskPrior == 0:          # Немедленный
            self.taskScore = round(5.0 * sum(self.taskEstimates), 2)
        elif self.taskPrior == 1:        # Очень высокий
            self.taskScore = round(2.0 * sum(self.taskEstimates), 2)     
        elif self.taskPrior == 2:        # Высокий
            self.taskScore = round(1.0 * sum(self.taskEstimates), 2)
        elif self.taskPrior == 3:        # Высокенький
            self.taskScore = round(0.7 * sum(self.taskEstimates), 2)
        elif self.taskPrior == 4:        # Нормальный
            self.taskScore = round(0.4 * sum(self.taskEstimates), 2)
        elif self.taskPrior == 5:        # Низкий
            self.taskScore = round(0.2 * sum(self.taskEstimates), 2)
        else:
            self.taskScore = round(0.4 * sum(self.taskEstimates), 2)

        if silentMode is not "silent":
            print("-----\n" + self.hl("Task.__init__", "g") + "Задача: %s Тип: %s Приоритет: %s Ценность: %s" % (self.taskId, self.taskType, self.taskPrior, self.taskScore))
            print(self.hl("Task.__init__", "g") + "Часы по задаче: %s " % self.taskEstimates)
            
        self.candsTaskIncluded = []
        self.candsTaskExcluded = []
            
    def acceptToCand(self, candId, silentMode = "silent"):
        self.candsTaskIncluded.append(candId)
        if silentMode is not "silent":
            print(self.hl("Task.acceptToCand", "g") + "Задача %s включена в состав-кандидат %s" % (self.taskId, candId))
    
    def declineFromCand(self, candId, silentMode = "silent"):
        self.candsTaskExcluded.append(candId)
        if silentMode is not "silent":
            print(self.hl("Task.declineFromCand", "g") + "Задача %s помечена как НЕ включённая в состав-кандидат %s" % (self.taskId, candId))
            
            
class Candidate:
# Атрибуты класса Candidate.
#   candId - уникальный id кандидата (int, генерируется инкрементально)
#   tasks - список задач, включённых в кандидат (list of Tasks)
#   hoursUnused - количество нераспределённых часов (list)
#   diagnosisForGroup - словарь: {groupId : diagnosis}, возможные диагнозы:
#       - "noTasksInGroup"
#       - "completelyIn"
#       - "completelyOut"
#       - "partiallyIn"
#
# Методы класса Candidate.
#   acceptTask - включить задачу в состав-кандидат
#   getScore - получить суммарную ценность состав-кандидата
#   printCandidate - напечатать список вошедших задач
#	execScenario - заполнить кандидата с помощью набора сценариев

    def hl(self, funcName, color = "g"):
        silentMode = False
        if not silentMode:
            if color == "g":
                return("\x1b[0;36;42m" + "(" + funcName + "):" + "\x1b[0m" + " ")
            if color == "r":
                return("\x1b[0;36;41m" + "(" + funcName + "):" + "\x1b[0m" + " ")
            if color == "y":
                return("\x1b[0;36;43m" + "(" + funcName + "):" + "\x1b[0m" + " ")
            if color == "b":
                return("\x1b[0;36;44m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        else: return("")

    def __init__(self, candId, hoursUnused, silentMode = "silent"):
        self.candId = candId
        self.hoursUnused = hoursUnused
        self.tasks = []
        if silentMode is not "silent":
            print(self.hl("Candidate.__init__", "g") + "----- Создан состав-кандидат №", self.candId)
            print(self.hl("Candidate.__init__", "g") + "Начальное количество часов:", self.hoursUnused)
        self.diagnosisForGroup = {}
            
    def acceptTask(self, task, silentMode = "silent"):
        self.tasks.append(task)
        if silentMode is not "silent":
            print(self.hl("Candidate.acceptTask", "g") + "-----\nВ состав-кандидат %s включена задача %s. Всего включено задач %s" %  (self.candId, self.tasks[len(self.tasks)-1].taskId, len(self.tasks)))
    
    def getScore(self):
        score = 0
        for task in self.tasks:
            score += task.taskScore
        return (score)
        
    def printCandidate(self):
        print("------------------------------\n------------------------------\n------------------------------\n" + self.hl("Candidate.printCandidate", "g") + "\nСостав-кандидат № %s - всего %s задач - ценность %s" % (self.candId, len(self.tasks), round(self.getScore(), 1)))
        for task in self.tasks:
            print("Задача %s - тип %s - приоритет %s - оценки %s" % (task.taskId, task.taskType, task.taskPrior, task.taskEstimates))
        print("Осталось часов: %s" % (self.hoursUnused))
     
        
        
'''        

        bufferCand = Candidate(-99, hoursUnused, "silent")

        def tryToPutTask(task):
            taskIsFit = [x <= y for x, y in zip(task.taskEstimates, bufferCand.hoursUnused)]
            if False in taskIsFit:
                if silentMode is not "silent":
                    print(self.hl("Scenario.execute", "g") + "--- Задача %s. Есть часов: %s, надо часов: %s" % (task.taskId, bufferCand.hoursUnused, task.taskEstimates))
                    print(self.hl("Scenario.execute", "g") + "Задача %s не влезает" % task.taskId)
            else:
                if silentMode is not "silent":
                    print(self.hl("Scenario.execute", "g") + "--- Задача %s. Есть часов: %s, надо часов: %s." % (task.taskId, bufferCand.hoursUnused, task.taskEstimates))
                    print(self.hl("Scenario.execute", "g") + "Задача %s влезает" % task.taskId)
                bufferCand.tasks.append(task)
                bufferCand.hoursUnused = [y - x for x, y in zip(task.taskEstimates, bufferCand.hoursUnused)]
                if silentMode is not "silent":
                    print(self.hl("Scenario.execute", "g") + "Остаётся часов:", bufferCand.hoursUnused)

        if self.scenType == "direct":
            if self.group.tasks:
                for task in self.group.tasks:
                    tryToPutTask(task)

        elif self.scenType == "minus1":
            if silentMode is not "silent": 
                print(self.hl("Group.execScenario", "g") + "Minus1")
            
        elif self.scenType == "minus1+shuffle":
            if silentMode is not "silent": 
                print(self.hl("Group.execScenario", "g") + "Minus1+shuffle")

        elif self.scenType == "shuffle":
            if silentMode is not "silent": 
                print(self.hl("Group.execScenario", "g") + "Shuffle")
        
        pass'''

class Group:
# Атрибуты класса Group:
#   id - идентификатор группы (int)
#   meta - метаданные группы (тип, приоритет) (list)
#   importance - важность группы, влияет на то, насколько активно пытаемся утоптать группу. Возможные значения:
#       - "h" - высокая важность
#       - "n" - средняя важность
#       - "l" - низкая важность
#   tasks - список задач, отнесённых к группе (list of Tasks)
#
# Методы класса Group:
#   __init__ - в качестве каждого атрибута нужно передавать list
#   fillAndSort - из переданного массива выбираем задачи с совпадающими метаданными


    def hl(self, funcName, color = "g"):
        silentMode = False
        if not silentMode:
            if color == "g":
                return("\x1b[0;36;42m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        if color == "r":
            return("\x1b[0;36;41m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        if color == "y":
            return("\x1b[0;36;43m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        if color == "b":
            return("\x1b[0;36;44m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        else: return("")
    
    def __init__ (self, groupId, tType, tPrior, tImportance = "n", silentMode = "silent"):
        self.groupId = groupId
        self.meta = []
        self.meta.append(tType)
        self.meta.append(tPrior)
        if silentMode is not "silent":
            print(self.hl("Group.__init__", "g") + "Создана группа id %s - %s" % (self.groupId, self.meta))
        self.importance = tImportance
        self.tasks = []
    
    def fillAndSort(self, tasksArray, silentMode = "silent"):
        if silentMode is not "silent":
            print(self.hl("Group.fillAndSort", "g") + "Метаданные группы (тип задачи, приоритет): %s" % (self.meta))
        for task in tasksArray:
            for taskType in self.meta[0]:
                for taskPrior in self.meta[1]:
                    if (taskType == task.taskType) and (taskPrior == task.taskPrior):
                        self.tasks.append(task)
        if self.tasks:
            self.tasks.sort(key=lambda x: x.taskEstimatesSum, reverse = True)
            for task in self.tasks:
                if silentMode is not "silent":
                    print(self.hl("Group.fillAndSort", "g") + "Задача №: %s. Суммарная оценка: %s" % (task.taskId, task.taskEstimatesSum))
        else:
            if silentMode is not "silent":
                print(self.hl("Group.fillAndSort", "g") + "Группа пуста")

class Scenario:
# Атрибуты класса Scenario:
#	targetGroupId - id группы задач (int), к которой применим сценарий
#   type - тип сценария:
#       "direct"
#       "minusN"
#       "shuffle"
#   taskI - для типа "minusN" - индекс задачи, исключаемой из группы
#
#
#
# Методы класса Scenario:
#   execute - выполнение сценария

    def hl(self, funcName, color = "g"):
        silentMode = False
        if not silentMode:
            if color == "g":
                return("\x1b[0;36;42m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        if color == "r":
            return("\x1b[0;36;41m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        if color == "y":
            return("\x1b[0;36;43m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        if color == "b":
            return("\x1b[0;36;44m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        else: return("")

    def __init__(self, targetGroupId, scenType, silentMode = "silent", *taskI):
        self.targetGroupId = targetGroupId
        self.scenType = scenType
        if taskI:
            self.taskI = taskI
        if silentMode is not "silent":
            print(self.hl("Scenario.__init__", "g") + "Для группы %s - новый сценарий %s" % (self.targetGroupId, self.scenType))
'''            
    def execute(self, hoursUnused, silentMode = "silent"):
        if silentMode is not "silent":
            print("------------------------------\n" + self.hl("Scenario.execute", "g") + "Запуск сценария на группе %s - тип %s" % (self.group.meta, self.scenType))

        bufferCand = Candidate(-99, hoursUnused, "silent")

        def tryToPutTask(task):
            taskIsFit = [x <= y for x, y in zip(task.taskEstimates, bufferCand.hoursUnused)]
            if False in taskIsFit:
                if silentMode is not "silent":
                    print(self.hl("Scenario.execute", "g") + "--- Задача %s. Есть часов: %s, надо часов: %s" % (task.taskId, bufferCand.hoursUnused, task.taskEstimates))
                    print(self.hl("Scenario.execute", "g") + "Задача %s не влезает" % task.taskId)
            else:
                if silentMode is not "silent":
                    print(self.hl("Scenario.execute", "g") + "--- Задача %s. Есть часов: %s, надо часов: %s." % (task.taskId, bufferCand.hoursUnused, task.taskEstimates))
                    print(self.hl("Scenario.execute", "g") + "Задача %s влезает" % task.taskId)
                bufferCand.tasks.append(task)
                bufferCand.hoursUnused = [y - x for x, y in zip(task.taskEstimates, bufferCand.hoursUnused)]
                if silentMode is not "silent":
                    print(self.hl("Scenario.execute", "g") + "Остаётся часов:", bufferCand.hoursUnused)

        if self.scenType == "direct":
            if self.group.tasks:
                for task in self.group.tasks:
                    tryToPutTask(task)

        elif self.scenType == "minus1":
            if silentMode is not "silent": 
                print(self.hl("Group.execScenario", "g") + "Minus1")
            
        elif self.scenType == "minus1+shuffle":
            if silentMode is not "silent": 
                print(self.hl("Group.execScenario", "g") + "Minus1+shuffle")

        elif self.scenType == "shuffle":
            if silentMode is not "silent": 
                print(self.hl("Group.execScenario", "g") + "Shuffle")

        return(bufferCand)
'''
