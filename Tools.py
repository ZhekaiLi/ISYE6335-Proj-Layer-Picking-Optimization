class Tools:
    def xor(x, y):
        return bool((x and not y) or (not x and y))

    def correctPosName(name):
        """
        Correct the name of pallet position by the following rules:
        - If the name is string number that no more than 3 digits
            '1'  --> '801-01-A-01'
            '11' --> '801-11-A-01'
            '111'--> '801-111-A-01'
        - Else no change
        :return: corrected name
        """
        if len(name) == 1: return '801-0' + str(name) + '-A-01'
        elif len(name) <= 3: return '801-' + str(name) + '-A-01'
        else: return name