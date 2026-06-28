class Solution(object):
    def arrayChange(self, nums, operations):

        pos = {}

        for i in range(len(nums)):
            pos[nums[i]] = i

        for old, new in operations:
            idx = pos[old]
            nums[idx] = new
            pos[new] = idx
            del pos[old]

        return nums