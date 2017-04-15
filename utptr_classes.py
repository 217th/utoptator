import utptr_rels
import random
import copy
import uuid
import utptr_log as log

class Task:
    # Атрибуты класса Task. Заполняются в конструкторе.
    #   id - uuid задачи, генерируется программой
    #   taskId - номер задачи, получаемый снаружи (int, генерируется случайно), может быть неуникальным
    #   taskPrior - приоритет (int, выбирается случайно из словаря)
    #   taskType - тип (int, выбирается случайно из словаря)
    #   taskEstimates - оценки (list, заполняются случайно только для разработчиков, которые есть в словаре)
    #   taskEstimatesSum - общая сумма трудозатрат по задаче (int)
    #   taskScore - ценность (float, рассчитывается из приоритета и оценок)
    #   primIsMandatory - True, если задачу только в основной состав
    #       (иначе - можно в основной или резервный)
    #   secIsPreferred - True, если задачу нужно стараться в резервный состав
    #       (иначе - по умолчанию ставим в основной)
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
    #   getTaskScore - расчёт score задачи целиком или для отдельной части

    def __init__(self, dictPriors, dictTaskTypes, devsArray, silentMode="silent"):
        import random, copy

        # То, что будет заменено получением реальных данных о задачах:
        # Генерируем правдоподобно выглядищий номер задачи
        self.taskId = int(str(random.randint(0, 9)) +
                          str(random.randint(0, 9)) +
                          str(random.randint(0, 9)) +
                          str(random.randint(0, 9)) +
                          str(random.randint(0, 9)))
        log.task(self.taskId, 'created', '')
        # Выбираем приоритет задачи
        self.taskPrior = random.choice(list(dictPriors.keys()))
        log.task(self.taskId, 'priority is set', self.taskPrior)
        # Выбираем тип задачи
        self.taskType = random.choice(list(dictTaskTypes.keys()))
        log.task(self.taskId, 'type is set', self.taskType)
        # Устанавливаем предпочтения (основной, резерв)
        self.primIsMandatory, self.secIsPreferred = random.choice(15*[[False, False]] +
                                                                  [[True, False]] +
                                                                  [[False, True]])
        self.partialIsPermitted = random.choice(15*[False] + [True])
        log.task(self.taskId, 'primary is mandatory', self.primIsMandatory)
        log.task(self.taskId, 'secondary is preferred', self.secIsPreferred)
        self.relConcurrent = []
        self.relAlternative = []
        self.relSequent = []

        taskEstimates = []

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

        self.id = uuid.uuid1()
        # Всё, что связано с relations, оставляем пока использующим в качестве идентификатора человекопонятный taskId

        # Расчитываем taskScore
        self.taskScore = self.getTaskScore()


    def getTaskScore(self, completeness='completely', isExtraHoursUsed=False):
        priorityFactor = {
            0: 5.0,
            1: 2.0,
            2: 1.0,
            3: 0.7,
            4: 0.4,
            5: 0.2,
            None: 0.4
        }
        completenessFactor = {
            'completely': 1.0,
            'backendOnly': 0.5,
            'htmlcssOnly': 0.5
        }
        extraHoursFactor = {
            True: 0.8,
            False: 1
        }
        if completeness is 'completely':
            sumOfHours = self.taskEstimatesSum
        elif completeness is 'backendOnly':
            sumOfHours = sum([x.hours for x in self.taskEstimates if x.devType == 'backenddev'])
        elif completeness is 'htmlcssOnly':
            sumOfHours = sum([x.hours for x in self.taskEstimates if x.devType == 'htmlcssdev'])
        score = round(priorityFactor[self.taskPrior] *
                      sumOfHours *
                      completenessFactor[completeness] *
                      extraHoursFactor[isExtraHoursUsed],
                      2)
        log.task(self.taskId,
                 'task (completeness = %s, extra hours = %s) score is calculated' % (completeness, isExtraHoursUsed),
                 score)
        return score


    def setRandomRelations(self, tasks, silentMode="silent"):
        # Всё, что связано с relations, оставляем пока использующим в качестве идентификатора человекопонятный taskId
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

        log.task(self.taskId, 'random conс relations are created', [x for x in self.relConcurrent if x is not False])
        log.task(self.taskId, 'random alt relations are created', [x for x in self.relAlternative if x is not False])
        log.task(self.taskId, 'random seq relations are created', [x for x in self.relSequent if x is not False])

        for altTaskId in self.relAlternative:
            altTasks = [x for x in tasks if x.taskId == altTaskId]
            for altTask in altTasks:
                altTask.relAlternative.append(self.taskId)
        log.task(self.taskId, 'random alt relations are syncronized', [x for x in self.relAlternative if x is not False])

        for concTaskId in self.relConcurrent:
            concTasks = [x for x in tasks if x.taskId == concTaskId]
            for concTask in concTasks:
                concTask.relConcurrent.append(self.taskId)
        log.task(self.taskId, 'random conc relations are syncronized', [x for x in self.relConcurrent if x is not False])

        for seqTaskId in self.relSequent:
            seqTasks = [x for x in tasks if x.taskId == seqTaskId]
            for seqTask in seqTasks:
                for seqSeqTaskId in seqTask.relSequent:
                    if seqSeqTaskId == seqTaskId:
                        log.task(self.taskId, 'mutual sequent relations found with taskId...', seqTaskId)
                        seqTask.relSequent = []
                        self.relSequent = []
                        break
        log.task(self.taskId, 'random seq relations are syncronized', [x for x in self.relSequent if x is not False])


class TaskEnrolled:
    """
    Атрибуты класса TaskEnrolled:
        task - экземпляр класса Task
        completeness - одно из текстовых значений:
            'completely'
            'backendOnly'
            'htmlcssOnly'
        dest - одно из текстовых значений:
            'prim'
            'sec'
        score - ценность включения, которая может отличаться от "базовой" ценности задачи за счёт девальвации
    """

    def __init__(self, task, completeness, dest, isExtraHoursUsed=False):
        self.task = task
        self.completeness = completeness
        self.dest = dest
        self.score = task.getTaskScore(completeness, isExtraHoursUsed)


class Candidate:
    # Атрибуты класса Candidate.
    #   candId - уникальный id кандидата (int, генерируется инкрементально)
    #   additionalTo - указываем кандидата, состав которого полностью включает данный кандидат
    #   tasks - список задач, включённых в кандидат (list of Tasks)
    #   tEnrld - список экземпляров класса TaskEnrolled - задач и их кусков, включённых в кандидата
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
            overallTasksList
    ):

        self.isUsed = False
        self.candId = candId
        self.additionalTo = basicCand
        self.lastGroupId = group.groupId
        self.checkSum = ''
        self.tEnrld = list()
        self.tasks = list()
        self.overallGroupIsCompletelyInExceptRelLocks = True

        log.groupAndCand(group.groupId, self.candId, 'candidate is created for group')
        if self.additionalTo:
            log.cand(self.candId, 'candidate is additional to other candidate:', self.additionalTo.candId)
        log.cand(self.candId, 'candidate last group id is:', self.lastGroupId)

        if basicCand == False:
            self.hoursUnused = copy.deepcopy(ifNoBasicCandHoursUnused)
            self.rels = copy.deepcopy(ifNoBasicCandOverallRels)
        else:
            self.hoursUnused = copy.deepcopy(basicCand.hoursUnused)
            self.rels = copy.deepcopy(basicCand.rels)

        log.cand(self.candId, 'candidate\'s initial primary hours:', [x.hoursPrimary for x in self.hoursUnused])
        log.cand(self.candId, 'candidate\'s initial secondary hours:', [x.hoursSecondary for x in self.hoursUnused])
        log.cand(self.candId, 'method set for candidate:', method)

        if group.tasks:
            # Независимо от наличия basicCand, предпринимаем попытки заполнения созданного кандидата newCand
            if method == "direct":
                group.tasks.sort(key=lambda x: x.taskEstimatesSum, reverse=True)
                for task in group.tasks:
                    self.tryToPutSingleTask(task, overallTasksList, group.groupId)
            elif method == "scroll":
                group.scroll("silent")
                for task in group.tasks:
                    self.tryToPutSingleTask(task, overallTasksList, group.groupId)
            elif method == "shuffle":
                random.shuffle(group.tasks)
                for task in group.tasks:
                    self.tryToPutSingleTask(task, overallTasksList, group.groupId)

    def isGroupCompletelyIn(self, group):
        for task in group.tasks:
            if task not in self.tasks:
                log.groupAndCand(group.groupId, self.candId, 'group is NOT completely inside the candidate')
                return False
        log.groupAndCand(group.groupId, self.candId, 'group is completely in the candidate')
        return True

    def refreshChecksum(self):
        import hashlib
        h = hashlib.md5()
        dataList = sorted([x.id.hex for x in self.tasks])
        # Потом в расчёт контрольной суммы нужно будет добавить расширенный статус вхождения задачи
        for element in dataList:
            h.update(element.encode())
        self.checkSum = h.hexdigest()
        return ()

    def acceptTask(self, task):
        self.tasks.append(task)
        self.hoursUnused = [x.substractHours(y) for x, y in zip(self.hoursUnused, task.taskEstimates)]
        self.refreshChecksum()
        log.taskAndCand(task.taskId, self.candId, 'task is accepted to candidate, total tasks inside:',
                        len(self.tasks))

    def getScore(self):
        scorePrim = 0
        scoreSec = 0
        for task in self.tasks:
            scorePrim += task.taskScore
        return (scorePrim, scoreSec)

    def print(self):
        print("------------------------------\n------------------------------\n------------------------------")
        if self.additionalTo:
            print(self.hl("Candidate.print", "g") +
                  "\nСостав-кандидат № %s - всего %s задач - последняя группа %s - добавочный к %s - ценность %s" %
                  (self.candId,
                   len(self.tasks),
                   self.lastGroupId,
                   self.additionalTo.candId,
                   round(self.getScore()[0], 1))
                  )
        else:
            print(self.hl("Candidate.print", "g") +
                  "\nСостав-кандидат № %s - всего %s задач - последняя группа %s - ценность %s" %
                  (self.candId,
                   len(self.tasks),
                   self.lastGroupId,
                   round(self.getScore()[0], 1))
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
        """
        Применяется, если надо проверить вхождение нескольких задач разом.
        То есть либо все разом входят (в основной или резерв), либо НЕ входят.
        Для задач, июмеющих связи relConcurrent, частичная постановка НЕ ПОДДЕРЖИВАЕТСЯ

        Результат выполнения функции воспринимается как однозначная рекомендация по способу постановки задач.
        Собствено постановка задач выполняется за пределами данной функции.
        
        Функция возвращает tuple, у которого:
            первое значение - в отношении какой части задачи/задач применяется результат
            второе значение - куда можно поставить
        
        Возможные первые значения:
            'multipleTasks'
            'singleTask'
            'backendOnly' - !!! пока не поддерживается
            'htmlCssOnly' - !!! пока не поддерживается
            'backendAndHtmlCssOnly' - !!! пока не поддерживается

        Возможные вторые значения:
            False
            'fitToPrim'
            'fitToSec'
            'fitToPrimSec'
            'fitToPrimSecExcess'
        """

        # Считаем суммарные оценки всех задач, которые надо поставить
        overallEstimates = [0] * len(quotaList)
        for task in taskList:
            overallEstimates = [x.hours+y for x, y in zip(task.taskEstimates, overallEstimates)]

        # Сравниваем с квотами:
        #   основного состава,
        #   резерва,
        #   основного состава + резерва,
        #   основного состава + резерва + экстра часов
        areFitToPrim = [x <= y.hoursPrimary
                        for x, y in zip(overallEstimates, quotaList)]
        areFitToSec = [x <= y.hoursSecondary
                        for x, y in zip(overallEstimates, quotaList)]
        areFitToPrimSec = [x <= (y.hoursPrimary+y.hoursSecondary)
                           for x, y in zip(overallEstimates, quotaList)]
        areFitToPrimSecExcess = [x <= (y.hoursPrimary+y.hoursSecondary+y.hoursExcess)
                           for x, y in zip(overallEstimates, quotaList)]

        if True in [task.primIsMandatory for task in taskList]:
            isPrimMandatory = True
        else:
            isPrimMandatory = False

        if True in [task.secIsPreferred for task in taskList]:
            isSecPreferred = True
        else:
            isSecPreferred = False

        if len(taskList) > 1:
            """Обработка случая, когда пытаемся поставить сразу несколько задач"""
            if False in areFitToPrimSecExcess:
                self.overallGroupIsCompletelyInExceptRelLocks = False
                return 'multipleTasks', False
            elif (False not in areFitToPrimSecExcess
                  and False in areFitToPrimSec
                  and not isPrimMandatory):
                return 'multipleTasks', 'fitToPrimSecExcess'
            elif (False not in areFitToPrimSecExcess
                  and False not in areFitToPrimSec
                  and False in areFitToSec
                  and False in areFitToPrim
                  and not isPrimMandatory):
                return 'multipleTasks', 'fitToPrimSec'
            elif (False not in areFitToPrimSecExcess
                  and False not in areFitToPrimSec
                  and False not in areFitToSec
                  and False in areFitToPrim
                  and not isPrimMandatory):
                return 'multipleTasks', 'fitToSec'
            elif (False not in areFitToPrimSecExcess
                  and False not in areFitToPrimSec
                  and False in areFitToSec
                  and False not in areFitToPrim):
                return 'multipleTasks', 'fitToPrim'
            elif (False not in areFitToPrimSecExcess
                  and False not in areFitToPrimSec
                  and False not in areFitToSec
                  and False not in areFitToPrim):
                if not isPrimMandatory and isSecPreferred:
                    return 'multipleTasks', 'fitToSec'
                elif not isPrimMandatory and not isSecPreferred:
                    return 'multipleTasks', 'fitToPrim'
                elif isPrimMandatory:
                    return 'multipleTasks', 'fitToPrim'
            else:
                self.overallGroupIsCompletelyInExceptRelLocks = False
                return 'multipleTasks', False

        elif len(taskList) == 1:
            """Обработка случая, когда пытаемся поставить сразу ТОЛЬКО ОДНУ задачу"""
            if False in areFitToPrimSecExcess:
                self.overallGroupIsCompletelyInExceptRelLocks = False
                return 'singleTask', False
            elif (False not in areFitToPrimSecExcess
                  and False in areFitToPrimSec
                  and not isPrimMandatory):
                return 'singleTask', 'fitToPrimSecExcess'
            elif (False not in areFitToPrimSecExcess
                  and False not in areFitToPrimSec
                  and False in areFitToSec
                  and False in areFitToPrim
                  and not isPrimMandatory):
                return 'singleTask', 'fitToPrimSec'
            elif (False not in areFitToPrimSecExcess
                  and False not in areFitToPrimSec
                  and False not in areFitToSec
                  and False in areFitToPrim
                  and not isPrimMandatory):
                return 'singleTask', 'fitToSec'
            elif (False not in areFitToPrimSecExcess
                  and False not in areFitToPrimSec
                  and False in areFitToSec
                  and False not in areFitToPrim):
                return 'singleTask', 'fitToPrim'
            elif (False not in areFitToPrimSecExcess
                  and False not in areFitToPrimSec
                  and False not in areFitToSec
                  and False not in areFitToPrim):
                if not isPrimMandatory and isSecPreferred:
                    return 'singleTask', 'fitToSec'
                elif not isPrimMandatory and not isSecPreferred:
                    return 'singleTask', 'fitToPrim'
                elif isPrimMandatory:
                    return 'singleTask', 'fitToPrim'
            else:
                self.overallGroupIsCompletelyInExceptRelLocks = False
                return 'singleTask', False

        # Если False в areFitToPrimSecExcess - не влезает никак
        # Если нет False в areFitToPrimSecExcess, но есть в areFitToPrimSec -
        #       влезает в сумму основного и резерва и экстра (в таком случае ставим в резерв, добавляя экстра
        #       и перераспределяя часы)
        # Если нет False в areFitToPrimSec, но есть в areFitToPrim И есть в areFitToSec -
        #       влезает в сумму основного и резерва (в таком случае ставим в резерв, перераспределяя часы)
        # Если нет False в areFitToPrim -
        #       влезает в основной состав (туда и ставим)
        # Если нет False в areFitToSec -
        #       влезает в резервный состав (туда и ставим)
        # Помимо влезаемости, нужно анализировать условия:
        #       primIsMandatory
        #       secIsPreferred
        # Если среди одновременных задач есть primIsMandatory, рассматривается ТОЛЬКО постановка в основной состав
        # Если среди одновременных задач есть secIsPreferred, приоритетно рассматривается постановка в резерв
        # Если среди одновременных задач есть и primIsMandatory, и secIsPreferred, рассматривается только постановка
        #       в основной состав


    def tryToPutSingleTask(self, task, allTasks, groupId):
        """
            * Создаём список задач, которые будут разом ставиться в кандидата
            * Добавляем в список задачу, для которой вызвали функцию
            * Проверяем наличие связей для данной задачи
                * Если связей нет, сразу trialIsFreeOfLocks = True
                * Если связи есть:
                    * Если есть активные связи типов "альтернатива", "последовательность", либо "уже взято", тогда:
                        * trialIsFreeOfLocks = False
                    * Если есть активные связи типа "одновременно", тогда:
                        * добавляем в список задач, которые будем пытаться ставить, все одновременные задачи. По taskId
                        * trialIsFreeOfLocks = True
            * Если блокировка по связям отсутствует, проверяем, влезает ли список отобранных задач в основной состав:
                self.areTasksFit(self.hoursUnused, tasksToPut)
            * Если влезает:
                * Для каждой задачи из списка:
                    * вызываем self.acceptTask(task1)
                    * изменяем статусы связей для всех связей кандидата, где текущая задача является ассоциированной:
                        * если связь - "последовательно", связь деактивируем (т.е. она в будущем уже 
                            не будет учитываться при постановке задач)
                        * если связь - "альтернатива", связь активируем
                        * если связь - "одновременно", связь деактивируем И создаём активную связь типа "уже взято"
        """
        # allTasks нужен только чтобы отработать связь relConcurrent
        # !!! Что-то придумать, чтобы не тащить !!!

        log.taskAndCand(task.taskId, self.candId, 'trying to put task to candidate with hours...',
                        [x.hours for x in task.taskEstimates])
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

        if len(tasksToPut)>1:
            log.taskAndCand(task.taskId, self.candId, 'trying to put task together with concurrents:',
                            [x.taskId for x in tasksToPut])
        elif len(tasksToPut) == 1:
            log.taskAndCand(task.taskId, self.candId, 'no concurrences for task')

        if not trialIsFreeOfLocks:
            log.taskAndCand(task.taskId, self.candId, 'task is retired because of blocks, relations type...',
                            [x.relType for x in taskActiveRelsArray])
            log.taskAndCand(task.taskId, self.candId, 'task is retired because of blocks, tasks...',
                            [x.assocTaskId for x in taskActiveRelsArray])
            # return "notEnrolledBecauseOfLocks"
        else:
            # Проверяем, влезает ли список задач
            # Если в tasksToPut БОЛЕЕ ОДНОЙ задачи,
            #   ЧАСТИЧНАЯ постановка задач НЕ ПОДДЕРЖИВАЕТСЯ

            multiplicity, areFit = self.areTasksFit(self.hoursUnused, tasksToPut)
            if not areFit:
                log.taskAndCand(task.taskId, self.candId, 'task (and its concurrents) are not fit',
                                [x.taskId for x in tasksToPut])
                # return "notEnrolledBecauseOfHours"
            else:
                log.taskAndCand(task.taskId, self.candId, 'task (and its concurrents) are fit',
                                [x.taskId for x in tasksToPut])

                for task1 in tasksToPut:
                    self.acceptTask(task1, areFit)

                    for rel in self.rels:
                        if rel.assocTaskId is task1.taskId:
                            if rel.relType == "relSequent":
                                rel.isActive = False
                            elif rel.relType == "relAlternative":
                                rel.isActive = True
                            elif rel.relType == "relConcurrent":
                                rel.isActive = False
                                self.rels.append(
                                    utptr_rels.Relation("relAlreadyTaken",
                                                        task1.taskId,
                                                        "",
                                                        False)
                                )













            log.cand(self.candId, 'primary hours remaining:', [x.hoursPrimary for x in self.hoursUnused])
            log.cand(self.candId, 'secondary hours remaining:', [x.hoursSecondary for x in self.hoursUnused])
            log.cand(self.candId, 'extra hours remaining:', [x.hoursExcess for x in self.hoursUnused])
            # return "sucessfullyEnrolled"


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
        self.importance = tImportance
        self.tasks = []
        log.group(self.groupId, 'empty group with meta is created', self.meta)

    def fillAndSort(self, tasksArray, silentMode="silent"):
        log.group(self.groupId, 'getting group filled', '')
        for task in tasksArray:
            for taskType in self.meta[0]:
                for taskPrior in self.meta[1]:
                    if (taskType == task.taskType) and (taskPrior == task.taskPrior):
                        self.tasks.append(task)
                        log.taskAndGroup(task.taskId, self.groupId, 'group has smallowed up the task', '')
        if self.tasks:
            self.tasks.sort(key=lambda x: x.taskEstimatesSum, reverse = True)
        else:
            if silentMode is not "silent":
                log.group(self.groupId, 'group remains empty', '')

    def scroll(self, silentMode="silent"):
        if silentMode is not "silent":
            print(self.hl("Group.scroll", "g") + "Группа %s. Задачу %s переносим в конец." % (self.groupId, self.tasks[0].taskId))
        firstTask = [self.tasks[0]]
        restTasks = self.tasks[1:]
        self.tasks.clear()
        self.tasks = restTasks + firstTask
        log.taskAndGroup(firstTask[0].taskId, self.groupId, 'group is scrolled, first task was...')


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