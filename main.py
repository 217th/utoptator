# https://www.tutorialspoint.com/python/

from filloriginaldata import (createDictDevs, createDictPriors, createDictTaskTypes, createArrayLabourQuotas)
import utptr_log as log
import copy
import random
import utptr_classes
import utptr_from_file
import utptr_to_file
import utptr_rels
import datetime

print("----- (%s) Начало программы -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
log.general('program launched')

silentMode = "babble"  # Режим тишины. "silent" - сокращённые сообщения. "babble" - полные сообщения
dictTaskTypes = createDictTaskTypes()
dictPriors = createDictPriors()
# dictDevs = createDictDevs(silentMode)
# listLabourHoursQuotas = createArrayLabourQuotas(list(dictDevs.keys()), silentMode)

print("----- (%s) Импортируем разработчиков -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
initialDevsArray = utptr_from_file.readDevs(4, 28)
for dev in initialDevsArray:
    print(dev.devId, dev.devName, dev.devType, dev.hoursPrimary, dev.hoursSecondary, dev.hoursExcess)


def сreateTasksArray(n):
    tasksArray = []
    if n > 0:
        for i in range(n):
            task = utptr_classes.Task(dictPriors, dictTaskTypes, initialDevsArray)
            tasksArray.append(task)
        for task in tasksArray:
            task.setRandomRelations(tasksArray)
    else:
        print('Попросили слишком мало задач. Массив задач не заполнен.')
    return tasksArray


print("----- (%s) Создаём задачи -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
originalTasksArray = сreateTasksArray(100)
log.general('list of %s tasks is created' % len(originalTasksArray))


def createTaskGroups(taskList, mode="prod"):
    log.general('start creating blank groups')
    if mode == 'test':
        metaList = [
            [[2], [0], "h"],
            [[2], [1], "h"],
            [[2], [2], "n"],
            [[3, 1], [5], "l"]
        ]
    elif mode == 'prod':
        # Немедл., оч. выс., выс. - сначала ошибки, потом разработка
        # Высокенький - ошибки и разработка в одной группе
        # Нормальный - ошибки и разработка в одной группе
        # Низкий - ошибки и разрбаботка в одной группе
        metaList = [
            [[2], [0], "h"],
            [[2], [1], "h"],
            [[2], [2], "h"],
            [[2], [3], "n"],
            [[2], [4], "n"],
            [[2], [5], "l"],
            [[3], [0], "h"],
            [[1], [0], "h"],
            [[3], [1], "h"],
            [[1], [1], "h"],
            [[3], [2], "h"],
            [[1], [2], "h"],
            [[3, 1], [3], "n"],
            [[3, 1], [4], "n"],
            [[3, 1], [5], "l"]
        ]
    groupList = list()
    for i1, meta in enumerate(metaList):
        groupList.append(utptr_classes.Group(i1, meta[0], meta[1], meta[2]))
    log.general('start distributing tasks to groups')
    print("----- (%s) Распределяем задачи по группам -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
    for gr in groupList:
        gr.fillAndSort(taskList)
    return groupList

taskGroups = createTaskGroups(originalTasksArray, 'prod')


def createOverallRelationsArray():
    # Временная функция для заполнения массива связей тестовыми данными
    # Всё, что связано с relations, оставляем пока использующим в качестве идентификатора человекопонятный taskId
    relsNeatArray = []
    for group in taskGroups:
        for task in group.tasks:
            if task.relAlternative:
                for assocTaskId in task.relAlternative:
                    relsNeatArray.append(utptr_rels.Relation("relAlternative", task.taskId, group.groupId, assocTaskId))
            if task.relConcurrent:
                for assocTaskId in task.relConcurrent:
                    relsNeatArray.append(utptr_rels.Relation("relConcurrent", task.taskId, group.groupId, assocTaskId))
            if task.relSequent:
                for assocTaskId in task.relSequent:
                    relsNeatArray.append(utptr_rels.Relation("relSequent", task.taskId, group.groupId, assocTaskId))

    relsNeatArray = utptr_rels.cleanRelsFromClones(relsNeatArray)
    relsNeatArray = utptr_rels.completeConcurrentRelations(relsNeatArray)
    relsNeatArray = utptr_rels.completeSequentRelations(relsNeatArray)

    return relsNeatArray


# Всё, что связано с relations, оставляем пока использующим в качестве идентификатора человекопонятный taskId
print("----- (%s) Заполняем связи между задачами -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
originalRelsArray = createOverallRelationsArray()
print("----- (%s) Валидируем связи между задачами -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
originalRelsConflictArray = utptr_rels.validateRels([x.taskId for x in originalTasksArray], originalRelsArray)
# Всё, что связано с relations, оставляем пока использующим в качестве идентификатора человекопонятный taskId


if originalRelsConflictArray:
    for relConflict in originalRelsConflictArray:
        relConflict.print()

else:
    print("Валидация пройдена. Связи между задачами - бесконлфиктные.")
    log.general('no conflict in relations')
    del originalRelsConflictArray

    if any(len(x.tasks) > 0 for x in taskGroups):
        candId = -1
        cands = []
        forFileRawCandMetaArray = list()
        forFileRawCandTasksArray = list()


        def cleanCandsFromClones(cands):
            for cand in reversed(cands):
                if cands.index(cand) > 0:
                    for candPrev in cands[0: cands.index(cand)]:
                        if cand.checkSum == candPrev.checkSum and\
                                (cand.lastGroupId == candPrev.lastGroupId) and\
                                (cand.additionalTo == candPrev.additionalTo):
                            log.cand(cand.candId, 'deleting candidate because it\'s equal to...', candPrev.candId)
                            for i, j in enumerate(forFileRawCandMetaArray):
                                if j[1] == cand.candId:
                                    forFileRawCandMetaArray[i].append("del")
                            cands.pop(cands.index(cand))
                            break
            return cands


        def isCandUnique(candList, candNew):
            if candList:
                for candExisted in reversed(candList):
                    if candExisted.checkSum == candNew.checkSum\
                            and candExisted.lastGroupId == candNew.lastGroupId\
                            and candExisted.additionalTo == candNew.additionalTo:
                        log.cand(candNew.candId,
                                 'candidate is declined from final list because it is a clone of another cand',
                                 candExisted.candId)
                        return False
            return True


        def fillSingleCand(group, basicCand, method):
            # Создание кандидата - входы:
            #   - целочисленный идентификатор для нового кандидата
            #   - объект класса Group (включая и задачи, отнесённые к группе)
            #   - объект класса Candidate, являющийся "базовым" для нового
            #   - метод заполнения кандидата
            #   - квоты часов разработки (если отсутствует базовый кандидат)
            #   - массив с данными о связях задач (если отсутствует базовый кандидат)
            #   - массив со всеми задачами (применяется при обработке связей)
            # Создание кандидата - выходы:
            #   - новый объект класса Candidate
            #   - forFileRawCandTasks - список задач в кандидате для экспорта в файл
            #   - forFileCandMeta - метаданные кандидата для экспорта в файл

            global candId
            candId += 1

            # Создаём объект newCand, который потом добавим в массив cands
            # Вся логика по наполнению кандидата задачами - в Candidate.__init__
            newCand = utptr_classes.Candidate(
                candId,
                group,
                basicCand,
                method,
                initialDevsArray,
                originalRelsArray,
                originalTasksArray
            )

            # Заполняем мета-информацию о сырых кандидатах для вывода в файл
            if newCand.additionalTo:
                forFileAddTo = 'addTo '+str(newCand.additionalTo.candId)
            else:
                forFileAddTo = False
            forFileCandMeta = list([
                forFileAddTo,
                newCand.candId,
                newCand.lastGroupId,
                newCand.checkSum,
                'amnt '+str(len(newCand.tEnrld)),
                [x.hoursPrimary for x in newCand.hoursUnused],
                [x.hoursSecondary for x in newCand.hoursUnused],
                [x.hoursExcess for x in newCand.hoursUnused],
                method])
            if not isCandUnique(cands, newCand):
                forFileCandMeta.append('del')

            # Заполняем мета-информацию о задачах, вошедших в сырой кандидат, для вывода в файл
            forFileRawCandTasks = list()
            for taskEnrolled in newCand.tEnrld:
                forFileRawCandTasks.append([
                    newCand.candId,
                    newCand.lastGroupId,
                    taskEnrolled.dest,
                    taskEnrolled.task.taskId,
                    taskEnrolled.task.taskPrior,
                    taskEnrolled.task.taskType,
                    [x.hours for x in taskEnrolled.task.taskEstimates],
                    round(taskEnrolled.task.taskScore, 1),
                    taskEnrolled.task.relConcurrent,
                    taskEnrolled.task.relAlternative,
                    taskEnrolled.task.relSequent
                ])

            if isCandUnique(cands, newCand):
                cands.append(newCand)

            global forFileRawCandTasksArray
            forFileRawCandTasksArray.extend(forFileRawCandTasks)
            global forFileRawCandMetaArray
            forFileRawCandMetaArray.append(forFileCandMeta)

            return ()


        def fillCandsWithTasksFromSpecificGroupAndOnSpecificBasicCand(group, basicCand):
            global cands
            if group.importance == "h":
                fillSingleCand(group, basicCand, "direct")
                completelyIn = cands[-1].isGroupCompletelyIn(group)
                if not completelyIn:
                    for i in range(len(group.tasks) + 1): fillSingleCand(group, basicCand, "scroll")
                    for i in range(len(group.tasks) * 2): fillSingleCand(group, basicCand, "shuffle")
            elif group.importance == "n":
                fillSingleCand(group, basicCand, "direct")
                completelyIn = cands[-1].isGroupCompletelyIn(group)
                if not completelyIn:
                    for i in range(len(group.tasks) + 1): fillSingleCand(group, basicCand, "scroll")
                    for i in range(len(group.tasks) + 1): fillSingleCand(group, basicCand, "shuffle")
            elif group.importance == "l":
                fillSingleCand(group, basicCand, "direct")
                completelyIn = cands[-1].isGroupCompletelyIn(group)
                if not completelyIn:
                    for i in range(len(group.tasks) + 1): fillSingleCand(group, basicCand, "shuffle")


        for i, group in enumerate(taskGroups):
            log.group(group.groupId, 'start creating candidates for group', '')
            print("----- (%s) Формируем кандидатов для группы %s -----" % (
                datetime.datetime.now().strftime("%H:%M:%S.%f"),
                group.groupId)
                  )
            if i is 0:
                fillCandsWithTasksFromSpecificGroupAndOnSpecificBasicCand(group, False)
                # cands = cleanCandsFromClones(cands)
            else:
                for basicCand in cands:
                    if (basicCand.lastGroupId + 1 == group.groupId) and (not basicCand.isUsed):
                        fillCandsWithTasksFromSpecificGroupAndOnSpecificBasicCand(group, basicCand)
                        basicCand.isUsed = True
                        # cands = cleanCandsFromClones(cands)

        # ▼▼▼▼▼▼▼ Склейка в один проход, удаление всех кандидатов, заканчивающихся непоследней группой,▼▼▼▼▼▼▼
        candsAssembled = copy.deepcopy(cands)
        print("----- (%s) Склеиваем кандидатов -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
        log.general('start gluing the candidates last to first')
        for i in range(len(taskGroups)):
            for cand in reversed(candsAssembled):
                log.cand(cand.candId, 'start gluing the candidate. pass...', i)
                if cand.additionalTo:
                    # Приклеиваем к более позднему всё из более раннего
                    # hoursUnused остаётся от позднего
                    # lastGroupId остаётся от позднего
                    cand.tEnrld.extend(cand.additionalTo.tEnrld)
                    cand.additionalTo = cand.additionalTo.additionalTo
                    cand.refreshChecksum()

        candsAssembled.sort(key=lambda x: x.lastGroupId, reverse=True)
        for cand in reversed(candsAssembled):
            if cand.lastGroupId < taskGroups[-1].groupId:
                candsAssembled.pop(candsAssembled.index(cand))
                log.cand(cand.candId, 'deleting candidate glued to the major. last group is...', cand.lastGroupId)

        candsAssembled = cleanCandsFromClones(candsAssembled)
        # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

        print("----- (%s) После склейки: -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
        for cand in candsAssembled:
            log.cand(cand.candId, 'candidate still alive after the gluing and cleaning clones')
            cand.print()

        # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ Заполнение всего необходимого для экспорта в excel ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼

        log.general('start preparing data for export to excel')
        print("----- (%s) Готовим данные для вывода в файл -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
        # Заполнение исходного списка задач для экспорта в файл
        forFileTasksList = []
        for group in taskGroups:
            for task in group.tasks:
                forFileTasksList.append([
                    group.groupId,
                    group.importance,
                    task.taskId,
                    task.taskPrior,
                    task.taskType,
                    [x.hours for x in task.taskEstimates],
                    round(task.taskScore, 1),
                    task.primIsMandatory,
                    task.secIsPreferred,
                    task.relConcurrent,
                    task.relAlternative,
                    task.relSequent
                ])

        # Заполнение массива межзадачных связей для экспорта в файл
        forFileRelsList = []
        for rel in originalRelsArray:
            forFileRelsList.append([
                rel.relType,
                rel.subjTaskId,
                rel.subjTaskGroupId,
                rel.assocTaskId
            ])

        # Заполнение списка настроек попытки для экспорта в файл
        forFileTrySettings = list()
        forFileTrySettings.append(initialDevsArray)

        forFileRawCandOnlyActiveArray = list()
        for record in forFileRawCandMetaArray:
            if 'del' in record:
                pass
            else:
                if record[0] == False:
                    record[0] = ""
                forFileRawCandOnlyActiveArray.append(record)

        # Заполнение массива с мета-информацией по финальным склеенным кандидатам для экспорта в файл
        forFileFinalCandMetaArray = []
        for cand in candsAssembled:
            forFileFinalCandMetaArray.append([
                cand.candId,
                len(cand.tasks),
                cand.getScore(),
                [x.hoursPrimary for x in cand.hoursUnused],
                [x.hoursSecondary for x in cand.hoursUnused],
                [x.hoursExcess for x in cand.hoursUnused],
                cand.checkSum])

        # Заполнение массива с подробной информацией о задачах, вошедших в финальные кандидаты, для экспорта в файл
        forFileFinalCandsTasksList = []
        for cand in candsAssembled:
            forFileSingleFinalCandTasksList = []
            for taskEnrolled in cand.tEnrld:
                forFileSingleFinalCandTasksList.append([
                    cand.candId,
                    len(cand.tEnrld),
                    cand.getScore(),
                    [x.hoursPrimary for x in cand.hoursUnused],
                    [x.hoursSecondary for x in cand.hoursUnused],
                    [x.hoursExcess for x in cand.hoursUnused],
                    cand.checkSum,
                    taskEnrolled.dest,
                    taskEnrolled.task.taskId,
                    taskEnrolled.task.taskPrior,
                    taskEnrolled.task.taskType,
                    [task.hours for task in taskEnrolled.task.taskEstimates],
                    taskEnrolled.task.taskScore,
                    taskEnrolled.score,
                    taskEnrolled.task.relConcurrent,
                    taskEnrolled.task.relAlternative,
                    taskEnrolled.task.relSequent
                    ])
            forFileFinalCandsTasksList.append(forFileSingleFinalCandTasksList)

        forFileFinalCandsRelsList = []
        for cand in candsAssembled:
            for rel in cand.rels:
                forFileFinalCandsRelsList.append([
                    cand.candId,
                    rel.relType,
                    rel.subjTaskId,
                    rel.assocTaskId,
                    rel.isActive
                ])

    # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

        # Экспорт в excel
        log.general('start exporting to excel')
        print("----- (%s) Выводим в файл -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
        utptr_to_file.writeReportToXLS(
            forFileTrySettings,
            forFileTasksList,
            forFileRelsList,
            forFileRawCandMetaArray,
            forFileRawCandOnlyActiveArray,
            forFileRawCandTasksArray,
            forFileFinalCandMetaArray,
            forFileFinalCandsTasksList,
            forFileFinalCandsRelsList
        )
        print("----- (%s) Экспорт завершён -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))

    else:
        print("Все группы задач пусты.")

    log.general('program finished')
