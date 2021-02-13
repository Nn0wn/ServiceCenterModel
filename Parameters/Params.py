class Parameters:

    def __init__(self, parList):
        self.__params = parList

    def combinations(self, indexes=None):
        chosenParams = [param for index, param in enumerate(self.__params) if not indexes or index in indexes]
        paramNames = ['param' + str(index) for index, param in enumerate(chosenParams)]
        if len(chosenParams) > 0:
            return eval('[[' + ', '.join(paramNames) + '] ' + ' '.join(
                ['for ' + param + ' in chosenParams[' + str(index) + ']' for index, param in
                 enumerate(paramNames)]) + ']', {'chosenParams': chosenParams})
        else:
            return []
