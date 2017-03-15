import utptr_rels
import random
import utptr_log as log

class Task:
    # Атрибуты класса Task. Заполняются в конструкторе.
    #   taskId - номер задачи (int, генерируется случайно)
    #   taskPrior - приоритет (int, выбирается случайно из словаря)
    #   taskType - тип (int, выбирается случайно из словаря)
    #   taskEstimates - оценки (list, заполняются случайно только для разработчиков, которые есть в словаре)
    #   taskEstimatesSum - общая сумма трудозатрат по задаче (int)
    #   taskScore - ценность (float, рассчитывается из приоритета и оценок)
    #
    #   relConcurrent - список задач, с которыми эта должна выполняться только одновременно
    #       (одинаковый для всех одновременных задач)
    #   relSequent - список задач, текущая может войти только после всех задач, включённых в список.
    #       Если в список включена задача, имеющая другие одновременные,
    #       то предшественниками становятся все задачи группы одновременных
    #   relAlternative - список взаимоисключающих задач.
    #       Если пара задач указана одновременно как альтернативная и последовательная, то альтернатива имеет приоритет
    #
    # Методы класса Task.
    #   setRandomRelations - метод (вероятно, временный) для заполнения relConcurrent, relSequent, relAlternative

    @staticmethod
    def hl(funcName, color="g"):
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

    def __init__(self, dictPriors, dictTaskTypes, devsArray, silentMode="silent"):
        import random, copy

        self.taskId = int(str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))) # Сгенерили правдоподобно выглядищий номер задачи
        log.task(self.taskId, 'created', '')
        self.taskPrior = random.choice(list(dictPriors.keys())) # Выбрали приоритет задачи
        log.task(self.taskId, 'priority is set', self.taskPrior)
        self.taskType = random.choice(list(dictTaskTypes.keys())) # Выбрали тип задачи
        log.task(self.taskId, 'type is set', self.taskType)

        self.relConcurrent = []
        self.relAlternative = []
        self.relSequent = []

        taskEstimates = []

        '''
        # Генерируем оценки по задаче для каждого разработчика _только из справочника_.
        # Так, чтобы id записи с оценкой соответствовал id разработчика из справочника
        for j in range(0, 1+max(list(dictDevs.keys()))):
            if j in dictDevs:
                # Проверяем, есть ли значение j среди ключей справочника разработчиков;
                # если есть, то присваиваем рандомную оценку (с очень большим весом нуля)
                taskEstimates.append(random.choice([0]*9 + list(range(1,11)) + list(range(1, 11))))
            else: # Если в справочнике нет разработчика с таким ID
                taskEstimates.append(0)
        self.taskEstimates = copy.deepcopy(taskEstimates)
        del taskEstimates

        self.taskEstimatesSum = sum(self.taskEstimates)
        '''

        # Генерируем оценки по задаче "по-новому"
        for dev in devsArray:
            hours = random.choice([0]*39 + list(range(1,11)) + list(range(1, 11)))
            taskEstimates.append(Estimate(dev.devId,
                                          dev.devType,
                                          hours)
                                 )
            log.taskAndDev(self.taskId, dev.devId, 'dev hours are assigned to task as the estimate', hours)

        self.taskEstimates = copy.deepcopy(taskEstimates)
        self.taskEstimatesSum = sum([x.hours for x in taskEstimates])
        del taskEstimates

        if self.taskPrior == 0:          # Немедленный
            self.taskScore = round(5.0 * self.taskEstimatesSum, 2)
        elif self.taskPrior == 1:        # Очень высокий
            self.taskScore = round(2.0 * self.taskEstimatesSum, 2)
        elif self.taskPrior == 2:        # Высокий
            self.taskScore = round(1.0 * self.taskEstimatesSum, 2)
        elif self.taskPrior == 3:        # Высокенький
            self.taskScore = round(0.7 * self.taskEstimatesSum, 2)
        elif self.taskPrior == 4:        # Нормальный
            self.taskScore = round(0.4 * self.taskEstimatesSum, 2)
        elif self.taskPrior == 5:        # Низкий
            self.taskScore = round(0.2 * self.taskEstimatesSum, 2)
        else:
            self.taskScore = round(0.4 * self.taskEstimatesSum, 2)
        log.task(self.taskId, 'task score is calculated', self.taskScore)

'''
        if silentMode is not "silent":
            print("-----\n" + self.hl("Task.__init__", "g") + "Задача: %s Тип: %s Приоритет: %s Ценность: %s" %
                  (self.taskId, self.taskType, self.taskPrior, self.taskScore))
            print(self.hl("Task.__init__", "g") + "Часы по задаче: %s " % [x.hours for x in self.taskEstimates])
'''

    def setRandomRelations(self, tasks, silentMode="silent"):
        import random

        r = random.randint(0, 10)
        if r in range(0, 7):
            self.relConcurrent.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
        elif r in range(8, 9):
            self.relConcurrent.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
            self.relConcurrent.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
        elif r == 10:
            self.relConcurrent.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
            self.relConcurrent.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
            self.relConcurrent.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))

        r = random.randint(0, 10)
        if r in range(0, 7):
            self.relAlternative.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
        elif r in range(8, 9):
            self.relAlternative.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
            self.relAlternative.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
        elif r == 10:
            self.relAlternative.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
            self.relAlternative.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
            self.relAlternative.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))

        r = random.randint(0, 10)
        if r in range(0, 7):
            self.relSequent.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
        elif r in range(8, 9):
            self.relSequent.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
            self.relSequent.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
        elif r == 10:
            self.relSequent.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
            self.relSequent.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))
            self.relSequent.append(random.choice([x.taskId for x in tasks if x.taskId != self.taskId] + len(tasks)*5*[False]))

        if silentMode is not "silent":
            print(self.hl("Task.setRandomRelations", "g") + "taskId %s ... start deleting falses" % self.taskId)
        self.relConcurrent = [x for x in self.relConcurrent if x is not False]
        self.relAlternative = [x for x in self.relAlternative if x is not False]
        self.relSequent = [x for x in self.relSequent if x is not False]

        if silentMode is not "silent":
            print(self.hl("Task.setRandomRelations", "g") + "taskId %s ... start searching unsyncronized alternatives" % self.taskId)
        for altTaskId in self.relAlternative:
            altTasks = [x for x in tasks if x.taskId == altTaskId]
            for altTask in altTasks:
                altTask.relAlternative.append(self.taskId)

        if silentMode is not "silent":
            print(self.hl("Task.setRandomRelations", "g") + "taskId %s ... start searching unsyncronized concurrences" % self.taskId)
        for concTaskId in self.relConcurrent:
            concTasks = [x for x in tasks if x.taskId == concTaskId]
            for concTask in concTasks:
                concTask.relConcurrent.append(self.taskId)

        if silentMode is not "silent":
            print(self.hl("Task.setRandomRelations", "g") + "taskId %s ... start searching unsyncronized sequences" % self.taskId)
        for seqTaskId in self.relSequent:
            seqTasks = [x for x in tasks if x.taskId == seqTaskId]
            for seqTask in seqTasks:
                for seqSeqTaskId in seqTask.relSequent:
                    if seqSeqTaskId == seqTaskId:
                        if silentMode is not "silent":
                            print(self.hl("Task.setRandomRelations", "g") + "setRandomRelations relSequent self %s seqTask %s" % (self.taskId, seqTask.taskId))
                        seqTask.relSequent = []
                        self.relSequent = []
                        break


class Candidate:
    # Атрибуты класса Candidate.
    #   candId - уникальный id кандидата (int, генерируется инкрементально)
    #   additionalTo - указываем кандидата, состав которого полностью включает данный кандидат
    #   tasks - список задач, включённых в кандидат (list of Tasks)
    #   hoursUnused - list of Quota
    #   lastGroupId - идентификатор последней группы, из которой ПЫТАЛИСЬ включить задачи (могли и не включить)
    #   checkSum - контрольная сумма кандидата
    #   isUsed - статус того, что для данного кандидата созданы все дополнительные (дочерние) кандидаты
    #   rels - list - массив объектов класса Relation.
    #       Должен копироваться при создании последующего кандидата из предыдущего кандидата,
    #       включая все сделанные ранее пометки.
    #
    # Методы класса Candidate.
    #   acceptTask - включить задачу в состав-кандидат
    #   getScore - получить суммарную ценность состав-кандидата
    #   print - напечатать список вошедших задач
    #   tryToPutSingleTask - попытаться включить одну задачу
    #   isGroupCompletelyIn - вернуть True, если группа целиком вошла в кандидата; иначе False

    @staticmethod
    def hl(funcName, color="g"):
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

    def __init__(
            self,
            candId,
            group,
            basicCand,
            method,
            ifNoBasicCandHoursUnused,
            ifNoBasicCandOverallRels,
            overallTasksList,
            silentMode = "silent"
    ):

        self.isUsed = False
        self.candId = candId
        self.additionalTo = basicCand
        self.lastGroupId = group.groupId
        self.checkSum = 0
        self.tasks = list()

        if basicCand == False:
            self.hoursUnused = ifNoBasicCandHoursUnused
            self.rels = ifNoBasicCandOverallRels
        else:
            self.hoursUnused = basicCand.hoursUnused
            self.rels = basicCand.rels

        if group.tasks:
            # Независимо от наличия basicCand, предпринимаем попытки заполнения созданного кандидата newCand
            if method == "direct":
                group.tasks.sort(key=lambda x: x.taskEstimatesSum, reverse=True)
                for task in group.tasks:
                    self.tryToPutSingleTask(task, overallTasksList, group.groupId, silentMode)
            elif method == "scroll":
                group.scroll("silent")
                for task in group.tasks:
                    self.tryToPutSingleTask(task, overallTasksList, group.groupId, silentMode)
            elif method == "shuffle":
                random.shuffle(group.tasks)
                for task in group.tasks:
                    self.tryToPutSingleTask(task, overallTasksList, group.groupId, silentMode)

        if silentMode is not "silent":
            print(self.hl("Candidate.__init__", "g") + "----- Создан состав-кандидат №", self.candId)
            print(self.hl("Candidate.__init__", "g") + "Начальное количество часов:",
                  [x.hoursPrimary for x in self.hoursUnused]
                  )

    def isGroupCompletelyIn(self, group):
        if len(group.tasks) > len(self.tasks):
            return False
        else:
            return True

    def acceptTask(self, task, silentMode = "silent"):
        self.tasks.append(task)
        self.hoursUnused = [x.substractHours(y) for x, y in zip(self.hoursUnused, task.taskEstimates)]
        self.checkSum += task.taskId
        self.checkSum += task.taskScore
        if silentMode is not "silent":
            print(self.hl("Candidate.acceptTask", "g") +
                  "В состав-кандидат %s включена задача %s. Всего включено задач %s" %
                  (self.candId, self.tasks[len(self.tasks)-1].taskId, len(self.tasks))
                  )

    def getScore(self):
        score = 0
        for task in self.tasks:
            score += task.taskScore
        return score

    def print(self):
        print("------------------------------\n------------------------------\n------------------------------")
        if self.additionalTo:
            print(self.hl("Candidate.print", "g") +
                  "\nСостав-кандидат № %s - всего %s задач - последняя группа %s - добавочный к %s - ценность %s" %
                  (self.candId,
                   len(self.tasks),
                   self.lastGroupId,
                   self.additionalTo.candId,
                   round(self.getScore(), 1))
                  )
        else:
            print(self.hl("Candidate.print", "g") +
                  "\nСостав-кандидат № %s - всего %s задач - последняя группа %s - ценность %s" %
                  (self.candId,
                   len(self.tasks),
                   self.lastGroupId,
                   round(self.getScore(), 1))
                  )

        for task in self.tasks:
            print("Задача %s - тип %s - приоритет %s - оценки %s" %
                  (task.taskId,
                   task.taskType,
                   task.taskPrior,
                   [x.hours for x in task.taskEstimates]
                   )
                  )

        print("Осталось часов: %s" % [x.hoursPrimary for x in self.hoursUnused])

    @staticmethod
    def areTasksFit(quotaList, taskList):
        # Возвращает True, если все задачи влезают
        # Пока делаем только постановку в основной состав всей кучи переданных задач
        overallEstimates = [0] * len(quotaList)
        for task in taskList:
            overallEstimates = [x.hours+y for x, y in zip(task.taskEstimates, overallEstimates)]
        areFit = [x <= y.hoursPrimary for x, y in zip(overallEstimates, quotaList)]
        if False in areFit:
            return False
        else:
            return True

    def tryToPutSingleTask(self, task, allTasks, groupId, silentMode = "silent"):
        # allTasks нужен только чтобы отработать связь relConcurrent
        # !!! Что-то придумать, чтобы не тащить !!!

        self.lastGroupId = groupId

        tasksToPut = list()
        tasksToPut.append(task)

        taskActiveRelsArray = [x for x in self.rels if x.isActive and task.taskId == x.subjTaskId]
        if not taskActiveRelsArray:
            trialIsFreeOfLocks = True
        else:
            if "relAlternative" in [x.relType for x in taskActiveRelsArray] or\
                    "relSequent" in [x.relType for x in taskActiveRelsArray] or \
                    "relAlreadyTaken" in [x.relType for x in taskActiveRelsArray]:
                trialIsFreeOfLocks = False
            elif "relConcurrent" in [x.relType for x in taskActiveRelsArray]:
                # Формируем список задач, которые будут пытаться установиться совместно
                tasksToPut.extend([x for x in allTasks if x.taskId in [y.assocTaskId for y in taskActiveRelsArray]])
                trialIsFreeOfLocks = True

        # Проверяем, влезает ли список задач
        tasksAreFit = self.areTasksFit(self.hoursUnused, tasksToPut)

        if not trialIsFreeOfLocks:
            if silentMode is not "silent":
                print(self.hl("Candidate.tryToPutSingleTask", "r") +
                      "Задача %s не рассматривается из-за блокировок %s %s" %
                      (task.taskId,
                       [x.relType for x in taskActiveRelsArray],
                       [x.assocTaskId for x in taskActiveRelsArray]))
        else:
            if not tasksAreFit:
                if silentMode is not "silent":
                    print(self.hl("Candidate.tryToPutSingleTask", "y") +
                          "--- Задача %s. Есть часов: %s. Не влезает" %
                          ([x.taskId for x in tasksToPut],
                           [x.hoursPrimary for x in self.hoursUnused])
                          )
            else:
                if silentMode is not "silent":
                    print(self.hl("Candidate.tryToPutSingleTask", "y") +
                          "--- Задача %s. Есть часов: %s. Влезает" %
                          ([x.taskId for x in tasksToPut],
                           [x.hoursPrimary for x in self.hoursUnused])
                          )

                for task1 in tasksToPut:
                    self.acceptTask(task1, silentMode)

                    for rel in self.rels:
                        if rel.assocTaskId is task1.taskId:
                            if rel.relType == "relSequent":
                                rel.isActive = False
                            elif rel.relType == "relAlternative":
                                rel.isActive = True
                            elif rel.relType == "relConcurrent":
                                rel.isActive = False
                                self.rels.append(utptr_rels.Relation("relAlreadyTaken", task1.taskId, "", False, silentMode))

                if silentMode is not "silent":
                    print(self.hl("Candidate.tryToPutSingleTask", "y") +
                          "Остаётся часов:",
                          [x.hoursPrimary for x in self.hoursUnused])


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
    #   scroll - делаем 0-ю задачу последней

    @staticmethod
    def hl(funcName, color="g"):
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
        else:
            return ""

    def __init__(self, groupId, tType, tPrior, tImportance="n", silentMode="silent"):
        self.groupId = groupId
        self.meta = []
        self.meta.append(tType)
        self.meta.append(tPrior)
        if silentMode is not "silent":
            print(self.hl("Group.__init__", "g") + "Создана группа id %s - %s" % (self.groupId, self.meta))
        self.importance = tImportance
        self.tasks = []

    def fillAndSort(self, tasksArray, silentMode="silent"):
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

    def scroll(self, silentMode="silent"):
        if silentMode is not "silent":
            print(self.hl("Group.scroll", "g") + "Группа %s. Задачу %s переносим в конец." % (self.groupId, self.tasks[0].taskId))
        firstTask = [self.tasks[0]]
        restTasks = self.tasks[1:]
        self.tasks.clear()
        self.tasks = restTasks + firstTask


class Estimate:
    # Класс Estimate
    # Для каждой задачи будет list of Estimate.
    # Если какая-то оценка нулевая, то для неё объект в листе не создаём.
    # Атрибуты:
    #   - devId
    #   - devType
    #   - hours

    def __init__(self, devId, devType, hours):
        self.devId = devId
        self.devType = devType
        self.hours = hours


class Quota(Estimate):

    @staticmethod
    def hl(funcName, color="g"):
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
        else:
            return ""

    def __init__(self, devId, devType, devName, hoursPrimary, hoursSecondary, hoursExcess):
        super().__init__(devId, devType, False)
        self.devName = devName
        self.hoursPrimary = hoursPrimary
        self.hoursSecondary = hoursSecondary
        self.hoursExcess = hoursExcess

    def substractHours(self, estimate):
        # Пока только из основного состава (hoursPrimary)
        if self.devId is estimate.devId:
            self.hoursPrimary -= estimate.hours
            return self
        else:
            print(self.hl("Quota.substractHours", "r") + "Несоответствие devId. Квоты: %s Оценки: %s" %
                  (self.devId,
                   estimate.devId)
                  )
            return False