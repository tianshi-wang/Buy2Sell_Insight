def numSquares(n):
    """
    :type n: int
    :rtype: int
    """

    def helper(countSoFar, intSet):
        if not intSet:
            return countSoFar

        squareList = []
        for i in range(1, max(intSet)):
            if i ** 2 <= max(intSet):
                squareList.append(i ** 2)
            else:
                break
        childSet = set()
        for num in set(intSet):
            if num in squareList:
                return helper(countSoFar + 1, None)
            else:
                for square in squareList:
                    if num > square:
                        childSet.add(num-square)
        return helper(countSoFar + 1, childSet)

    return helper(0, set([n]))

print(numSquares(7))