import csv

def writeTasks(taskList):
    with open('tasks.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter = ";")
        writer.writerow(["groupId",
                         "groupImportance",
                         "taskId",
                         "taskPrior",
                         "taskType",
                         "taskEstimates",
                         "taskScore",
                         "relConcurrent",
                         "relAlternative",
                         "relSequent"])
        writer.writerows(taskList)
    return()

def writeCands(candsList):
    with open('cands.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter = ";")
        writer.writerow(["candId",
                         "numberOfTasks",
                         "score",
                         "hoursUnused",
                         "checkSum",
                         "taskId",
                         "taskPrior",
                         "taskType",
                         "taskEstimates",
                         "taskScore",
                         "relConcurrent",
                         "relAlternative",
                         "relSequent"])
        writer.writerows(candsList)
    return()







"""
    with open('eggs.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
        spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])
"""
